set PATH=c:\python35\;c:\python35\scripts\;%PATH%

python ..\jobs_launcher\executeTests.py --tests_root ..\jobs --work_root ..\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya2017\bin\maya.exe" RenderDevice 0 TestsFilter full
