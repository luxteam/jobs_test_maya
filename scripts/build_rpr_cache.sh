#!/bin/bash
export PYTHONPATH=$PWD/../jobs/Scripts;$PYTHONPATH
export MAYA_SCRIPT_PATH=$PWD/../jobs/Scripts;$MAYA_SCRIPT_PATH
"maya2019" -command "python(\"import cache_building\")"