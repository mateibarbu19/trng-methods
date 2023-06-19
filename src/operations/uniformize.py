from operations.operation import operation

import numpy as np
from scipy.stats import rankdata
from scipy.fft import rfft, irfft


class uniformize_signal(operation):
    def __init__(self, method='ordinal', **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def blocks_func(self, data):
        # Normalize the data to the range of int16
        data = data / np.max(np.abs(data))

        # Apply the quantile transformation
        ranked_data = rankdata(data, method=self.method)
        uniform_data = (ranked_data - 1) / (len(ranked_data) - 1)

        # Scale the data back to int16
        max_val = np.iinfo(np.int16).max
        min_val = np.iinfo(np.int16).min
        uniform_data = np.int16(uniform_data * (max_val - min_val) + min_val)

        return uniform_data


class uniformize_spectrum(operation):
    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        # Compute the magnitude of the spectrum
        magnitude = np.abs(spectrum)

        # Compute the mean magnitude
        mean_magnitude = np.mean(magnitude)

        # Compute the whitened spectrum
        whitened_spectrum = (spectrum / magnitude) * mean_magnitude

        # Return the inverse Fourier transform of the whitened spectrum
        # We use np.real to discard the imaginary part which occurs due to numerical errors
        whitened_data = np.real(irfft(whitened_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        max_val = np.iinfo(np.int16).max
        whitened_data = np.int16(
            whitened_data / np.max(np.abs(whitened_data)) * max_val)

        return whitened_data
