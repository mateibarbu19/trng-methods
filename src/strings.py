import sys

SOURCE_FORMAT='''Source must be in one of the following formats:
    - name
    - name(option_1=val_1,...,option_n=val_n)
Examples:
    - osrandom
    - fm(freqs=["80M", "160M"], gain="33.8", ppm="50")
'''

OPERATIONS_FORMAT='''Operations must be in one of the following formats:
    - name
    - name(option_1=val_1,...,option_n=val_n)
    - [name_1(...), ..., name_n(...)]

Examples:
    - autocorrelate_spectrum
    - filter_spectrum_average(window_size=100)
    - [uniformize_spectrum_median(block_size=64), winsorize_spectrum, uniformize_signal]
'''

PLOTS_FORMAT='''Plots must be in one of the following format:
    - name
    - [name_1, ... name_n]
    
Examples:
    - wave
    - [spectrum, spectrogram]
'''

TESTS_FORMAT='''Tests must be in one of the following format:
    - name
    - [name_1, ... name_n]
    
Examples:
    - ent
    - [ent, rngtools]
'''

BANNER=f'''Command-line tool for prototyping TRNGs.

The program can be used to acquire data from an entropy source, 
apply operations on the data, plot and evaluate the results.

General steps are as follows, each one being optional:
    1. Acquire data from a source.
      1.1. Evaluate and/or plot the results.
    2. Apply operations on the data.
      2.1. Evaluate and/or plot the results at each operation.

Data is stored in 16-bit mono channel WAV files at the sample rate specified by
the user.

Each source or operation can be tweaked by using key-value pairs.
Please use only valid Python expressions as in the examples below for each
parameter.
Please take into account your shells escape sequnces if you plan to use spaces.
Here is an example in Bash for an FM radio noise source.

python3 {sys.argv[0]}                                                                                   \\
    --source 'fm(freqs=["80M", "160M", "230M"])'                                                      \\
    --acquire                                                                                         \\
    --name test_fm                                                                                    \\
    --block_size 65536                                                                                \\
    --operations "[uniformize_spectrum_median(block_size=64), winsorize_spectrum, uniformize_signal]" \\
    --evaluate_only_last_operation                                                                    \\
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]"       \\
    --tests "[ent, rngtools]"

All options:
'''
