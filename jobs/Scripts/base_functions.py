import maya.mel as mel
import maya.cmds as cmds
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
SPU = {SPU}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')


def reportToJSON(case, render_time=0):
	path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')
	with open(path_to_file, 'r') as file:
		report = json.loads(file.read())[0]

	report['file_name'] = case['case'] + '.jpg'
	# TODO: render device may be incorrect (if it changes in case)
	report['render_device'] = cmds.optionVar(q='RPR_DevicesName')[0]
	report['tool'] = mel.eval('about -iv')
	report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	report['render_version'] = mel.eval('getRPRPluginVersion()')
	report['core_version'] = mel.eval('getRprCoreVersion()')
	report['render_color_path'] = path.join('Color', report['file_name'])
	report['render_time'] = render_time
	report['test_group'] = TEST_TYPE
	report['test_case'] = case['case']
	report['difference_color'] = 0
	report['script_info'] = case['script_info']
	report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
	if not get_scene_name():
		report['scene_name'] = case.get('scene', '')
	else:
		report['scene_name'] = get_scene_name()

	if case['status'] == 'inprogress':
		report['test_status'] = 'passed'
	else:
		report['test_status'] = case['status']

	with open(path_to_file, 'w') as file:
		file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
	return path.join(LOGS_DIR, name + '.log')


def get_scene_name():
	scene_name = cmds.file(q=True, sn=True, shn=True)
	if not scene_name:
		print('Problem with scene')
	return scene_name


def validateFiles():
	unresolved_files = cmds.filePathEditor(
		query=True, listFiles='', unresolved=True, attributeOnly=True)
	new_path = RES_PATH
	if unresolved_files:
		for item in unresolved_files:
			cmds.filePathEditor(item, repath=new_path, recursive=True, ra=1)


def check_rpr_load():
	if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmds.loadPlugin('RadeonProRender', quiet=True)
	if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
		cmds.loadPlugin('fbxmaya', quiet=True)


def rpr_render(case):
	render_device = RENDER_DEVICE
	cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
	cmds.optionVar(rm='RPR_DevicesSelected')

	cmds.optionVar(iva=('RPR_DevicesSelected',
						(render_device in ['gpu', 'dual'])))
	cmds.optionVar(iva=('RPR_DevicesSelected',
						(render_device in ['cpu', 'dual'])))

	cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', 0)
	cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

	mel.eval('fireRender -waitForItTwo')
	start_time = time.time()
	mel.eval('renderIntoNewWindow render')
	cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
	test_case_path = path.join(WORK_DIR, 'Color', case['case'])
	cmds.renderWindowEditor('renderView', edit=1,  dst='color')
	cmds.renderWindowEditor('renderView', edit=1, com=1,
							writeImage=test_case_path)
	test_time = time.time() - start_time

	reportToJSON(case, test_time)


def prerender(case):
	test_case = case['case']  # for call in functions in case
	script_info = case['script_info']  # for call in functions in case
	scene = case.get('scene', '')
	scene_name = cmds.file(q=True, sn=True, shn=True)
	if scene_name != scene:
		try:
			cmds.file(scene, f=True, op='v=0;', prompt=False, iv=True, o=True)
		except:
			cmds.evalDeferred('cmds.quit(abort=True)')

	validateFiles()

	check_rpr_load()

	if RESOLUTION_X and RESOLUTION_Y:
		cmds.setAttr('defaultResolution.width', RESOLUTION_X)
		cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

	cmds.setAttr('defaultRenderGlobals.currentRenderer',
				 type='string' 'FireRender')
	cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
	cmds.setAttr(
		'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)

	for function in case['functions']:
		try:
			if re.match('(^\w+ = |^print)', function):
				exec(function)
			else:
				eval(function)
		except Exception as e:
			print('Error "{{}}" with string "{{}}"'.format(e, function))


def rpr_save(case):
	cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
	work_dir = path.join(WORK_DIR, 'Color', case['case'] + '.jpg')
	source_dir = path.join(WORK_DIR, '..', '..', '..',
						   '..', 'jobs_launcher', 'common', 'img')

	if case['status'] == 'inprogress':
		cmds.sysFile(path.join(source_dir, 'passed.jpg'), copy=work_dir)
	else:
		cmds.sysFile(
			path.join(source_dir, case['status'] + '.jpg'), copy=work_dir)

	check_rpr_load()

	reportToJSON(case)


def case_function(case):
	try:
		projPath = RES_PATH + '/' + TEST_TYPE
		temp = projPath + '/' + case['scene'][:-3]
		if os.path.isdir(temp):
			projPath = temp
		mel.eval('setProject("{{}}")'.format(projPath))
	except:
		print('Can\'t set project in "' + projPath + '"')
		cmds.evalDeferred('cmds.quit(abort=True)')

	functions = {{
		'render': prerender,
		'save_report': rpr_save
	}}

	func = 'render'

	if case['functions'][0] == 'check_test_cases_success_save':
		func = 'save_report'

	if case['status'] == 'fail':
		case['status'] = 'error'
		func = 'save_report'

	functions[func](case)


def main():
	cmds.sysFile(LOGS_DIR, makeDir=True)

	with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
		cases = json.load(json_file)

	for case in cases:
		if case['status'] == 'active' or case['status'] == 'fail':
			if case['status'] == 'active':
				case['status'] = 'inprogress'

			with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
				json.dump(cases, file, indent=4)

			log_path = render_tool_log_path(case['case'])
			if not path.exists(log_path):
				with open(log_path, 'w'):
					pass
			cmds.scriptEditorInfo(historyFilename=log_path, writeHistory=True)

			print(case['case'])
			case_function(case)

			if case['status'] == 'inprogress':
				case['status'] = 'done'

			with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
				json.dump(cases, file, indent=4)

		if case['status'] == 'skipped':
			rpr_save(case)

	cmds.evalDeferred('cmds.quit(abort=True)')

#   Possible case statuses:
# - Active: Case will be executed.
# - Inprogress: Case is in progress (if maya was crashed, case will be inprogress).
# - Fail: Maya was crashed during case. Fail report will be created.
# - Error: Maya was crashed during case. Fail report is already created.
# - Done: Case was finished successfully.
# - Skipped: Case will be skipped. Skip report will be created.


