set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%

set TOOL=%1
if not defined TOOL set TOOL=2019

"C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" -command "python(\"import cache_building\")"
