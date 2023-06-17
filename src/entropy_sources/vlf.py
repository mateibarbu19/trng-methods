from entropy_sources.source import source

import os
from concurrent.futures import ThreadPoolExecutor
from subprocess import run, DEVNULL

import re
import requests
from bs4 import BeautifulSoup

from pydub import AudioSegment

from plots import plot_type, plot_spectrogram, plot_distribution

# URLs for VLF radio noise
EVENTS_URL = 'http://abelian.org/vlf/events.php?stream=vlf'
RECORDINGS_URL = 'http://abelian.org/vsa/vlf'
LIVE_URL = 'http://abelian.org/vlf/'
STREAMS_URL = 'http://5.9.106.210/vlf'


class vlf_source(source):
    def __init__(self, captures, results):
        super().__init__(captures, results)

    def acquire(self, duration, plot_types):
        # Create the base directory for the acquisitions
        os.makedirs(self.captures, exist_ok=True)

        # Get all hosts
        hosts = self.get_live_hosts(LIVE_URL, STREAMS_URL)

        # Download audio clips from all URLs in parallel
        with ThreadPoolExecutor() as executor:
            for host in hosts:
                audio_file = os.path.join(self.captures, f'{host}.wav')
                executor.submit(self.record_live, STREAMS_URL +
                                host, duration, audio_file)

        # Trim all files to minimum duration
        # Initialize minimum duration
        min_duration = float('inf')

        # Get all files in the directory
        files = os.listdir(self.captures)

        # Iterate through all wav files in the directory
        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = os.path.join(self.captures, file)

                # Load audio file
                audio = AudioSegment.from_wav(path)

                # Update minimum duration
                min_duration = min(min_duration, len(audio))

        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = os.path.join(self.captures, file)

                # Load audio file
                audio = AudioSegment.from_wav(path)

                # Trim audio file
                trimmed_audio = audio[:min_duration]

                # Export trimmed audio file
                trimmed_audio.export(path, format="wav")

        plot_types.execute(self.captures, self.results)

    def get_live_hosts(self, live_url, streams_url):
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

    def record_live(self, url, duration, output):
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

    def store_last_event(self, host_nr, events_url, recordings_url):
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

                response = requests.get(
                    recordings_url + str(host_nr) + '/' + id + '.wav')
                if response.status_code == 200:
                    # Open the file in write-binary mode and write the response content to it
                    with open(os.path.join(self.captures, f'{host_nr}.wav'), 'wb') as file:
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
