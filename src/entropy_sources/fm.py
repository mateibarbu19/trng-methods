from entropy_sources.source import source

from subprocess import run, Popen, PIPE, DEVNULL

from os.path import join

DEFAULT_FREQUENCYS = ['101.9M', '102.8M']


class fm_source(source):
    def __init__(self, freqs=DEFAULT_FREQUENCYS, gain='33.8', ppm='50', **kwargs):
        super().__init__(**kwargs)

        self.freqs = freqs
        self.gain = gain
        self.ppm = ppm

    def acquire(self, duration):
        super().acquire(duration)

        for freq in self.freqs:
            self.fm_record(freq, str(duration))

    def fm_record(self, freq, duration):
        # Set up the rtl_fm command to demodulate FM radio
        rtl_fm_cmd = ['rtl_fm', '-M', 'fm', '-s', '176.4k', '-r',
                      f'{self.sample_rate}', '-A', 'lut', '-g', self.gain,
                      '-p', self.ppm, '-f', freq]

        # Run the command and pipe the output to a file
        radio = Popen(rtl_fm_cmd, stdout=PIPE, stderr=DEVNULL)

        # Create the base directory for the acquisitions
        audio_file = join(self.source_dir, f'{freq}.wav')

        # Set up the rtl_fm command to match the sampling rate with the resampling
        # rate of the radio output and to use a single channel
        # Also trim the time
        sox_cmd = ['sox', '-t', 'raw', '-r', f'{self.sample_rate}', '-es',
                   '-b', '16', '-c', '1', '-V0', '-', audio_file, 'trim', '0', duration]

        # Run the command and set the input to the last pipe
        record = run(sox_cmd, stdin=radio.stdout, stderr=DEVNULL)

        # Allow the radio process to be terminated when the sox process is done
        radio.stdout.close()
        radio.wait()

        # Check for errors
        if radio.returncode != 0 or record.returncode != 0:
            print(f"Radio exit code: {radio.stderr.decode('utf-8')}")
            print(f"Recording exit code: {record.stderr.decode('utf-8')}")
        else:
            print("Successful recording!")
