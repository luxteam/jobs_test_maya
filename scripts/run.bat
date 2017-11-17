set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set HWProfiles=CPU
set TestsFilter=small
set Tool=2017

python ..\..\jobs_launcher\executeTests.py --tests_root ..\jobs --work_root ..\Results --work_dir maya