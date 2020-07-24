def alpha_render(case):
    event('Prerender', False, case['case'])
    logging('Render image')

    mel.eval('fireRender -waitForItTwo')
    start_time = time.time()
    mel.eval('renderIntoNewWindow render')
    cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
    test_case_path = path.join(WORK_DIR, 'Color', case['case'])
    cmds.renderWindowEditor('renderView', edit=1,  dst='color')
    mel.eval('renderWindowEditor -edit -displayStyle "mask" renderView')
    cmds.renderWindowEditor('renderView', edit=1, com=1,
                            writeImage=test_case_path)
    test_time = time.time() - start_time

    event('Postrender', True, case['case'])
    mel.eval('renderWindowEditor -edit -displayStyle "color" renderView')
    reportToJSON(case, test_time)
