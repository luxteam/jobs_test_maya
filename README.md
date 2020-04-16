# Autotests for Radeon ProRender plugin for Autodesk Maya
[![Deployed submodule](https://rpr.cis.luxoft.com/buildStatus/icon?job=Utils/jobs_launcher-Deploy&build=last&config=release-badge)](https://rpr.cis.luxoft.com/job/Utils/job/jobs_launcher-Deploy)

## Install
 1. Clone this repo
 2. Get `jobs_launcher` as git submodule, using next commands  
 `git submodule init`  
 `git submodule update`
 3. Run `scripts/auto_config.bat`. This script will create `scripts/Devices.config.json` for your hardware configuration.  
 4. Check that `maya_assets` scenes placed in `/TestResources` (`git clone https://gitlab.cts.luxoft.com/dtarasenko/maya_assets.git`) and environment variable CIS_TOOLS is set on your TestResources folder. If not follow this guide https://docs.oracle.com/en/database/oracle/r-enterprise/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0
 Variable name should be "CIS_TOOLS" and value is path to TestResources (include "TestResources" in the end)
 5. Run `scripts/run.bat` with customised `--cmd_variables`. For example:  
 
     > --cmd_variables Tool "C:\Program Files\Autodesk\Maya2017\bin\maya.exe" RenderDevice 0 TestsFilter small  
     * Tool define path to Maya  
     * RenderDevice define what hardware will be used.  
         0 - GPU (if you have more than one GPU, CPU index will be increased)  
         1 - CPU
         RenderDevice also can take "CPU", "AMD Radeon R9 200  HD 7900 Series", if this strings exist in `Device.config.json`  
     * TestsFilter takes only `small` or `full`, and define count of scenes that will be send ot render.  
