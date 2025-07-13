#!/bin/bash

python3 src/main.py                                                                                  \
    --source randomorg                                                                               \
    --acquire                                                                                        \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]" \
    --tests "[ent, rngtools]"
