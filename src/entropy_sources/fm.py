from entropy_sources.source import source

from subprocess import run, Popen, PIPE

import os

DEFAULT_FREQUENCYS = ['103.8M']


class fm_source(source):
    def __init__(self, freqs=DEFAULT_FREQUENCYS, sample_rate='32k', **kwargs):
        super().__init__(**kwargs)

        self.freqs = freqs
        self.sample_rate = sample_rate

    def acquire(self, duration):
        super().acquire(duration)

        for freq in self.freqs:
            fm_source.fm_record(freq, duration)
        
        self.trim()

    def fm_record(self, freq, duration):
        # Set up the rtl_fm command to demodulate Wideband FM with a 60 ppm error
        rtl_fm_cmd = ['rtl_fm', '-M', 'wbfm', '-f', freq, '-p', '60']

        # Allow for different sample rates
        if self.sample_rate != '32k':
            rtl_fm_cmd += ['-r', self.sample_rate]

        # Run the command and pipe the output to a file
        radio = Popen(rtl_fm_cmd, stdout=PIPE)

        # Create the base directory for the acquisitions
        audio_file = os.path.join(self.source_dir, f'{freq}.wav')

        # Set up the rtl_fm command to match the sampling rate with the resampling
        # rate of the radio output and to use a single channel
        # Also trim the time
        sox_cmd = ['sox', '-t', 'raw', '-r', self.sample_rate, '-es', '-b', '16', '-c',
                   '1', '-V0', '-', audio_file, 'trim', '0', duration]

        # Run the command and set the input to the last pipe
        record = run(sox_cmd, stdin=radio.stdout)

        # Allow the radio process to be terminated when the sox process is done
        radio.stdout.close()
        radio.wait()

        # Check for errors
        if radio.returncode != 0 or record.returncode != 0:
            print(f"Radio exit code: {radio.stderr.decode('utf-8')}")
            print(f"Recording exit code: {record.stderr.decode('utf-8')}")
        else:
            print("Successful recording!")
