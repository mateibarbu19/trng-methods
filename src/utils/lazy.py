import wave
import numpy as np

from utils.data import sample_width_to_np_dtype

class lazy_wav_blocks:
    def __init__(self, file_path, block_size=1024):
        self.file_path = file_path
        self.block_size = block_size

        # Read WAV metadata once
        with wave.open(self.file_path, 'rb') as wav_file:
            self.num_channels = wav_file.getnchannels()
            self.sample_width = wav_file.getsampwidth()
            self.frame_rate = wav_file.getframerate()
            self.num_frames = wav_file.getnframes()

        # Map sample width to numpy dtype
        self.dtype = sample_width_to_np_dtype(self.sample_width)

        if self.dtype is None:
            raise ValueError(f"Unsupported sample width: {self.sample_width}")

    def __iter__(self):
        with wave.open(self.file_path, 'rb') as wav_file:
            while True:
                frames = wav_file.readframes(self.block_size)
                if not frames:
                    break

                samples = np.frombuffer(frames, dtype=self.dtype)
                if self.num_channels > 1:
                    samples = samples.reshape(-1, self.num_channels)

                yield samples


