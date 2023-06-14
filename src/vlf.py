import concurrent.futures

import argparse
import itertools

import os
from pathlib import Path

# My modules
from acquire import *
from plots import *
from tools import *

# URLs for VLF radio noise
EVENTS_URL = 'http://abelian.org/vlf/events.php?stream=vlf'
RECORDINGS_URL = 'http://abelian.org/vsa/vlf'
LIVE_URL = 'http://abelian.org/vlf/'
STREAMS_URL = 'http://5.9.106.210/vlf'

# The directory which will work with
captures = os.path.join('audio', 'vlf', 'hosts')
results = os.path.join('out', 'vlf')


def parallel_download(duration, plot):
    # Create the base directory for the recordings
    os.makedirs(captures, exist_ok=True)

    # Get all hosts
    hosts = vlf_get_live_hosts(LIVE_URL, STREAMS_URL)

    # Download audio clips from all URLs in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for host in hosts:
            audio_file = os.path.join(captures, f'{host}.wav')
            executor.submit(vlf_live, STREAMS_URL + host, duration, audio_file)

    # Get minimum duration
    min_duration = get_min_duration(captures)

    # Trim all files to minimum duration
    trim_files_to_min_duration(captures, min_duration)

    # When plotting is enabled
    if plot:
        # Plot the spectrogram and distribution for each recording
        for host in hosts:
            # Set the path to the audio file
            audio_file = os.path.join(captures, f'{host}.wav')
            description = f'VLF Host {host} - Live Stream'

            # skip if file does not exist
            if not os.path.isfile(audio_file):
                continue

            # Set the base directory for the recordings plots
            base = os.path.join(results, 'hosts', host)
            os.makedirs(base, exist_ok=True)

            # Plot the spectrogram and distribution
            img = os.path.join(base, f'spec.png')
            plot_spectrogram(audio_file, img, description + ' Spectrum')
            img = os.path.join(base, f'dist.png')
            plot_distribution(audio_file, img, description + ' Distribution')


def single_barbu(hosts, plot, test_type):
    ...


def barbu(hosts, plot, test_type, nr):
    # Set the base directory for the uniformized recordings
    base_unif = os.path.join(os.path.join(
        'audio', 'vlf'), barbu.__name__, 'uniformized')
    os.makedirs(base_unif, exist_ok=True)

    # # Uniformize the distributions
    # for host in hosts:
    #     src = os.path.join(captures, f'{host}.wav')
    #     dst = os.path.join(base_unif, f'{host}.wav')
    #     quantile_transformation(src, dst)

    #     # When plotting is enabled
    #     if plot:
    #         # TODO description
    #         plots = os.path.join(results, barbu.__name__, 'uniformized', host)
    #         os.makedirs(plots, exist_ok=True)

    #         plot_waves([dst, src], os.path.join(
    #             plots, 'wave.png'))
    #         plot_distribution(dst, os.path.join(plots, 'dist.png'),
    #                           f'Uniformized distribution of host {host}')
    #         plot_spectrogram(dst, os.path.join(plots, 'spec.png'),
    #                          f'Spectogram after uniformizing distribution of host {host}')

    base_xor = os.path.join(os.path.join(
        'audio', 'vlf'), barbu.__name__, 'xored')
    os.makedirs(base_xor, exist_ok=True)

    for tuple in list(itertools.combinations(hosts, nr)):
        name = '-'.join(tuple)
        dst = os.path.join(base_xor, name + '.wav')

        fst = AudioSegment.from_wav(os.path.join(base_unif, f'{tuple[0]}.wav'))

        # fill fst with zeros
        fst = AudioSegment.silent(duration=len(fst), frame_rate=fst.frame_rate)
        fst.export(dst, format="wav")

        for host in tuple:
            xor_zip(dst, os.path.join(base_unif, f'{host}.wav'), dst)

        # When plotting is enabled
        if plot:
            # TODO description
            plots = os.path.join(results, barbu.__name__, 'xored', name)
            os.makedirs(plots, exist_ok=True)

            plot_distribution(dst, os.path.join(plots, 'dist.png'),
                              f'Distribution of xor between {name} uniformized')
            plot_spectrogram(dst, os.path.join(plots, 'spec.png'),
                             f'Spectogram of xor between {name} uniformized')


def scramble(hosts, plot, test_type):
    ...


def classic():
    ...


def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(description='VLF Radio Noise based TRNG.')
    parser.add_argument('--download', dest='download', action='store_true',
                        help='download the VLF radio noise')
    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='download the VLF radio noise')
    parser.add_argument('--test', dest='test_type', action='store',
                        choices=['fips', 'nist', 'all'], type=str,
                        help='a method of choose for processing the VLF radio noise')
    parser.add_argument('--duration', dest='duration', action='store',
                        default=5, type=int,  # 5 seconds default
                        help='download the VLF radio noise')
    parser.add_argument('--nr', dest='number', action='store',
                        default=2, type=int,
                        help='method-specific fine tuning parameter')

    # Add the method as a command line argument
    methods = list(map(lambda f: f.__name__, [
        single_barbu, barbu, scramble, classic])) + ['all']
    parser.add_argument('--method', dest='method', action='store',
                        choices=methods, type=str,
                        help='a method of choose for processing the VLF radio noise')

    # Parse command line arguments
    args = parser.parse_args()

    # Double the duration if needed
    if args.method is single_barbu.__name__:
        args.duration *= 2

    # Verify if there is a need to download
    if (args.download):
        parallel_download(args.duration, args.plot)

    # List all files in the download directory
    files = os.listdir(captures)

    # Extract the names of the WAV files
    hosts = [Path(file).stem for file in files if file.endswith('.wav')]
    # Sort the hosts
    hosts.sort()

    match args.method:
        case single_barbu.__name__ | 'all':
            single_barbu(hosts, args.plot, args.test_type)
        case barbu.__name__ | 'all':
            barbu(hosts, args.plot, args.test_type, args.number)
        case classic.__name__ | 'all':
            barbu(hosts, args.plot, args.test_type)
        case _:
            print('No method selected, exiting...')


if __name__ == '__main__':
    main()
