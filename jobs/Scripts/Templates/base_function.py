import maya.mel as mel
import maya.cmds as cmd
import datetime
import time
import json
import re
import os.path as path
import fireRender.rpr_material_browser

WORK_DIR = '{work_dir}'
TEST_TYPE = '{testType}'
RENDER_DEVICE = '{render_device}'
RES_PATH = '{res_path}'
PASS_LIMIT = {pass_limit}
RESOLUTION_X = {resolution_x}
RESOLUTION_Y = {resolution_y}
TEST_CASES = "{testCases}"
SPU = {SPU}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')

class RPR_report_json:
	def __init__(self, render_color_path='', render_time='', test_case='', difference_color='', test_status='', script_info=[], render_log=''):
		self.render_device = cmd.optionVar(q="RPR_DevicesName")[0]
		self.tool = mel.eval('about -iv')
		self.date_time = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
		self.render_version = mel.eval('getRPRPluginVersion()')
		self.core_version = mel.eval('getRprCoreVersion()')
		self.render_color_path = path.join("Color", "MAYA_SM_000.jpg")
		self.render_time = 0
		self.scene_name = get_scene_name()
		self.test_group = TEST_TYPE
		self.test_case = test_case
		self.difference_color = difference_color
		self.test_status = test_status
		self.script_info = script_info
		self.render_log = render_log

	def toJSON(self, path_to_file):
		with open(path_to_file, 'r') as file:
			report = json.loads(file.read())

		report["file_name"] = self.test_case + ".jpg"
		report["date_time"] = self.date_time
		report["script_info"] = self.script_info
		report["render_color_path"] = path.join("Color", report["file_name"])
		report["test_case"] = self.test_case
		report["render_version"] = self.render_version
		report["test_status"] = self.test_status
		report["tool"] = self.tool
		report["render_time"] = self.render_time
		report["scene_name"] = self.scene_name
		report["test_group"] = self.test_group
		report["difference_color"] = self.difference_color
		report["core_version"] = self.core_version
		report["render_device"] = self.render_device
		report["render_log"] = render_tool_log_path(self.test_case)

		with open(path_to_file, 'w') as file:
			file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
	return path.join(LOGS_DIR, name + ".log")


def get_scene_name():
	scene_name = cmd.file(q=True, sn=True, shn=True)
	if (scene_name == ""):
		scene_name = "untitled"
	return scene_name


def check_test_cases_fail_save(test_case, script_info):
	test = TEST_CASES
	tests = test.split(',')

	if (test != "all"):
		for test in tests:
			if test == test_case:
				rpr_fail_save(test_case, script_info)
	else:
		rpr_fail_save(test_case, script_info)



def rpr_render(test_case, script_info):
	render_device = RENDER_DEVICE
	cmd.setAttr("RadeonProRenderGlobals.samplesPerUpdate", SPU)
	cmd.optionVar(rm="RPR_DevicesSelected")

	cmd.optionVar(iva=("RPR_DevicesSelected",
					   (render_device == "gpu") | (render_device == "dual")))
	cmd.optionVar(iva=("RPR_DevicesSelected",
					   (render_device == "cpu") | (render_device == "dual")))

	cmd.setAttr("RadeonProRenderGlobals.adaptiveThreshold", 0)
	cmd.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 0)

	mel.eval('fireRender -waitForItTwo')
	start_time = time.time()
	mel.eval('renderIntoNewWindow render')
	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	test_case_path = path.join(WORK_DIR, "Color", test_case)
	cmd.renderWindowEditor('renderView', edit=1,  dst="color")
	cmd.renderWindowEditor('renderView', edit=1, com=1,
						   writeImage=test_case_path)
	test_time = time.time() - start_time

	report_JSON = path.join(WORK_DIR, (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.render_time = test_time
	report.test_case = test_case
	report.difference_color = "not compared yet"
	report.test_status = "passed"
	report.script_info = script_info

	report.toJSON(report_JSON)


def check_test_cases_success_save(test_case, script_info):
	test_cases = TEST_CASES
	tests = test_cases.split(',')
	if (test_cases != "all"):
		for test in tests:
			if (test == test_case):
				rpr_success_save(test_case, script_info)
	else:
		rpr_success_save(test_case, script_info)


def rpr_success_save(test_case, script_info):
	if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
		mel.eval('loadPlugin RadeonProRender')

	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	work_folder = path.join(WORK_DIR, "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join(WORK_DIR, "..", "..", "..",
						  "..", "jobs", "Tests", "pass.jpg"), copy=(work_folder))

	report_JSON = path.join(WORK_DIR, (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.test_case = test_case
	report.difference_color = "no compare"
	report.test_status = "passed"
	report.script_info = script_info

	report.toJSON(report_JSON)


def rpr_fail_save(test_case, script_info):
	if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
		mel.eval('loadPlugin RadeonProRender')

	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	work_folder = path.join(WORK_DIR, "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join(WORK_DIR, "..", "..", "..", "..",
						  "jobs", "Tests", "failed.jpg"), copy=(work_folder))

	report_JSON = path.join(WORK_DIR, (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.test_case = test_case
	report.difference_color = "no compare"
	report.test_status = "error"
	report.script_info = script_info

	report.toJSON(report_JSON)


def validateFiles():
	unresolved_files = cmd.filePathEditor(
		query=True, listFiles="", unresolved=True, attributeOnly=True)
	new_path = RES_PATH
	if (unresolved_files is not None):
		for item in unresolved_files:
			cmd.filePathEditor(item, repath=new_path, recursive=True, ra=1)


def check_rpr_load():
	if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
		mel.eval('loadPlugin RadeonProRender')
	if(cmd.pluginInfo('fbxmaya', query=True, loaded=True) == 0):
		mel.eval('loadPlugin fbxmaya')

	cmd.setAttr("defaultRenderGlobals.currentRenderer",
				type="string" "FireRender")


def main():

	mel.eval('setProject (\"' + RES_PATH + '\");')

	check_rpr_load()

	cmd.sysFile(LOGS_DIR, makeDir=True)

	with open(path.join(WORK_DIR, "test_cases.json"), 'r') as json_file:
		cases = json.load(json_file)

	for case in cases:
		if (case['status'] == 'active'):
			case['status'] = 'inprogress'
		if ((case['status'] == 'inprogress') | (case['status'] == 'fail')):
			with open(path.join(WORK_DIR, "test_cases.json"), 'w') as file:
				json.dump(cases, file, indent=4)

			if (not path.exists(render_tool_log_path(case['case']))):
				with open(render_tool_log_path(case['case']), 'w'):
					pass

			cmd.scriptEditorInfo(historyFilename=render_tool_log_path(
				case['case']), writeHistory=True)
			case_function(case)

			if (case['status'] == 'inprogress'):
				case['status'] = 'done'

			with open(path.join(WORK_DIR, "test_cases.json"), 'w') as file:
				json.dump(cases, file, indent=4)

	cmd.evalDeferred("maya.cmds.quit(abort=True)")
