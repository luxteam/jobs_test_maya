import os
import maya.cmds as cmds
import maya.mel as mel
import datetime
import json


def rpr_render(scene):
    cmds.optionVar(rm="RPR_DevicesSelected")
    cmds.optionVar(iva=("RPR_DevicesSelected", 1))

    cmds.fireRender(waitForItTwo=True)

    TIMER = datetime.datetime.now()
    mel.eval("renderIntoNewWindow render")
    output = os.path.join("{work_dir}", "Color", scene)
    cmds.renderWindowEditor("renderView", edit=True, dst="color")
    cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)
    Render_time = datetime.datetime.now() - TIMER

    return Render_time


def prerender(scene, rpr_iter):
    scene_name = cmds.file(q=True, sn=True, shn=True)
    test_status = "passed"

    print("\n\n--------\n")
    print("Processing: " + scene_name + "\n")

    try:
        cmds.file(os.path.join('scenes', scene), f=True, options="v=0;", ignoreVersion=True, o=True)
    except Exception as err:
        print("[ERROR] Failed to open scene: {{}}\n".format(str(err)))
        return -1

    if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
        print("Loading RPR plugin ....\n")
        cmds.loadPlugin("RadeonProRender")

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
    cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", rpr_iter)

    Render_time = rpr_render(scene)
    print("Render finished.\n")
    print("--------\n")

    try:
        print("Try to export scene as RPR GLTF\n")
        mel.eval("""file -force -options "" -type "RPR GLTF" -pr -ea "{work_dir}/""" + scene + """.gltf";""")
    except Exception as err:
        print("[ERROR] Failed to open scene: {{}}\n".format(str(err)))
        test_status = "error"

    RENDER_REPORT_BASE = {{
        "file_name": scene + ".jpg",
        "date_time": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
        "script_info": [],
        "render_color_path": "Color/" + scene + ".jpg",
        "test_case": scene,
        "render_version": mel.eval("getRPRPluginVersion()"),
        "core_version": mel.eval("getRprCoreVersion()"),
        "test_status": test_status,
        "tool": "Maya " + cmds.about(version=True),
        "render_time": Render_time.total_seconds(),
        "baseline_render_time": -0.0,
        "render_mode": "gpu",
        "scene_name": scene,
        "test_group": "{test_group}",
        "difference_color": "not compared yet",
        "render_device": cmds.optionVar(q="RPR_DevicesName")[0]
    }}

    filePath = "{work_dir}/" + scene + "_RPR.json"

    with open(filePath, 'w') as file:
        json.dump([RENDER_REPORT_BASE], file, indent=4)


def main():
    mel.eval("setProject(\"{res_path}\")")
    tests = {tests}
    for each in tests:
        prerender(each, 200)

    cmds.evalDeferred(cmds.quit(abort=True))
