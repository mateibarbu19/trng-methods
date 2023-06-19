from abc import ABC, abstractmethod

import os

from pydub import AudioSegment


class source(ABC):
    # Use keyworded arguments to allow for more flexibility
    def __init__(self, source_dir=None, eval_dir=None):
        self.source_dir = source_dir
        self.eval_dir = eval_dir

    @abstractmethod
    def acquire(self, duration):
        # Create the base directory for the acquisitions
        os.makedirs(self.source_dir, exist_ok=True)

    def trim(self):
        # Trim all files to minimum duration
        # Initialize minimum duration
        min_duration = float('inf')

        # Get all files in the directory
        files = os.listdir(self.source_dir)

        # Iterate through all wav files in the directory
        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = os.path.join(self.source_dir, file)

                # Load audio file
                audio = AudioSegment.from_wav(path)

                # Update minimum duration
                min_duration = min(min_duration, len(audio))

        for file in files:
            if file.endswith(".wav"):
                # Set the path
                path = os.path.join(self.source_dir, file)

                # Load audio file
                audio = AudioSegment.from_wav(path)

                # Trim audio file
                trimmed_audio = audio[:min_duration]

                # Export trimmed audio file
                trimmed_audio.export(path, format="wav")
