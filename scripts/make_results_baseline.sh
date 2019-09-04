#!/bin/bash
set PYTHONPATH=..\jobs_launcher\;%PYTHONPATH%

python3 ..\jobs_launcher\common\scripts\generate_baseline.py --results_root ..\Work\Results\Maya --baseline_root ..\Work\Baseline