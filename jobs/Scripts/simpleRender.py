import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
import platform
from shutil import copyfile
import sys
import re
import time
import platform

sys.path.append(os.path.abspath(os.path.join(
	os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

import jobs_launcher.core.config as core_config
from jobs_launcher.core.kill_process import kill_process

PROCESS = ['Maya', 'maya.exe']


if platform.system() == 'Darwin':
	# from PyObjCTools import AppHelper
	# import objc
	# from objc import super
	from Cocoa import NSWorkspace
	# from AppKit import NSWorkspace
	from Quartz import CGWindowListCopyWindowInfo
	from Quartz import kCGWindowListOptionOnScreenOnly
	from Quartz import kCGNullWindowID
	from Quartz import kCGWindowName


def get_windows_titles():
	try:
		if platform.system() == 'Darwin':
			ws_options = kCGWindowListOptionOnScreenOnly
			windows_list = CGWindowListCopyWindowInfo(ws_options, kCGNullWindowID)
			maya_titles = {x.get('kCGWindowName', u'Unknown') for x in windows_list if 'Maya' in x['kCGWindowOwnerName']}

			# duct tape for windows with empty title
			expected = {'Maya', 'Render View', 'Rendering...'}
			if maya_titles - expected:
				maya_titles.add('Radeon ProRender Error')

			return list(maya_titles)

		elif platform.system() == 'Windows':
			EnumWindows = ctypes.windll.user32.EnumWindows
			EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
			GetWindowText = ctypes.windll.user32.GetWindowTextW
			GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
			IsWindowVisible = ctypes.windll.user32.IsWindowVisible

			titles = []

			def foreach_window(hwnd, lParam):
				if IsWindowVisible(hwnd):
					length = GetWindowTextLength(hwnd)
					buff = ctypes.create_unicode_buffer(length + 1)
					GetWindowText(hwnd, buff, length + 1)
					titles.append(buff.value)
				return True

			EnumWindows(EnumWindowsProc(foreach_window), 0)

			return titles
	except Exception as err:
		core_config.main_logger.error("Exception has occurred while pull windows titles: {}".format(str(err)))

	return []


def createArgsParser():
	parser = argparse.ArgumentParser()

	parser.add_argument('--tool', required=True, metavar="<path>")
	parser.add_argument('--render_device', required=True)
	parser.add_argument('--output', required=True, metavar="<dir>")
	parser.add_argument('--testType', required=True)
	parser.add_argument('--res_path', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--resolution_x', required=True)
	parser.add_argument('--resolution_y', required=True)
	parser.add_argument('--testCases', required=True)
	parser.add_argument('--SPU', required=False, default=10)
	parser.add_argument('--fail_count', required=False, default=0, type=int)

	return parser


def check_licenses(res_path, maya_scenes):
	for scene in maya_scenes:
		with open(os.path.join(res_path, scene[:-1])) as f:
			scene_file = f.read()

		license = "fileInfo \"license\" \"student\";"
		scene_file = scene_file.replace(license, '')

		with open(os.path.join(res_path, scene[:-1]), "w") as f:
			f.write(scene_file)


def main(args):
	testsList = None
	script_template = None
	cmdScriptPath = None

	core_config.main_logger.info('Make script')

	try:
		with open(os.path.join(os.path.dirname(__file__), args.testCases)) as f:
			tc = f.read()
			testCases_mel = json.loads(tc)[args.testType]
	except Exception as e:
		testCases_mel = "all"

	try:
		with open(os.path.realpath(os.path.join(os.path.dirname(__file__),  '..', 'Tests', args.testType, 'test_cases.json'))) as f:
			script_template = f.read()
		with open(os.path.join(os.path.dirname(__file__), "base_functions.py")) as f:
			script = f.read()
	except OSError as e:
		core_config.main_logger.error(str(e))
		return 1

	maya_scenes = set(re.findall(r"\w*\.ma\"", script_template))
	check_licenses(args.res_path, maya_scenes)

	res_path = args.res_path
	res_path = res_path.replace('\\', '/')
	work_dir = os.path.abspath(args.output).replace('\\', '/')
	melScript = script.format(work_dir=work_dir, testType=args.testType, render_device=args.render_device, res_path=res_path, pass_limit=args.pass_limit, 
							  resolution_x=args.resolution_x, resolution_y=args.resolution_y, testCases=testCases_mel, SPU=args.SPU)

	with open(os.path.join(args.output, 'base_functions.py'), 'w') as file:
		file.write(melScript)

	try:
		cases = json.load(open(os.path.realpath(
			os.path.join(work_dir, 'test_cases.json'))))
	except:
		cases = json.load(open(os.path.realpath(os.path.join(os.path.dirname(__file__),  '..', 'Tests', args.testType, 'test_cases.json'))))

	temp = []
	if testCases_mel != "all":
		for case in cases:
			if case['case'] in testCases_mel:
				temp.append(case)
		cases = temp

	active_cases_default_tool = 0
	for case in cases:
		if (case['status'] not in ['error', 'skipped', 'done']):
			try:
				tool = case['tool']
			except:
				active_cases_default_tool += 1
			else: 
				case['status'] = 'need another tool'
	if (active_cases_default_tool == 0):
		for case in cases:
			if (case['status'] == 'need another tool'):
				case['status'] = 'active'
				args.tool = case['tool']

	for case in cases:
		try:
			if ((args.render_device in case['skip on']) or ([a for a in list(platform.architecture()) if a in case['skip on']])):
				case['status'] = 'skipped'
		except:pass

	core_config.main_logger.info('Create empty report files')

	for case in cases:
		if case['status'] != 'done':
			if case["status"] == 'inprogress':
				case['status'] = 'fail'

			template = core_config.RENDER_REPORT_BASE
			template["test_case"] = case["case"]
			template["test_status"] = case["status"]

			try:
				template["scene_name"] = case["scene"]
			except:
				pass
				
			template["script_info"] = case["script_info"]
			with open(os.path.join(work_dir, case['case'] + core_config.CASE_REPORT_SUFFIX), 'w') as f:
				f.write(json.dumps([template], indent=4))

	with open(os.path.join(work_dir, 'test_cases.json'), "w+") as f:
		json.dump(cases, f, indent=4)

	system_pl = platform.system()
	if system_pl == 'Windows':
		cmdRun = '''
		  set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log 
		  set PYTHONPATH=%cd%;PYTHONPATH
		  set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
		  "{tool}" -command "python(\\"import base_functions\\"); python(\\"base_functions.main()\\");"
		'''.format(tool=args.tool)

		cmdScriptPath = os.path.join(args.output, 'script.bat')
		with open(cmdScriptPath, 'w') as file:
			file.write(cmdRun)

	elif system_pl == 'Darwin':
		cmdRun = '''
		  export MAYA_CMD_FILE_OUTPUT=$PWD/renderTool.log
		  export PYTHONPATH=$PWD:$PYTHONPATH
		  export MAYA_SCRIPT_PATH=$PWD:$MAYA_SCRIPT_PATH
		  "{tool}" -command "python(\\"import base_functions\\"); python(\\"base_functions.main()\\");"
		'''.format(tool=args.tool)

		cmdScriptPath = os.path.join(args.output, 'script.sh')
		with open(cmdScriptPath, 'w') as file:
			file.write(cmdRun)
		os.system('chmod +x {}'.format(cmdScriptPath))

	core_config.main_logger.info('Try to run run.* file')

	os.chdir(args.output)
	p = psutil.Popen(cmdScriptPath, stdout=subprocess.PIPE,
					 stderr=subprocess.PIPE, shell=True)
	rc = -1

	while True:
		try:
			rc = p.communicate(timeout=40)

		except (psutil.TimeoutExpired, subprocess.TimeoutExpired) as err:
			fatal_errors_titles = ['maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor',
								   'Autodesk Maya 2017 Error Report', 'Autodesk Maya 2017 Error Report', 'Autodesk Maya 2017 Error Report',
								   'Autodesk Maya 2018 Error Report', 'Autodesk Maya 2018 Error Report', 'Autodesk Maya 2018 Error Report',
								   'Autodesk Maya 2019 Error Report', 'Autodesk Maya 2019 Error Report', 'Autodesk Maya 2019 Error Report']

			fatal_window = [window for window in fatal_errors_titles if window in set(
				get_windows_titles())]

			if (fatal_window):
				core_config.main_logger.error(
					'Fatal window found: ' + str(fatal_window))
				rc = -1
				try:
					error_screen = pyscreenshot.grab()
					error_screen.save(os.path.join(
						args.output, 'error_screenshot.jpg'))
				except:
					pass
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()
				break
		else:
			rc = 0
			break

	return rc


def group_failed(args):
	try:
		cases = json.load(open(os.path.realpath(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
	except:
		cases = json.load(open(os.path.realpath(os.path.join(os.path.dirname(__file__),  '..', 'Tests', args.testType, 'test_cases.json'))))

	for case in cases:
		if case['status'] == 'active':
			case['status'] = 'skipped'

	with open(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'), "w+") as f:
		json.dump(cases, f, indent=4)

	rc = main(args)
	exit(rc)


if __name__ == "__main__":
	i = 0

	args = createArgsParser().parse_args()

	try:
		os.makedirs(args.output)
	except OSError as e:
		pass

	while True:
		i += 1
		core_config.main_logger.info('Iteration: ' + str(i))
		rc = main(args)

		try:
			cases = json.load(open(os.path.realpath(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
		except:
			cases = json.load(open(os.path.realpath(os.path.join(os.path.dirname(__file__),  '..', 'Tests', args.testType, 'test_cases.json'))))

		active_cases = 0
		failed_count = 0

		for case in cases:
			if case['status'] not in ['skipped']:
				if case['status'] in ['fail', 'error', 'inprogress']:
					failed_count += 1
					if args.fail_count == failed_count:
						group_failed(args)
				else:
					failed_count = 0

				if case['status'] in ['active', 'fail', 'inprogress', 'need another tool']:
					active_cases += 1

		if active_cases == 0:
			exit()
