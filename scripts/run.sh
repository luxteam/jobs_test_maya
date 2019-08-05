#!/bin/bash

python ../jobs_launcher/executeTests.py --test_filter "" --file_filter $1 --tests_root ../jobs --work_root ../Work/Results --work_dir Maya --cmd_variables Tool "maya" RenderDevice "gpu" ResPath "$CIS_TOOLS/../TestResources/MayaAssets" PassLimit 5 rx 0 ry 0 SPU 10
