#!/bin/bash

python3 src/main.py                                                                             \
    --source 'fm(freqs=["80M", "160M", "230M"])'                                                \
    --acquire                                                                                   \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]" \
    --tests ent

python3 src/main.py                                                                                   \
    --source fm                                                                                       \
    --operations "[uniformize_spectrum_median(block_size=64), winsorize_spectrum, uniformize_signal]" \
    --evaluate_only_last_operation                                                                    \
    --name test_fm                                                                                    \
    --block_size 65536                                                                                \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]"       \
    --tests "[ent, rngtest]"
