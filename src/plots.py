from enum import Flag, auto

from os.path import join
from os import listdir, makedirs
from pathlib import Path

# Wav files
import wave
from scipy.io import wavfile

# Maths
import numpy as np
from matplotlib.mlab import window_hanning
from scipy.fft import rfft, rfftfreq

# Plots and images
import matplotlib.pyplot as plt
import seaborn

import librosa
import librosa.display

from PIL import Image

# List of colors to use for plots.
color_list = ['skyblue', 'orange', 'green', 'red',
              'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

# Use seaborn styles for pretty plots
seaborn.set_theme(style="darkgrid")


class plot_type(Flag):
    NONE = auto()
    WAVE = auto()
    DISTRIBUTION = auto()
    SPECTROGRAM = auto()
    SPECTRUM = auto()
    MAGNITUDE_DISTRIBUTION = auto()
    PHASE_DISTRIBUTION = auto()
    BITMAP = auto()

    def execute(self, audio_dir, eval_dir):
        # Skip if no plots are requested
        if self == plot_type.NONE:
            return

        # Iterate through all wav files in the directory
        for file in listdir(audio_dir):
            # skip if it isn't a wav file
            if not file.endswith(".wav"):
                continue

            name = Path(file).stem
            file = join(audio_dir, file)

            # Set the base directory for the results of a file
            base = join(eval_dir, name)
            makedirs(base, exist_ok=True)

            if self & plot_type.WAVE:
                # Plot the wave
                img = join(base, f'wave.png')
                plot_waves([file], img)

            if self & plot_type.DISTRIBUTION:
                # Plot the distribution
                img = join(base, f'distribution.png')
                plot_distribution(file, img)

            if self & plot_type.SPECTROGRAM:
                # Plot the spectrogram
                img = join(base, f'spectrogram.png')
                plot_spectrogram(file, img)

            if self & plot_type.SPECTRUM:
                # Plot the spectrum
                img = join(base, f'spectrum.png')
                plot_spectrum(file, img)

            if self & plot_type.MAGNITUDE_DISTRIBUTION:
                # Plot the magnitude distribution
                img = join(base, f'magnitude_distribution.png')
                plot_magnitude_distribution(file, img)

            if self & plot_type.PHASE_DISTRIBUTION:
                # Plot the phase distribution
                img = join(base, f'phase_distribution.png')
                plot_phase_distribution(file, img)

            if self & plot_type.BITMAP:
                # Plot the bitmap
                img = join(base, f'bitmap.png')
                audio_to_bitmap(file, img)


def plot_waves(audio_files, output, title=None, labels=None):
    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(12, 6))

    nr_audios = len(audio_files)
    nr_colors = len(color_list)

    # Check if more files than colors available
    assert nr_audios <= nr_colors, f'Please add more colors. ' + \
        f'Number of files({nr_audios}) exceeds number of colors({nr_colors}).'

    # Assert that labels and audio_files have the same length
    assert labels is None or nr_audios == len(labels), \
        "The number of labels must be the same as the number of audio files."

    # Load and plot each file
    for i, filename in enumerate(audio_files):
        # Load the audio file
        y, sr = librosa.load(filename, sr=None)

        # Generate a time axis
        t = np.arange(len(y)) / sr

        # Get the label
        if labels is not None:
            legend_label = labels[i]
        else:
            legend_label = f'Wave of {filename}'

        # Plot the wave
        plt.plot(t, y, color=color_list[i], label=legend_label)

    if title is None:
        title = 'Wave of ' + ' '.join(audio_files)

    # Plot the wave
    plt.title(title, fontsize=16)
    plt.xlabel("Time (s)", fontsize=14)
    plt.ylabel("Amplitude", fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(True)

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()


def plot_distribution(audio_file, output, description=None):
    # Open the WAV file
    with wave.open(audio_file, 'rb') as wav_file:
        # Read the frames from the WAV file
        frames = wav_file.readframes(wav_file.getnframes())

    # Convert the frames to a numpy array of 16-bit signed integers
    data = np.frombuffer(frames, dtype=np.int16)

    if description is None:
        description = 'Data distribution of ' + audio_file

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))

    # Plot a histogram of the data values with a higher number of bins and a subtle color
    ax = seaborn.histplot(data, bins=100, color='skyblue',
                          edgecolor='black', kde=True)
    ax.lines[0].set_color('xkcd:pumpkin orange')
    ax.lines[0].set_linewidth(2)

    # Label the axes and provide a title
    plt.title(description, fontsize=16)
    plt.xlabel("Amplitude", fontsize=14)
    plt.ylabel("Density", fontsize=14)
    plt.grid(True)

    # Use tight layout to optimize space
    plt.tight_layout()

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')

    # Close the figure
    plt.close()


