from abc import ABC, abstractmethod

import os

import numpy as np
import wave
from scipy.io import wavfile

from multiprocessing import Pool
from itertools import combinations


class operation(ABC):
    # Use keyworded arguments to allow for more flexibility
    def __init__(self, audio_dir=None, product_dir=None, eval_dir=None, block_size=None, nr_inputs=1):
        self.audio_dir = audio_dir
        self.product_dir = product_dir
        self.eval_dir = eval_dir
        self.block_size = block_size
        self.nr_inputs = nr_inputs

    # This is the function that will be applied to each combination of blocks
    @abstractmethod
    def blocks_func(self, **args):
        pass

    def execute(self):
        # Get all wav files in the directory
        wavs = list(filter(lambda f:
                           f.endswith('.wav'), os.listdir(self.audio_dir)))

        # Sort the files
        wavs.sort()

        # If wavs is not empty
        if len(wavs) != 0:
            # Create the product directory
            os.makedirs(self.product_dir, exist_ok=True)

        # Iterate through all wav files in the directory
        for tuple in list(combinations(wavs, self.nr_inputs)):
            # Get the full path of the input files
            files = list(
                map(lambda f: os.path.join(self.audio_dir, f), tuple))

            # Check that all files have the same sample rate and number of frames
            sample_rate, nframes = operation.check_wav_files(files)
            flag = sample_rate is not None and nframes is not None
            assert flag, 'All inputs must have the same sample rate and duration'

            # Block size edge case
            if self.block_size is None or self.block_size > nframes:
                self.block_size = nframes

            # Aggregate the blocks from each file
            blocks_list = map(lambda f: self.get_blocks(f), files)

            # "Transpose" the blocks
            blocks_arg = list(zip(*blocks_list))

            with Pool() as pool:
                transformed_blocks = pool.starmap(self.blocks_func, blocks_arg)

            # Concatenate all blocks back into one array
            transformed_data = np.concatenate(transformed_blocks)

            # Set the path of the product file
            product_file = os.path.join(
                self.product_dir, '-'.join(tuple))

            # Write the transformed data to a new WAV file
            wavfile.write(product_file, sample_rate, transformed_data)

    def check_wav_files(files):
        # Sample rate and number of frames of the first file
        sample_rate = None
        nframes = None

        for file in files:
            with wave.open(file, 'rb') as audio_file:
                if sample_rate is None:
                    sample_rate = audio_file.getframerate()
                elif sample_rate != audio_file.getframerate():
                    # Sample rates do not match
                    return None, None

                if nframes is None:
                    nframes = audio_file.getnframes()
                elif nframes != audio_file.getnframes():
                    # Number of frames do not match
                    return None, None

        # All files have the same sample rate and number of frames
        return sample_rate, nframes

    def get_blocks(self, file):
        # Read the WAV file
        _, data = wavfile.read(file)

        # Break data into blocks
        blocks = [data[i:i+self.block_size]
                  for i in range(0, len(data), self.block_size)]

        return blocks
