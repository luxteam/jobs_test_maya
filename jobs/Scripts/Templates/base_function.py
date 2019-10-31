import maya.mel as mel
import maya.cmds as cmd
import datetime
import time
import json
import fireRender.rpr_material_browser
import unicodedata


class RPR_report_json:
    def __init__(self, render_device = '', file_name = '', render_color_path = '', render_time = '', scene_name = '', test_group = '', test_case = '', difference_color = '', test_status = '', script_info = ''):
        self.render_device = render_device
        self.tool = mel.eval('about -version')
        self.date_time = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        self.render_version = mel.eval('getRPRPluginVersion()')
        self.core_version = mel.eval('getRprCoreVersion()')
        self.file_name = file_name
        self.render_color_path = "Color/MAYA_SM_000.jpg"
        self.render_time = 0
        self.scene_name = scene_name
        self.test_group = test_group
        self.test_case = test_case
        self.difference_color = difference_color
        self.test_status = test_status
        self.script_info = script_info

    def toJSON(self):
        json.dumps(self)


def rpr_render(test_case, script_info):
    render_device = "{render_device}"
    cmd.setAttr("RadeonProRenderGlobals.samplesPerUpdate", {SPU})
    cmd.optionVar(rm="RPR_DevicesSelected")
    if (render_device == "gpu"):
        cmd.optionVar(iva=("RPR_DevicesSelected", 1))
        cmd.optionVar(iva=("RPR_DevicesSelected", 0))
    elif (render_device == "cpu"):
        cmd.optionVar(iva=("RPR_DevicesSelected", 0))
        cmd.optionVar(iva=("RPR_DevicesSelected", 1))
    elif (render_device == "dual"):
        cmd.optionVar(iva=("RPR_DevicesSelected", 1))
        cmd.optionVar(iva=("RPR_DevicesSelected", 1))

    cmd.setAttr("RadeonProRenderGlobals.adaptiveThreshold", 0)
    cmd.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 0)

    startTime = 0
    testTime = 0
    mel.eval('fireRender -waitForItTwo')
    startTime = time.time()
    mel.eval('renderIntoNewWindow render')
    cmd.sysFile(("{work_dir}" + "/Color"), makeDir=True)
    ff = "{work_dir}" + "/Color/" + test_case
    cmd.renderWindowEditor('renderView', edit=1,  dst="color")
    cmd.renderWindowEditor('renderView', edit=1, com=1, writeImage=ff)
    testTime = time.time() - startTime

    scene_name = cmd.file(q=True, sn=True, shn=True)
    if (scene_name == ""):
        scene_name = "untitled"

    render_device_name = cmd.optionVar(q="RPR_DevicesName")
    filePath = "{work_dir}" + "/" + test_case + "_RPR.json"

    report = RPR_report_json()
    report.render_device = render_device_name
    report.file_name = test_case + ".jpg"
    report.render_color_path = "Color/" + test_case + ".jpg"
    report.render_time = testTime
    report.scene_name = scene_name
    report.test_group = "{testType}"
    report.test_case = test_case
    report.difference_color = "not compared yet"
    report.test_status = "passed"
    report.script_info = script_info

    f = open(filePath, 'a')
    f.write(report.toJSON())
    f.close


def check_test_cases_success_save(test_case, script_info):
    test = "{testCases}"
    tests = test.split(',')
    if (test != "all"):
        for test in tests:
            if (test == test_case):
                rpr_success_save(test_case, script_info)
    else:
        rpr_success_save(test_case, script_info)


def rpr_success_save(test_case, script_info):
    if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
        mel.eval('loadPlugin RadeonProRender')

    cmd.sysFile(("{work_dir}" + "/Color"), makeDir=True)
    work_folder = "{work_dir}/Color/" + test_case + ".jpg"
    cmd.sysFile(("{work_dir}" + "/../../../../jobs/Tests/pass.jpg"), copy=(work_folder))

    scene_name = cmd.file(q=True, sn=True, shn=True)
    if (scene_name == ""):
        scene_name = "untitled"

    render_device_name = cmd.optionVar(q="RPR_DevicesName")
    filePath = "{work_dir}" + "/" + test_case + "_RPR.json"

    report = RPR_report_json()
    report.render_device = render_device_name
    report.file_name = test_case + ".jpg"
    report.render_color_path = "Color/" + test_case + ".jpg"
    report.scene_name = scene_name
    report.test_group = "{testType}"
    report.test_case = test_case
    report.difference_color = "no compare"
    report.test_status = "passed"
    report.script_info = script_info

    f = open(filePath, 'a')
    f.write(report.toJSON())
    f.close


def rpr_fail_save(test_case, script_info):
    if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
        mel.eval('loadPlugin RadeonProRender')

    cmd.sysFile(("{work_dir}" + "/Color"), makeDir=True)
    work_folder = "{work_dir}/Color/" + test_case + ".jpg"
    cmd.sysFile(("{work_dir}" + "/../../../../jobs/Tests/failed.jpg"), copy=(work_folder))
    scene_name = cmd.file(q=True, sn=True, shn=True)
    if (scene_name == ""):
        scene_name = "untitled"

    render_device_name = cmd.optionVar(q="RPR_DevicesName")
    filePath = "{work_dir}" + "/" + test_case + "_RPR.json"

    report = RPR_report_json()
    report.render_device = render_device_name
    report.file_name = test_case + ".jpg"
    report.render_color_path = "Color/" + test_case + ".jpg"
    report.scene_name = scene_name
    report.test_group = "{testType}"
    report.test_case = test_case
    report.difference_color = "no compare"
    report.test_status = "error"
    report.script_info = script_info

    f = open(filePath, 'a')
    f.write(report.toJSON())
    f.close


def validateFiles():
    unresolved_files = cmd.filePathEditor(
        query=True, listFiles="", unresolved=True, attributeOnly=True)
    new_path = "{res_path}"
    if (unresolved_files is not None):
        for item in unresolved_files:
            cmd.filePathEditor(item, repath=new_path, recursive=True, ra=1)
