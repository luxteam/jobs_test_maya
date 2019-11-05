import maya.mel as mel
import maya.cmds as cmd
import datetime
import time
import json
import os.path as path
import fireRender.rpr_material_browser


class RPR_report_json:
	def __init__(self, file_name='', render_color_path='', render_time='', test_case='', difference_color='', test_status='', script_info=[]):
		self.render_device = cmd.optionVar(q="RPR_DevicesName")[0]
		self.tool = mel.eval('about -iv')
		self.date_time = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
		self.render_version = mel.eval('getRPRPluginVersion()')
		self.core_version = mel.eval('getRprCoreVersion()')
		self.file_name = file_name
		self.render_color_path = path.join("Color", "MAYA_SM_000.jpg")
		self.render_time = 0
		self.scene_name = get_scene_name()
		self.test_group = "{testType}"
		self.test_case = test_case
		self.difference_color = difference_color
		self.test_status = test_status
		self.script_info = script_info

	def toJSON(self, path):
		with open(path, 'r') as file:
			report = json.loads(file.read())

		report["file_name"] = self.file_name
		report["date_time"] = self.date_time
		report["script_info"] = self.script_info
		report["render_color_path"] = self.render_color_path
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
			
		with open(path, 'w') as file:
			file.write(json.dumps([report], indent=4))


def get_scene_name():
	scene_name = cmd.file(q=True, sn=True, shn=True)
	if (scene_name == ""):
		scene_name = "untitled"
	return scene_name


def rpr_render(test_case, script_info):
	render_device = "{render_device}"
	cmd.setAttr("RadeonProRenderGlobals.samplesPerUpdate", {SPU})
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
	cmd.sysFile(path.join("{work_dir}", "Color"), makeDir=True)
	test_case_path = path.join("{work_dir}", "Color", test_case)
	cmd.renderWindowEditor('renderView', edit=1,  dst="color")
	cmd.renderWindowEditor('renderView', edit=1, com=1,
						   writeImage=test_case_path)
	test_time = time.time() - start_time

	report_JSON = path.join("{work_dir}", (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.file_name = test_case + ".jpg"
	report.render_color_path = path.join("Color", report.file_name)
	report.render_time = test_time
	report.test_case = test_case
	report.difference_color = "not compared yet"
	report.test_status = "passed"
	report.script_info = script_info

	report.toJSON(report_JSON)


def check_test_cases_success_save(test_case, pass_count, script_info, scene_name):
	test_cases = "{testCases}"
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

	cmd.sysFile(path.join("{work_dir}", "Color"), makeDir=True)
	work_folder = path.join("{work_dir}", "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join("{work_dir}", "..", "..", "..",
						  "..", "jobs", "Tests", "pass.jpg"), copy=(work_folder))

	report_JSON = path.join("{work_dir}", (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.file_name = test_case + ".jpg"
	report.render_color_path = path.join("Color", report.file_name)
	report.test_case = test_case
	report.difference_color = "no compare"
	report.test_status = "passed"
	report.script_info = script_info

	report.toJSON(report_JSON)


def rpr_fail_save(test_case, script_info):
	if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
		mel.eval('loadPlugin RadeonProRender')

	cmd.sysFile(path.join("{work_dir}", "Color"), makeDir=True)
	work_folder = path.join("{work_dir}", "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join("{work_dir}", "..", "..", "..", "..",
						  "jobs", "Tests", "failed.jpg"), copy=(work_folder))

	report_JSON = path.join("{work_dir}", (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.file_name = test_case + ".jpg"
	report.render_color_path = path.join("Color", report.file_name)
	report.test_case = test_case
	report.difference_color = "no compare"
	report.test_status = "error"
	report.script_info = script_info

	report.toJSON(report_JSON)


def validateFiles():
	unresolved_files = cmd.filePathEditor(
		query=True, listFiles="", unresolved=True, attributeOnly=True)
	new_path = "{res_path}"
	if (unresolved_files is not None):
		for item in unresolved_files:
			cmd.filePathEditor(item, repath=new_path, recursive=True, ra=1)
