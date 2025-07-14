from abc import ABC, abstractmethod

from os.path import join
from os import makedirs, listdir

import wave

from multiprocessing import Pool
from itertools import combinations

import numpy as np
from utils.lazy import lazy_wav_blocks

BUFFER_SIZE_MB = 100
BUFFER_SIZE_BYTES = BUFFER_SIZE_MB * 1024 * 1024


class operation(ABC):
    # Use keyworded arguments to allow for more flexibility
    def __init__(
        self,
        audio_dir=None,
        product_dir=None,
        eval_dir=None,
        block_size=None,
        nr_inputs=1,
        sample_rate=None,
    ):
        self.audio_dir = audio_dir
        self.product_dir = product_dir
        self.eval_dir = eval_dir

        self.block_size = block_size
        self.nr_inputs = nr_inputs
        self.sample_rate = sample_rate

    # This is the function that will be applied to each combination of blocks
    @abstractmethod
    def blocks_func(self, **args):
        pass

    def blocks_func_tuple(self, args):
        return self.blocks_func(*args)

    def execute(self):
        # Get all wav files in the directory
        wavs = list(filter(lambda f: f.endswith(".wav"), listdir(self.audio_dir)))

        # Sort the files
        wavs.sort()

        # If wavs is empty
        if len(wavs) == 0:
            # Exit early
            return

        # Create the product directory
        makedirs(self.product_dir, exist_ok=True)

        # Iterate through all wav files in the directory
        for t in list(combinations(wavs, self.nr_inputs)):
            # Get the full path of the input files
            files = list(map(lambda f: join(self.audio_dir, f), t))

            # Check that all files have the same sample rate and number of frames
            sample_rate, nframes, nchannels, sampwidth = operation.check_wav_files(
                files
            )
            flag = (
                sample_rate is not None
                and nframes is not None
                and nchannels is not None
                and sampwidth is not None
            )
            assert flag, "All inputs must have the same format"

            # Block size edge case
            if self.block_size is None or self.block_size > nframes:
                self.block_size = nframes

            # Evaluate blocks as needed
            lazy_wavs = map(lambda f: lazy_wav_blocks(f, self.block_size), files)

            # Zip to get block tuples (lazily)
            block_tuples = zip(*lazy_wavs)

            # Output WAV file path
            product_file = join(self.product_dir, "-".join(t))

            buffer = bytearray()

            # Open wave file for writing
            with wave.open(product_file, "wb") as wf:
                wf.setnchannels(nchannels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(sample_rate)

                # Process in parallel, lazily
                with Pool() as pool:
                    for block in pool.imap(self.blocks_func_tuple, block_tuples, chunksize=100):
                        buffer.extend(block.tobytes())

                        # If buffer exceeds threshold, write to file
                        if len(buffer) >= BUFFER_SIZE_BYTES:
                            wf.writeframes(buffer)
                            buffer.clear()

                    wf.writeframes(buffer)

    def check_wav_files(files):
        # Sample rate and number of frames of the first file
        sample_rate = None
        nframes = None
        nchannels = None
        sampwidth = None

        for file in files:
            with wave.open(file, "rb") as audio_file:
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

                if nchannels is None:
                    nchannels = audio_file.getnchannels()
                elif nchannels != audio_file.getnchannels():
                    # Number of channels do not match
                    return None, None

                if sampwidth is None:
                    sampwidth = audio_file.getsampwidth()
                elif sampwidth != audio_file.getsampwidth():
                    # Data sizes do not match
                    return None, None

        # Return all info
        return sample_rate, nframes, nchannels, sampwidth

    def normalize_and_scale(data, res_type=np.int16):
        local_max = np.max(np.abs(data))
        if local_max == 0:
            return data

        # Normalize the data
        normalized_data = data / np.max(np.abs(data))

        # Scale the data
        max_val = np.iinfo(res_type).max
        scaled_data = res_type(normalized_data * max_val)

        return scaled_data

    def get_fft_index(self, frequency):
        return round(frequency * self.block_size / self.sample_rate)
