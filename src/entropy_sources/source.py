from abc import ABC, abstractmethod

from os.path import join
from os import makedirs, listdir

from scipy.io import wavfile


class source(ABC):
    # Use keyworded arguments to allow for more flexibility
    def __init__(self, source_dir=None, eval_dir=None,
                 sample_rate=None, block_size=None):
        self.source_dir = source_dir
        self.eval_dir = eval_dir

        self.sample_rate = sample_rate
        self.block_size = block_size

    @abstractmethod
    def acquire(self, duration):
        # Create the base directory for the acquisitions
        makedirs(self.source_dir, exist_ok=True)

    def check(self):
        # Check that all the source files have the same size and sample rate
        min_size = None
        sample_rate = None

        # Get all files in the directory
        files = listdir(self.source_dir)

        # Iterate through all wav files in the directory
        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = join(self.source_dir, file)

                # Load audio file
                sample_rate, data = wavfile.read(path)

                if self.sample_rate is None:
                    self.sample_rate = sample_rate
                else:
                    assert self.sample_rate == sample_rate, "Sample rates do not match"

                if min_size is None:
                    min_size = data.size

                # Update minimum size
                min_size = min(min_size, data.size)

        if self.block_size is not None:
            min_size -= min_size % self.block_size

        # Trim all files to minimum size
        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = join(self.source_dir, file)

                # Load audio file
                sample_rate, data = wavfile.read(path)

                # Trim audio file
                data = data[:min_size]

                # Export trimmed audio file
                wavfile.write(path, sample_rate, data)
