#!/bin/bash

python3 src/main.py                                                                             \
    --source 'vlf(hosts=["15", "35", "41"])'                                                    \
    --acquire                                                                                   \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]" \
    --tests ent

python3 src/main.py                                                                               \
    --source vlf                                                                                  \
    --operations "[expand_band, uniformize_spectrum_median, uniformize_signal(block_size=65536)]" \
    --evaluate_only_last_operation                                                                \
    --name test_vlf                                                                               \
    --block_size 64                                                                               \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]"   \
    --tests "[ent, rngtest]"
