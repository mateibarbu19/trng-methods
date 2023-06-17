from abc import ABC, abstractmethod

import os

import numpy as np
from scipy.io import wavfile

from multiprocessing import Pool


class Transformation(ABC):
    # Use keword arguments to allow for more flexibility
    def __init__(self, audio_dir=None, product_dir=None, results_dir=None, block_size=None):
        self.audio_dir = audio_dir
        self.product_dir = product_dir
        self.results_dir = results_dir
        self.block_size = block_size

    # This is the function that will be applied to each block
    @abstractmethod
    def block_func(self, data):
        pass

    def execute(self):
        # Get all wav files in the directory
        wavs = list(filter(lambda f:
                           f.endswith('.wav'), os.listdir(self.audio_dir)))

        # If wavs is not empty
        if len(wavs) != 0:
            # Create the product directory
            os.makedirs(self.product_dir, exist_ok=True)

        # Iterate through all wav files in the directory
        for file in wavs:
            # Get the full path of the files
            audio_file = os.path.join(self.audio_dir, file)
            product_file = os.path.join(self.product_dir, file)

            # Read the WAV file
            sample_rate, data = wavfile.read(audio_file)

            # Block size edge case
            if self.block_size is None or self.block_size > len(data):
                self.block_size = len(data)

            # Flatten the data to 1D if it's stereo
            if len(data.shape) > 1:
                data = data.flatten()

            # Break data into blocks
            blocks = [data[i:i+self.block_size]
                      for i in range(0, len(data), self.block_size)]

            with Pool() as pool:
                transformed_blocks = pool.map(self.block_func, blocks)

            # Concatenate all blocks back into one array
            transformed_data = np.concatenate(transformed_blocks)

            # Write the transformed data to a new WAV file
            wavfile.write(product_file, sample_rate, transformed_data)
