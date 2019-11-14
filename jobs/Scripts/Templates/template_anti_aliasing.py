

def prerender(test_case, filterAA, filter_size, script_info, scene):
    scene_name = cmd.file(q=True, sn=True, shn=True)
    if (scene_name != scene):
        if (mel.eval('catch (`file -f -options "v=0;"  -ignoreVersion -o ' + scene + '`)')):
            cmd.evalDeferred("maya.cmds.quit(abort=True)")
        validateFiles()

    if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
        mel.eval('loadPlugin RadeonProRender')

    if (RESOLUTION_X & RESOLUTION_Y):
        cmd.setAttr("defaultResolution.width", RESOLUTION_X)
        cmd.setAttr("defaultResolution.height", RESOLUTION_Y)

    cmd.setAttr("defaultRenderGlobals.currentRenderer",
                type="string" "FireRender")
    cmd.setAttr("defaultRenderGlobals.imageFormat", 8)
    cmd.setAttr(
        "RadeonProRenderGlobals.completionCriteriaIterations", PASS_LIMIT)

    cmd.setAttr("RadeonProRenderGlobals.filter", filterAA)
    cmd.setAttr("RadeonProRenderGlobals.filterSize", filter_size)

    rpr_render(test_case, script_info)


def check_test_cases(test_case, filterAA, filter_size, script_info, scene):
    test = TEST_CASES
    tests = test.split(',')
    if (test != "all"):
        for test in tests:
            if test == test_case:
                prerender(test_case, filterAA, filter_size, script_info, scene)
    else:
        prerender(test_case, filterAA, filter_size, script_info, scene)


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

    scene_name = case['scene']

    if (func == 0):
        functions[func](case['case'], case['filter'],
                        case['filter_size'], case['script_info'], scene_name)
    else:
        functions[func](case['case'], case['script_info'])
