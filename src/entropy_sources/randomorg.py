from entropy_sources.source import source

import numpy as np
from scipy.io import wavfile

from os.path import join
from subprocess import check_output

INTEGERS_URL = 'https://www.random.org/integers/'
MAX_NUM = 10000


class randomorg_source(source):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def acquire(self, duration):
        super().acquire(duration)

        total_num = duration * self.sample_rate
        data = np.array([], dtype=np.int16)

        while total_num > 0:
            total_num -= MAX_NUM

            # Get a block of data
            data_block = randomorg_source.get_data_block(MAX_NUM)

            # Concatenate all blocks into one array
            data = np.concatenate((data, data_block))

        # Set the path of the file
        file = join(self.source_dir, 'randomorg.wav')

        # Write the data to a new WAV file
        wavfile.write(file, self.sample_rate, data)

    def get_data_block(num):
        min = np.iinfo(np.int16).min
        max = np.iinfo(np.int16).max

        url = INTEGERS_URL + '?' + \
            f'num={num}&min={min}&max={max}' + \
            '&col=1&base=10&format=plain&rnd=new'

        # Send a GET request
        curl_command = ['curl', '-s', url]

        # Run the command and get the output
        response = check_output(curl_command)

        # Convert the byte string content to a string
        str_string = response.decode('utf-8')

        # Split the string into individual numbers
        str_list = str_string.split()

        if not str_list[0].isnumeric():
            return np.array([], dtype=np.int16)

        # Convert the list of strings to a list of integers
        int_list = [int(i) for i in str_list]

        # Convert the list of integers to a NumPy array of 16-bit signed integers
        arr = np.array(int_list, dtype=np.int16)

        return arr
