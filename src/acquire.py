import os
from subprocess import Popen, PIPE, DEVNULL, run

import re
import requests
from bs4 import BeautifulSoup

def vlf_last_event(captures, host_nr, events_url, recordings_url):
    # Send a GET request
    response = requests.get(events_url + str(host_nr))

    # Check that the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'lxml')

        # Convert the parsed HTML to a string
        html_string = str(soup)

        # Find the first occurrence of the pattern
        match = re.search('id=(\d)+', html_string)

        if match:
            # Get the ID from the match
            id = match.group(0)[3:]

            response = requests.get(recordings_url + str(host_nr) + '/' + id + '.wav')
            if response.status_code == 200:
                # Open the file in write-binary mode and write the response content to it
                with open(os.path.join(captures, f'{host_nr}.wav'), 'wb') as file:
                    file.write(response.content)
                return True
            else:
                print('An error occurred while trying to fetch the WAV file.')
                return False
        else:
            # If not found, print a message
            print(f'The pattern was not found in the HTML content.')
            return False
    else:
        print('An error occurred while trying to fetch the webpage.')
        return False


def vlf_get_live_hosts(live_url, streams_url):
    # Send a GET request
    response = requests.get(live_url)

    # Check that the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'lxml')

        # Convert the parsed HTML to a string
        html_string = str(soup)

        # Set the pattern
        pattern = r"src=\"" + streams_url + "(\d+)\""

        # Find all the occurrences of the pattern
        matches = re.findall(pattern, html_string)

        if matches.count == 0:
            # If not found, print a message
            print(f'The pattern was not found in the HTML content.')
            return []

        return matches
    else:
        print('An error occurred while trying to fetch the webpage.')
        return []


def vlf_live(url, duration, output):
    # Convert the duration in seconds to the format HH:MM:SS
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"

    # Set up the ffmpeg command
    cmd = ['ffmpeg', '-y', '-i', url, '-t', duration_str, '-ac',
           '1', '-sample_fmt', 's16', '-f', 'wav', output]
    
    # Run the command
    result = run(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # Check for errors
    if result.returncode != 0:
        print(f"Error: {result.stderr.decode('utf-8')}")
    else:
        print("Successful download!")


def fm_record(freq='103.8M', audio_file='output.wav', time='5', sample_rate='32k'):
    # Set up the rtl_fm command to demodulate Wideband FM with a 60 ppm error
    rtl_fm_cmd = ['rtl_fm', '-M', 'wbfm', '-f', freq, '-p', '60']

    # Allow for different sample rates
    if sample_rate != '32k':
        rtl_fm_cmd += ['-r', sample_rate]

    # Run the command and pipe the output to a file
    radio = Popen(rtl_fm_cmd, stdout=PIPE)

    # Set up the rtl_fm command to match the sampling rate with the resampling
    # rate of the radio output and to use a single channel
    # Also trim the time
    sox_cmd = ['sox', '-t', 'raw', '-r', sample_rate, '-es', '-b', '16', '-c',
               '1', '-V0', '-', audio_file, 'trim', '0', time]

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
