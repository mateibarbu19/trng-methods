import wave
from scipy.io import wavfile

import numpy as np
from scipy.signal import spectrogram

from matplotlib import style
import matplotlib.pyplot as plt

import librosa
import librosa.display

from PIL import Image

# List of colors to use for plots.
color_list = ['skyblue', 'orange', 'green', 'red',
              'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']


def plot_spectrogram(audio_file, output, title=None):
    # Read the .wav file
    file = wave.open(audio_file, 'rb')

    # Extract Raw Audio from Wav File
    raw_signal = file.readframes(-1)
    raw_signal = np.frombuffer(raw_signal, np.int16)

    # If Stereo
    assert file.getnchannels() == 1, 'Just mono files'

    # Compute the spectrogram
    spectrogram(raw_signal, file.getframerate())

    # Set up the plot in a printer-friendly way
    plt.figure(figsize=(10, 5))
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['figure.titlesize'] = 16

    plt.specgram(raw_signal, NFFT=1024, Fs=file.getframerate())

    if title is None:
        title = 'Spectrogram of ' + audio_file + ' file'

    # Label the axes and provide a title
    plt.title(title)
    plt.xlabel('Time [sec]')
    plt.ylabel('Frequency [Hz]')

    plt.colorbar(label='Amplitude', orientation='vertical')

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

    # If the data is stereo, take the mean
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Pad the data if it cannot be reshaped into a perfect square
    data = np.pad(data, (0, dim*dim - length), 'constant', constant_values=255)

    # Reshape the data into a square
    image_data = data.reshape((dim, dim))

    # Convert the array into an image
    img = Image.fromarray(image_data)

    # Save the image
    img.save(output)


def plot_distribution(audio_file, output, description=None):
    # Open the WAV file
    with wave.open(audio_file, 'rb') as wav_file:
        # Ensure this is a 16-bit WAV file
        assert wav_file.getsampwidth() == 2, "This function supports only 16-bit audio."
        # Read the frames from the WAV file
        frames = wav_file.readframes(wav_file.getnframes())

    # Convert the frames to a numpy array of 16-bit signed integers
    data = np.frombuffer(frames, dtype=np.int16)

    if description is None:
        description = 'Data distribution of ' + audio_file

    # Use a printer friendly style
    style.use('seaborn-darkgrid')

    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(10, 6))
    # Plot a histogram of the data values with a higher number of bins and a subtle color
    plt.hist(data, bins=100, color='skyblue', edgecolor='black')
    plt.title(description, fontsize=16)
    plt.xlabel("Amplitude", fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.grid(True)

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()

    # Reset the style to the default
    style.use('default')


# TODO legend
def plot_waves(audio_files, output, description=None):
    # Create a new figure with a decently large size (in inches)
    plt.figure(figsize=(12, 6))

    # Check if more files than colors available
    if len(audio_files) > len(color_list):
        print(
            f"Please add more colors. Number of files ({len(audio_files)}) exceeds number of colors ({len(color_list)}).")
        return

    # Load and plot each file
    for i, filename in enumerate(audio_files):
        # Load the audio file
        y, sr = librosa.load(filename, sr=None)

        # Generate a time axis
        t = np.arange(len(y)) / sr

        # Plot the wave
        plt.plot(t, y, color=color_list[i], label=f'Wave of {filename}')

    if description is None:
        description = 'Wave of ' + ' '.join(audio_files)

    # Plot the wave
    plt.title(description, fontsize=16)
    plt.xlabel("Time (s)", fontsize=14)
    plt.ylabel("Amplitude", fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(True)

    # Save the figure as a high-res PNG
    plt.savefig(output, dpi=300, format='png')
    # Close the figure
    plt.close()
