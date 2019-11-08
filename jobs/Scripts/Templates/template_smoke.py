

def check_test_cases_fail_save(test_case, passCount, script_info, scene):
	test = TEST_CASES
	tests = test.split(',')

	if (test != "all"):
		for test in tests:
			if test == test_case:
				rpr_fail_save(test_case, script_info)
	else:
		rpr_fail_save(test_case, script_info)


def check_test_cases(test_case, passCount, script_info, scene):
	test = TEST_CASES
	tests = test.split(',')
	if (test != "all"):
		for test in tests:
			if test == test_case:
				prerender(test_case, passCount, script_info, scene)
	else:
		prerender(test_case, passCount, script_info, scene)


def prerender(test_case, passCount, script_info, scene):
	scene_name = cmd.file(q=True, sn=True, shn=True)
	if (scene_name != scene):
		if (mel.eval('catch (`file -f -options "v=0;"  -ignoreVersion -o ' + scene + '`)')):
			cmd.evalDeferred("maya.cmds.quit(abort=True)")
		else:
			cmd.setAttr("defaultRenderGlobals.imageFormat", 8)
	validateFiles()

	if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
		mel.eval('loadPlugin RadeonProRender')

	if(cmd.pluginInfo('fbxmaya', query=True, loaded=True) == 0):
		mel.eval('loadPlugin fbxmaya')

	cmd.setAttr("defaultRenderGlobals.currentRenderer",
				type="string" "FireRender")
	cmd.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", passCount)

	with open(path.join(WORK_DIR, "test_cases.json"), 'r') as json_file:
		cases = json.load(json_file)

	try:
		for case in cases:
			if (case['case'] == test_case):
				for function in case['functions']:
					if (re.match('^\w+ = ', function) is not None):
						exec(function)
					else:
						eval(function)
	except Exception as e:
		if (e.message != 'functions'):
			print('Error: ' + str(e))
		rpr_render(test_case, script_info)


def case_function(case):
	functions = {{
		0: check_test_cases,
		1: check_test_cases_success_save,
		2: check_test_cases_fail_save
	}}

	func = 0

	try:
		if (case['functions'][0] == "check_test_cases_success_save"):
			func = 1
	except:
		pass

	if (case['status'] == "fail"):
		func = 2
		case['status'] = "failed"

	try:
		pass_count = case['pass_count']
	except:
		pass_count = 50

	try:
		scene_name = case['scene']
	except:
		scene_name = ''

	functions[func](case['case'], pass_count, case['script_info'], scene_name)
