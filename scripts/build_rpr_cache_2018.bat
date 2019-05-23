set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%
"C:\Program Files\Autodesk\Maya2018\bin\maya.exe" -command "python(\"import cache_building\")"
