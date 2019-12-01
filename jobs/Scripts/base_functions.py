import maya.mel as mel
import maya.cmds as cmd
import datetime
import time
import json
import re
import os.path as path
import os
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
			report = json.loads(file.read())[0]

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
		report["render_log"] = path.join('render_tool_logs', self.test_case+ ".log")

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

	if test != "all":
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
					   (render_device in ["gpu", "dual"])))
	cmd.optionVar(iva=("RPR_DevicesSelected",
					   (render_device in ["cpu", "dual"])))

	cmd.setAttr("RadeonProRenderGlobals.adaptiveThreshold", 0)
	cmd.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 0)

	mel.eval('fireRender -waitForItTwo')
	start_time = time.time()
	mel.eval('renderIntoNewWindow render')
	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	test_case_path = path.join(WORK_DIR, "Color", test_case)
	cmd.renderWindowEditor('renderView', edit=1,  dst="color")
	cmd.renderWindowEditor('renderView', edit=1, com=1, writeImage=test_case_path)
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
	if test_cases != "all":
		for test in tests:
			if test == test_case:
				rpr_success_save(test_case, script_info)
	else:
		rpr_success_save(test_case, script_info)


def rpr_success_save(test_case, script_info):
	if not cmd.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmd.loadPlugin("RadeonProRender", quiet=True)

	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	work_folder = path.join(WORK_DIR, "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join(WORK_DIR, "..", "..", "..", "..", "jobs", "Tests", "pass.jpg"), copy=(work_folder))

	report_JSON = path.join(WORK_DIR, (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.test_case = test_case
	report.difference_color = "not compared yet"
	report.test_status = "passed"
	report.script_info = script_info

	report.toJSON(report_JSON)


def rpr_fail_save(test_case, script_info):
	if not cmd.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmd.loadPlugin("RadeonProRender", quiet=True)

	cmd.sysFile(path.join(WORK_DIR, "Color"), makeDir=True)
	work_folder = path.join(WORK_DIR, "Color", (test_case + ".jpg"))
	cmd.sysFile(path.join(WORK_DIR, "..", "..", "..", "..", "jobs", "Tests", "failed.jpg"), copy=(work_folder))

	report_JSON = path.join(WORK_DIR, (test_case + "_RPR.json"))

	report = RPR_report_json()
	report.test_case = test_case
	report.difference_color = "not compared yet"
	report.test_status = "error"
	report.script_info = script_info

	report.toJSON(report_JSON)


def validateFiles():
	unresolved_files = cmd.filePathEditor(query=True, listFiles="", unresolved=True, attributeOnly=True)
	new_path = RES_PATH
	if unresolved_files:
		for item in unresolved_files:
			cmd.filePathEditor(item, repath=new_path, recursive=True, ra=1)


def check_rpr_load():
	if not cmd.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmd.loadPlugin("RadeonProRender", quiet=True)
	if not cmd.pluginInfo('fbxmaya', query=True, loaded=True):
		cmd.loadPlugin("fbxmaya", quiet=True)


def prerender(test_case, script_info, scene):
	scene_name = cmd.file(q=True, sn=True, shn=True)
	if scene_name != scene:
		try:
			cmd.file(scene, f=True, op='v=0;', iv=True, o=True)
		except:
			cmd.evalDeferred(cmd.quit(abort=True))

	validateFiles()

	if not cmd.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmd.loadPlugin("RadeonProRender", quiet=True)
	if not cmd.pluginInfo('fbxmaya', query=True, loaded=True):
		cmd.loadPlugin("fbxmaya", quiet=True)

	if RESOLUTION_X and RESOLUTION_Y:
		cmd.setAttr("defaultResolution.width", RESOLUTION_X)
		cmd.setAttr("defaultResolution.height", RESOLUTION_Y)

	cmd.setAttr("defaultRenderGlobals.currentRenderer", type="string" "FireRender")
	cmd.setAttr("defaultRenderGlobals.imageFormat", 8)
	# TODO 
	cmd.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", PASS_LIMIT)

	with open(path.join(WORK_DIR, "test_cases.json"), 'r') as json_file:
		cases = json.load(json_file)

	for case in cases:
		if case['case'] == test_case:
			try:
				for function in case['functions']:
					try:
						if re.match('(^\w+ = |^print)', function):
							exec(function)
						else:
							eval(function)
					except Exception as e:
						print('Error {{}} with string {{}}'.format(e, function))
			except Exception as e:
				rpr_render(test_case, script_info)


def check_test_cases(test_case, script_info, scene):
	test = TEST_CASES
	tests = test.split(',')
	if test != "all":
		for test in tests:
			if test == test_case:
				prerender(test_case, script_info, scene)
	else:
		prerender(test_case, script_info, scene)


def case_function(case):
	functions = {{
		0: check_test_cases,
		1: check_test_cases_success_save,
		2: check_test_cases_fail_save
	}}

	func = 0

	try:
		if case['functions'][0] == "check_test_cases_success_save":
			func = 1
	except:
		pass

	if case['status'] == "fail":
		func = 2
		case['status'] = "error"

	try:
		scene_name = case['scene']
	except:
		scene_name = ''

	if not func:
		functions[func](case['case'], case['script_info'], scene_name)
	else:
		functions[func](case['case'], case['script_info'])


def main():

	mel.eval('setProject(\"{{}}\")'.format(RES_PATH))

	check_rpr_load()

	cmd.sysFile(LOGS_DIR, makeDir=True)

	with open(path.join(WORK_DIR, "test_cases.json"), 'r') as json_file:
		cases = json.load(json_file)

	#   Possible case statuses:
	# - Active: Case will be executed.
	# - Inprogress: Case is in progress (if maya was crashed, case will be inprogress).
	# - Fail: Maya was crashed during case. Fail report will be created.
	# - Error: Maya was crashed during case. Fail report is already created.
	# - Done: Case was finished successfully.
	# - Skipped: Case will be skipped. Skip report will be created.

	for case in cases:
		if case['status'] == 'active':
			case['status'] = 'inprogress'
		if case['status'] == 'inprogress' or case['status'] == 'fail':
			with open(path.join(WORK_DIR, "test_cases.json"), 'w') as file:
				json.dump(cases, file, indent=4)

			if not path.exists(render_tool_log_path(case['case'])):
				with open(render_tool_log_path(case['case']), 'w'):
					pass

			cmd.scriptEditorInfo(historyFilename=render_tool_log_path(case['case']), writeHistory=True)
			print(case['case'])
			case_function(case)

			if case['status'] == 'inprogress':
				case['status'] = 'done'

			with open(path.join(WORK_DIR, "test_cases.json"), 'w') as file:
				json.dump(cases, file, indent=4)

	cmd.evalDeferred(cmd.quit(abort=True))


def setAttribute(attr, value):
	file = cmd.shadingNode("file", asTexture=True, isColorManaged=True)
	texture = cmd.shadingNode("place2dTexture", asUtility=True)
	cmd.connectAttr(texture + ".coverage", file + ".coverage", f=True)
	cmd.connectAttr(texture + ".translateFrame", file + ".translateFrame", f=True)
	cmd.connectAttr(texture + ".rotateFrame", file + ".rotateFrame", f=True)
	cmd.connectAttr(texture + ".mirrorU", file + ".mirrorU", f=True)
	cmd.connectAttr(texture + ".mirrorV", file + ".mirrorV", f=True)
	cmd.connectAttr(texture + ".stagger", file + ".stagger", f=True)
	cmd.connectAttr(texture + ".wrapU", file + ".wrapU", f=True)
	cmd.connectAttr(texture + ".wrapV", file + ".wrapV", f=True)
	cmd.connectAttr(texture + ".repeatUV", file + ".repeatUV", f=True)
	cmd.connectAttr(texture + ".offset", file + ".offset", f=True)
	cmd.connectAttr(texture + ".rotateUV", file + ".rotateUV", f=True)
	cmd.connectAttr(texture + ".noiseUV", file + ".noiseUV", f=True)
	cmd.connectAttr(texture + ".vertexUvTwo", file + ".vertexUvTwo" , f=True)
	cmd.connectAttr(texture + ".vertexUvThree", file + ".vertexUvThree", f=True)
	cmd.connectAttr(texture + ".vertexCameraOne", file + ".vertexCameraOne", f=True)
	cmd.connectAttr(texture + ".outUV", file + ".uv", f=True)
	cmd.connectAttr(texture + ".outUvFilterSize", file + ".uvFilterSize")
	cmd.connectAttr(texture + ".vertexUvOne", file + ".vertexUvOne")

	return file


def setAttributeSS(attr, value):
	file = setAttribute(attr, value)
	cmd.connectAttr(file + ".outColor", "RPRSkyShape." + attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file


def removeEnvironment():
	objects = cmd.ls(g=True)
	for obj in objects:
		if cmd.objectType(obj) in ('RPRIBL', 'RPRSky'):
			transform = cmd.listRelatives(obj, p=True)[0]
			cmd.delete(transform)	


def resetAttributesV():
	cmd.setAttr('RPRVolumeMaterial1.scatterColor', 1, 1, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.transmissionColor', 1, 1, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.emissionColor', 1, 0, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.density', 0.5)
	cmd.setAttr('RPRVolumeMaterial1.scatteringDirection', 0.096)
	cmd.setAttr('RPRVolumeMaterial1.multiscatter', 1)


def setAttributeV(volume_attr, file_attr, value):
	file = setAttribute(volume_attr, value)
	cmd.connectAttr(file + "." + file_attr, "RPRVolumeMaterial1." + volume_attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file


def setAttributePBR(pbr_attr, file_attr, value):
	file = setAttribute(pbr_attr, value)
	cmd.connectAttr(file + "." + file_attr, "R_PBRMat." + pbr_attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file


def resetAttributePBR():
	cmd.setAttr('R_PBRMat.color', 0.0719, 0.31, 0.0719, type='double3')
	cmd.setAttr('R_PBRMat.metalness', 0)
	cmd.setAttr('R_PBRMat.specular', 1)
	cmd.setAttr('R_PBRMat.roughness', 0.1)
	try:
		cmd.connectAttr('RPRNormal4.out', 'R_PBRMat.normalMap', f=True)
	except:
		pass
	cmd.setAttr('file14.fileTextureName', 'sourceimages/normal.tif', type='string' )
	cmd.setAttr('R_PBRMat.glass', 1)
	cmd.setAttr('R_PBRMat.glassIOR', 1.2)
	cmd.setAttr('R_PBRMat.emissiveColor', 0.5, 0.5, 0.5, type='double3')
	cmd.setAttr('R_PBRMat.emissiveWeight', 0)
	cmd.setAttr('R_PBRMat.subsurfaceWeight', 0)
	cmd.setAttr('R_PBRMat.subsurfaceColor', 0.436, 0.227, 0.131, type='double3')
	cmd.setAttr('R_PBRMat.subsurfaceRadius0', 3.67)
	cmd.setAttr('R_PBRMat.subsurfaceRadius1', 1.37)
	cmd.setAttr('R_PBRMat.subsurfaceRadius2', 0.68)


def setAttributeU(pbr_attr, file_attr, value):  # for Uber
	file = setAttribute(pbr_attr, value)
	cmd.connectAttr(file + "." + file_attr, "R_UberMat." + pbr_attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file


def resetAttributeU():
	cmd.setAttr('R_UberMat.diffuse', 1)
	cmd.setAttr('R_UberMat.diffuseColor', 0.05285, 0.298014, 0.303, type='double3')
	cmd.setAttr('R_UberMat.diffuseWeight', 1)
	cmd.setAttr('R_UberMat.diffuseRoughness', 1)
	cmd.setAttr('R_UberMat.useShaderNormal', 1)
	cmd.setAttr('R_UberMat.diffuseNormal', 1, 1, 1, type='double3')
	cmd.setAttr('R_UberMat.backscatteringWeight', 0)
	cmd.setAttr('R_UberMat.separateBackscatterColor', 0)
	cmd.setAttr('R_UberMat.backscatteringColor', 0.5, 0.5, 0.5, type='double3')

	cmd.setAttr('R_UberMat.reflections', 1)
	cmd.setAttr('R_UberMat.reflectColor', 1, 1, 1, type='double3')
	cmd.setAttr('R_UberMat.reflectWeight', 1)
	cmd.setAttr('R_UberMat.reflectRoughness', 0.119)
	cmd.setAttr('R_UberMat.reflectAnisotropy', 0)
	cmd.setAttr('R_UberMat.reflectAnisotropyRotation', 0)
	cmd.setAttr('R_UberMat.reflectUseShaderNormal', 1)
	cmd.setAttr('R_UberMat.reflectNormal', 1, 1, 1, type='double3')

	cmd.setAttr('R_UberMat.reflectMetalMaterial', 0)
	cmd.setAttr('R_UberMat.reflectIOR', 1.5)
	cmd.setAttr('R_UberMat.reflectMetalness', 0)

	cmd.setAttr('R_UberMat.refraction', 1)
	cmd.setAttr('R_UberMat.refractColor', 0.22, 0.957, 0.794, type='double3')
	cmd.setAttr('R_UberMat.refractWeight', 1)
	cmd.setAttr('R_UberMat.refractRoughness', 0)
	cmd.setAttr('R_UberMat.refractLinkToReflect', 0)
	cmd.setAttr('R_UberMat.refractIor', 1.5)
	cmd.setAttr('R_UberMat.refractThinSurface', 0)
	cmd.setAttr('R_UberMat.refractAbsorptionDistance', 0)
	cmd.setAttr('R_UberMat.refractAbsorbColor', 0, 0, 0, type='double3')
	cmd.setAttr('R_UberMat.refractAllowCaustics', 1)

	cmd.setAttr('R_UberMat.clearCoat', 0)
	cmd.setAttr('R_UberMat.coatColor', 1, 1, 1, type='double3')
	cmd.setAttr('R_UberMat.coatWeight', 1)
	cmd.setAttr('R_UberMat.coatRoughness', 0.5)
	cmd.setAttr('R_UberMat.coatIor', 1.5)
	cmd.setAttr('R_UberMat.coatUseShaderNormal', 0)
	cmd.setAttr('R_UberMat.coatNormal', 1, 1, 1, type='double3')
	cmd.setAttr('R_UberMat.coatThickness', 1)
	cmd.setAttr('R_UberMat.coatTransmissionColor', 1, 1, 1, type='double3')

	cmd.setAttr('R_UberMat.emissive', 0)
	cmd.setAttr('R_UberMat.emissiveWeight', 1)
	cmd.setAttr('R_UberMat.emissiveColor', 1, 1, 1, type='double3')
	cmd.setAttr('R_UberMat.emissiveIntensity', 1)
	cmd.setAttr('R_UberMat.emissiveDoubleSided', 0)

	cmd.setAttr('R_UberMat.sssEnable', 0)
	cmd.setAttr('R_UberMat.sssWeight')
	cmd.setAttr('R_UberMat.sssUseDiffuseColor', 0)
	cmd.setAttr('R_UberMat.volumeScatter', 0.436, 0.227, 0.131, type='double3')
	cmd.setAttr('R_UberMat.subsurfaceRadius0', 3.67)
	cmd.setAttr('R_UberMat.subsurfaceRadius1', 1.37)
	cmd.setAttr('R_UberMat.subsurfaceRadius2', 0.68)
	cmd.setAttr('R_UberMat.scatteringDirection', 0)
	cmd.setAttr('R_UberMat.multipleScattering', 1)

	cmd.setAttr('R_UberMat.transparencyEnable', 0)
	cmd.setAttr('R_UberMat.transparencyLevel', 1)
	cmd.setAttr('R_UberMat.normalMapEnable', 1)

	try:
		cmd.connectAttr('RPRNormal3.out', 'R_UberMat.normalMap', force=True)
	except:
		pass

	cmd.setAttr('file13.fileTextureName', 'sourceimages/normal_normalmap.png', type='string')
	cmd.setAttr('R_UberMat.displacementEnable', 0)
	cmd.setAttr('R_UberMat.displacementMap', 0, 0, 0, type='double3')
	cmd.setAttr('R_UberMat.displacementMin', 13.986)
	cmd.setAttr('R_UberMat.displacementMax', 23.776)
	cmd.setAttr('R_UberMat.displacementSubdiv', 4)
	cmd.setAttr('R_UberMat.displacementCreaseWeight', 0)
	cmd.setAttr('R_UberMat.displacementBoundary', 1)


def resetAttributesQ():
	cmd.setAttr('RadeonProRenderGlobals.maxRayDepth', 8)
	cmd.setAttr('RadeonProRenderGlobals.maxDepthDiffuse', 3)
	cmd.setAttr('RadeonProRenderGlobals.maxDepthGlossy', 5)
	cmd.setAttr('RadeonProRenderGlobals.maxDepthRefraction', 5)
	cmd.setAttr('RadeonProRenderGlobals.maxDepthRefractionGlossy', 5)
	cmd.setAttr('RadeonProRenderGlobals.maxDepthShadow', 5)
	cmd.setAttr('RadeonProRenderGlobals.raycastEpsilon', 0.02)
	cmd.setAttr('RadeonProRenderGlobals.enableOOC', 0)
	cmd.setAttr('RadeonProRenderGlobals.textureCacheSize', 512)


def ibl():
	exist = 0		
	objects = cmd.ls(g=True)
	for obj in objects:
		if obj == 'RPRIBLShape':
			exist = 1
	if exist == 0:
		ibl_shape = cmd.createNode('RPRIBL', n='RPRIBLShape')
		ibl_transform = cmd.listRelatives(ibl_shape, p=True)[0]
		cmd.setAttr(ibl_transform + '.scale', 1001.25663706144, 1001.25663706144, 1001.25663706144)