from operations.operation import operation

import numpy as np
from scipy.signal import convolve, medfilt
from scipy.stats import norm
from scipy.fft import rfft, irfft


class filter_spectrum_linear(operation):
    def __init__(self, kernel=None, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def blocks_func(self, data):
        # Take FFT
        spectrum = rfft(data)

        # Compute the magnitude of the spectrum
        magnitude = np.abs(spectrum)

        # Smooth the magnitude spectrum with a moving average
        filtered_magnitude = convolve(magnitude, self.kernel, mode='same')

        # Retain original phase
        filtered_spectrum = np.multiply(
            filtered_magnitude, np.exp(1j*np.angle(spectrum)))

        # Inverse FFT
        filtered_data = np.real(irfft(filtered_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        max_val = np.iinfo(np.int16).max
        filtered_data = np.int16(
            filtered_data / np.max(np.abs(filtered_data)) * max_val)

        return filtered_data


class filter_spectrum_average(filter_spectrum_linear):
    def __init__(self, window_size=50, **kwargs):
        assert window_size % 2 == 0, "Window size must be even"

        # Create a moving average kernel
        moving_average_kernel = np.ones(self.window_size) / self.window_size

        # Call the parent constructor
        kwargs['kernel'] = moving_average_kernel
        super().__init__(**kwargs)


class filter_spectrum_gaussian(filter_spectrum_linear):
    def __init__(self, sigma=1.0, nr_std_dev=3.0, **kwargs):
        # Create a Gaussian kernel.
        # The size of the kernel is chosen to be 3 standard deviations,
        # which captures over 99% of the area under the Gaussian curve.
        kernel_size = int(nr_std_dev * sigma)
        x = np.arange(-kernel_size, kernel_size + 1)
        gaussian_kernel = norm.pdf(x, scale=sigma)

        # Normalize the kernel so it sums to 1.
        gaussian_kernel /= np.sum(gaussian_kernel)

        # Call the parent constructor
        kwargs['kernel'] = gaussian_kernel
        super().__init__(**kwargs)


class filter_spectrum_median(operation):
    def __init__(self, window_size=51, **kwargs):
        super().__init__(**kwargs)
        assert window_size % 2 == 1, "Window size must be odd"
        self.window_size = window_size

    def blocks_func(self, data):
        # Take FFT
        spectrum = rfft(data)

        # Compute the magnitude of the spectrum
        magnitude = np.abs(spectrum)

        # Apply median filter to the magnitude spectrum
        filtered_magnitude = medfilt(magnitude, self.window_size)

        # Retain original phase
        filtered_spectrum = np.multiply(
            filtered_magnitude, np.exp(1j*np.angle(spectrum)))

        # Inverse FFT
        filtered_data = np.real(irfft(filtered_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        max_val = np.iinfo(np.int16).max
        filtered_data = np.int16(
            filtered_data / np.max(np.abs(filtered_data)) * max_val)

        return filtered_data
