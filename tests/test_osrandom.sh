#!/bin/bash

python3 src/main.py                                                                             \
    --source osrandom                                                                           \
    --acquire                                                                                   \
    --plots "[distribution, spectrum, spectrogram, magnitude_distribution, phase_distribution]" \
    --tests "[ent, rngtools]"
