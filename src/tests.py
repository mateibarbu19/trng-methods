from enum import Flag, auto

from os.path import join
from os import listdir, makedirs
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE

from utils.lazy import lazy_wav_blocks


class test_type(Flag):
    NONE = auto()
    ENT = auto()
    RNGTEST = auto()

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
                    test = join(base, "ent.txt")
                    executor.submit(test_ent, file, test)

                if self & test_type.RNGTEST:
                    test = join(base, "rngtest.txt")
                    executor.submit(test_rngtest, file, test)


def test_ent(audio_file, output):
    # Evaluate blocks as needed
    blocks = lazy_wav_blocks(audio_file)

    with open(output, "w") as o:
        # Open a subprocess and send the blocks one by one
        with Popen(["ent"], stdin=PIPE, stdout=o) as proc:
            try:
                for block in blocks:
                    raw_bytes = block.astype(blocks.dtype).tobytes()
                    proc.stdin.write(raw_bytes)
                proc.stdin.close()

            except Exception as e:
                proc.kill()
                raise e


def test_rngtest(audio_file, output):
    # Evaluate blocks as needed
    blocks = lazy_wav_blocks(audio_file)

    # Open a subprocess and send the blocks one by one
    with Popen(["rngtest"], stdin=PIPE, stderr=PIPE) as proc:
        try:
            for block in blocks:
                raw_bytes = block.astype(blocks.dtype).tobytes()
                proc.stdin.write(raw_bytes)
            proc.stdin.close()

            # Open the output file
            with open(output, "w") as o:
                # Enumerate over the output lines
                for i, line in enumerate(iter(proc.stderr.readline, b"")):
                    line = line.decode()  # convert bytes to string
                    # Write only a range of lines
                    if 7 <= i < 15:
                        o.write(line)

        except Exception as e:
            proc.kill()
            raise e
