set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set RENDER_DEVICE=%1
set TESTS_FILTER=%2
set TEST_PACKAGE=%3
if "%RENDER_DEVICE%" EQU "" set RENDER_DEVICE=gpu
if "%TESTS_FILTER%" EQU "" set TESTS_FILTER=full
if "%TEST_PACKAGE%" EQU "" set TEST_PACKAGE=smoke

python ..\jobs_launcher\executeTests.py --file_filter %TEST_PACKAGE% --tests_root ..\jobs --work_root ..\Work\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya2017\bin\maya.exe" RenderDevice %RENDER_DEVICE% TestsFilter %TESTS_FILTER% ResPath "C:\TestResources\MayaAssets" PassLimit 10 rx 0 ry 0
