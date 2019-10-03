#!/bin/bash

python3 ../jobs_launcher/executeTests.py --test_filter "$3" --file_filter $2 --tests_root ../jobs --work_root ../Work/Results --work_dir Maya --cmd_variables Tool "maya2017" RenderDevice "$1" ResPath "$CIS_TOOLS/../TestResources/MayaAssets" PassLimit 50 rx 0 ry 0 SPU 10