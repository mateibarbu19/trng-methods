from enum import Flag, auto

from os.path import join
from os import listdir, makedirs
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE

from scipy.io import wavfile


class test_type(Flag):
    NONE = auto()
    ENT = auto()
    RNGTOOLS = auto()

    def execute(self, audio_dir, eval_dir):
        # Skip if no tests are requested
        if self == test_type.NONE:
            return

        with ThreadPoolExecutor() as executor:
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

                if self & test_type.ENT:
                    test = join(base, 'ent.txt')
                    executor.submit(test_ent, file, test)

                if self & test_type.RNGTOOLS:
                    test = join(base, 'rngtools.txt')
                    executor.submit(test_rngtools, file, test)

def test_ent(audio_file, output):
    # Read the audio file
    _, data = wavfile.read(audio_file)

    with open(output, 'w') as o:
        # Open a subprocess and send the array
        with Popen(['ent'], stdin=PIPE, stdout=o) as proc:
            proc.stdin.write(data.tobytes())


def test_rngtools(audio_file, output):
    # Read the audio file
    _, data = wavfile.read(audio_file)

    # Open a subprocess and send the array
    proc = Popen(['rngtest'], stdin=PIPE, stderr=PIPE)

    # Send the array
    proc.stdin.write(data.tobytes())
    proc.stdin.close()

    # Open the output file
    with open(output, 'w') as o:
        # Enumerate over the output lines
        for i, line in enumerate(iter(proc.stderr.readline, b'')):
            line = line.decode()  # convert bytes to string
            # Write only a range of lines
            if 7 <= i < 15:
                o.write(line)
