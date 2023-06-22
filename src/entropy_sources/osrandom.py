from entropy_sources.source import source

import numpy as np
from scipy.io import wavfile

from os.path import join
from os import getrandom, GRND_RANDOM


class osrandom_source(source):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def acquire(self, duration):
        super().acquire(duration)

        total_num = duration * self.sample_rate * 2

        byte_arr = getrandom(total_num, GRND_RANDOM)

        # Convert the byte array to a NumPy array of 16-bit signed integers
        data = np.frombuffer(byte_arr, dtype=np.int16)

        # Set the path of the file
        file = join(self.source_dir, 'osrandom.wav')

        # Write the data to a new WAV file
        wavfile.write(file, self.sample_rate, data)
