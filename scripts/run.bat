set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set HWProfiles=0,1,2
set TestsFilter=small
set Tool=2017
set ConfigPath=%CD%\Maya.config.json

python ..\..\jobs_launcher\executeTests.py --tests_root ..\jobs --work_root ..\Results --work_dir Maya