from transformations.transform import Transformation

import numpy as np
from scipy.stats import rankdata


class UniformizeSignal(Transformation):
    def block_func(self, data):
        # Normalize the data to the range of int16
        data = data / np.max(np.abs(data))

        # Apply the quantile transformation
        ranked_data = rankdata(data, method='average')
        uniform_data = (ranked_data - 1) / (len(ranked_data) - 1)

        # Scale the data back to int16
        uniform_data_int16 = np.int16(
            uniform_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) + np.iinfo(np.int16).min)

        return uniform_data_int16


class UniformizeSpectrum(Transformation):
    def block_func(self, data):
        # Compute the spectrum using FFT
        spectrum = np.fft.fft(data)

        # Compute the magnitudes and phases of the spectrum
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)

        # Apply the quantile transformation to the magnitudes
        ranked_magnitudes = rankdata(magnitudes, method='average')
        uniform_magnitudes = (ranked_magnitudes - 1) / \
            (len(ranked_magnitudes) - 1)

        # Scale the magnitudes back to the original range
        uniform_magnitudes_scaled = uniform_magnitudes * \
            (np.max(magnitudes) - np.min(magnitudes)) + np.min(magnitudes)

        # Construct the transformed spectrum with the transformed magnitudes and original phases
        transformed_spectrum = uniform_magnitudes_scaled * np.exp(1j * phases)

        # Compute the inverse FFT of the transformed spectrum and take the real part of the complex output
        transformed_data = np.real(np.fft.ifft(transformed_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        max_val = np.iinfo(np.int16).max
        transformed_data_int16 = np.int16(
            transformed_data / np.max(np.abs(transformed_data)) * max_val)

        return transformed_data_int16