def plot_spectrogram(audio_file, output, title=None):
    # Read the .wav file
    file = wave.open(audio_file, 'rb')

    # Extract Raw Audio from Wav File
    raw_signal = file.readframes(-1)
    raw_signal = np.frombuffer(raw_signal, np.int16)

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))

    # Set up the plot in a printer-friendly way
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['figure.titlesize'] = 16

    plt.specgram(raw_signal, NFFT=1024, Fs=file.getframerate(),
                 window=window_hanning, scale='dB', cmap='viridis')

    if title is None:
        title = 'Spectrogram of ' + audio_file + ' file'

    # Label the axes and provide a title
    plt.title(title)
    plt.xlabel('Time (sec)')
    plt.ylabel('Frequency (Hz)')

    plt.colorbar(label='Amplitude (dB)', orientation='vertical')

    # Use tight layout to optimize space
    plt.tight_layout()

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')

    # Close the figure
    plt.close()


def plot_spectrum(audio_file, output, title=None):
    # Read the wav file
    sample_rate, data = wavfile.read(audio_file)

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))

    # Calculate and plot the magnitude spectrum
    plt.magnitude_spectrum(
        data, Fs=sample_rate, color='xkcd:azure', window=window_hanning, scale='linear')

    if title is None:
        title = 'Spectrum of ' + audio_file + ' file'

    # Label the axes and provide a title
    plt.title(title, fontsize=16)
    plt.xlabel('Frequency (Hz)', fontsize=14)
    plt.ylabel('Magnitude', fontsize=14)
    plt.grid(True)

    # Use tight layout to optimize space
    plt.tight_layout()

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()


def plot_magnitude_distribution(audio_file, output, title=None):
    # Read the wav file
    _, data = wavfile.read(audio_file)

    # Apply a Hanning window to the data
    windowed_data = window_hanning(data)

    # Take the Fourier transform
    spectrum = rfft(windowed_data)
    magnitudes = np.abs(spectrum)

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))

    # Plot the distribution of magnitudes
    ax = seaborn.histplot(magnitudes, bins=100, color='skyblue',
                          kde=True)
    ax.lines[0].set_color('xkcd:pumpkin orange')
    ax.lines[0].set_linewidth(2)

    if title is None:
        title = 'Distribution of Magnitudes in ' + audio_file + ' file'

    # Label the axes and provide a title
    plt.title(title, fontsize=16)
    plt.xlabel('Magnitude', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.grid(True)

    # Use tight layout to optimize space
    plt.tight_layout()

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()


def plot_phase_distribution(audio_file, output, title=None):
    # Read the wav file
    _, data = wavfile.read(audio_file)

    # Apply a Hanning window to the data
    windowed_data = window_hanning(data)

    # Take the Fourier transform
    spectrum = rfft(windowed_data)
    phases = np.angle(spectrum)

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))

    # Plot the distribution of phases
    ax = seaborn.histplot(phases, bins=100, color='skyblue',
                          edgecolor='black', kde=True)
    ax.lines[0].set_color('xkcd:pumpkin orange')
    ax.lines[0].set_linewidth(2)

    if title is None:
        title = 'Distribution of Phases in ' + audio_file + ' file'

    # Label the axes and provide a title
    plt.title(title, fontsize=16)
    plt.xlabel('Phase (radians)', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.grid(True)

    # Use tight layout to optimize space
    plt.tight_layout()

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()


def audio_to_bitmap(audio_file, output):
    # Read the audio file
    _, data = wavfile.read(audio_file)

    # Normalize to 0-255
    data = ((data / np.max(np.abs(data))) * 255).astype(np.uint8)

    # Reshape the data into a square format
    length = data.shape[0]
    dim = int(np.sqrt(length)) + 1

    # Pad the data if it cannot be reshaped into a perfect square
    data = np.pad(data, (0, dim*dim - length), 'constant', constant_values=255)

    # Reshape the data into a square
    image_data = data.reshape((dim, dim))

    # Convert the array into an image
    img = Image.fromarray(image_data)

    # Save the image
    img.save(output)
