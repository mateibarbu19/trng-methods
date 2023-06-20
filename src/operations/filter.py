from operations.operation import operation
from abc import abstractmethod

import numpy as np
from scipy.signal import convolve, medfilt
from scipy.signal import iirnotch, lfilter
from scipy.stats import norm
from scipy.fft import rfft, irfft


class filter_spectrum_magnitudes(operation):
    @abstractmethod
    def filter_magnitudes(self, magnitudes):
        pass

    def blocks_func(self, data):
        # Take FFT
        spectrum = rfft(data)

        # Compute the magnitudes and phases of the spectrum
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)

        # Filter the magnitudes
        filtered_magnitudes = self.filter_magnitudes(magnitudes)

        # Retain original phases
        filtered_spectrum = np.multiply(filtered_magnitudes, np.exp(1j*phases))

        # Inverse FFT
        filtered_data = np.real(irfft(filtered_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        return operation.normalize_and_scale(filtered_data)


class filter_spectrum_linear(filter_spectrum_magnitudes):
    def __init__(self, kernel=None, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def filter_magnitudes(self, magnitudes):
        # Apply linear filter to the magnitudes of the spectrum
        return convolve(magnitudes, self.kernel, mode='same')


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


class filter_spectrum_median(filter_spectrum_magnitudes):
    def __init__(self, window_size=51, **kwargs):
        super().__init__(**kwargs)
        assert window_size % 2 == 1, "Window size must be odd"
        self.window_size = window_size

    def filter_magnitudes(self, magnitudes):
        # Apply median filter to the magnitudes spectrum
        return medfilt(magnitudes, self.window_size)


class filter_spectrum_notch(operation):
    # notch_freq is the frequency to be removed
    # Q is the quality factor - higher values mean a narrower stop-band
    def __init__(self, notch_freq=19e3, Q=100, **kwargs):
        super().__init__(**kwargs)

        # Numerator and denominator polynomials of the IIR filter
        n, d = iirnotch(notch_freq, Q, 44.1e3)

        self.numerator = n
        self.denominator = d

    def blocks_func(self, data):
        filtered_data = lfilter(
            self.numerator,
            self.denominator,
            data)

        return operation.normalize_and_scale(filtered_data)
