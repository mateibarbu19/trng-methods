

def fm_record(freq='103.8M', audio_file='output.wav', time='5', sample_rate='32k'):
    # Set up the rtl_fm command to demodulate Wideband FM with a 60 ppm error
    rtl_fm_cmd = ['rtl_fm', '-M', 'wbfm', '-f', freq, '-p', '60']

    # Allow for different sample rates
    if sample_rate != '32k':
        rtl_fm_cmd += ['-r', sample_rate]

    # Run the command and pipe the output to a file
    radio = Popen(rtl_fm_cmd, stdout=PIPE)

    # Set up the rtl_fm command to match the sampling rate with the resampling
    # rate of the radio output and to use a single channel
    # Also trim the time
    sox_cmd = ['sox', '-t', 'raw', '-r', sample_rate, '-es', '-b', '16', '-c',
               '1', '-V0', '-', audio_file, 'trim', '0', time]

    # Run the command and set the input to the last pipe
    record = run(sox_cmd, stdin=radio.stdout)

    # Allow the radio process to be terminated when the sox process is done
    radio.stdout.close()
    radio.wait()

    # Check for errors
    if radio.returncode != 0 or record.returncode != 0:
        print(f"Radio exit code: {radio.stderr.decode('utf-8')}")
        print(f"Recording exit code: {record.stderr.decode('utf-8')}")
    else:
        print("Successful recording!")
