set PATH=c:\python35\;c:\python35\scripts\;%PATH%

python ..\jobs_launcher\executeTests.py --tests_root ..\jobs_special --work_root ..\Work\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya2018\bin\maya.exe" RenderDevice gpu ResPath "C:\TestResources\GLTF_export\Maya" PassLimit 50 rx 0 ry 0 SPU 10