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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import jobs_launcher.core.config as core_config

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

            return [x.get('kCGWindowName' u'Unknown') for x in windows_list]

        if platform.system() == 'Windows':
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
    except:
        core_config.main_logger.error("Exception has occured while pull windows titles")

    return []


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tool', required=True, metavar="<path>")
    parser.add_argument('--render_device', required=True)
    parser.add_argument('--output', required=True, metavar="<dir>")
    parser.add_argument('--testType', required=True)
    parser.add_argument('--template', required=True)
    parser.add_argument('--res_path', required=True)
    parser.add_argument('--pass_limit', required=True)
    parser.add_argument('--resolution_x', required=True)
    parser.add_argument('--resolution_y', required=True)
    parser.add_argument('--testCases', required=True)
    parser.add_argument('--SPU', required=False, default=10)

    return parser


def main(args, startFrom, lastStatus):
    
    testsList = None
    script_template = None
    cmdScriptPath = None

    try:
        with open(os.path.join(os.path.dirname(__file__), args.testCases)) as f:
            tc = f.read()
            testCases_mel = json.loads(tc)[args.testType]
    except Exception as e:
        testCases_mel = "all"
    
    try:        
        with open(os.path.join(os.path.dirname(__file__),  args.template)) as f:
            script_template = f.read()
        with open(os.path.join(os.path.dirname(__file__), "Templates", "base_function.mel")) as f:
            base = f.read()
    except OSError as e:
        return 1

    res_path = args.res_path
    res_path = res_path.replace('\\', '/')
    mel_template = base + script_template
    work_dir = os.path.abspath(args.output).replace('\\', '/')
    melScript = mel_template.format(work_dir=work_dir,
                                       testType=args.testType,
                                       render_device = args.render_device, res_path=res_path,
                                       pass_limit = args.pass_limit, resolution_x = args.resolution_x,
                                       resolution_y = args.resolution_y, testCases = testCases_mel,
                                       SPU=args.SPU)

    if lastStatus == "last_fail":
        melScript = melScript.replace("@check_test_cases", "@check_test_cases_fail_save")

    original_tests = melScript[melScript.find("<-- start -->") + 13: melScript.find("// <-- end -->")]
    modified_tests = original_tests.split("@")[startFrom:]
    replace_tests = "\n\t"
    for each in modified_tests:
        replace_tests += each + "\n\t"
    melScript = melScript.replace(original_tests, replace_tests)

    if lastStatus == "fail":
        fail_test = original_tests.split("@")[startFrom-1:startFrom]
        fail_test_ = ""
        for each in fail_test:
            each = each.replace("check_test_cases", "check_test_cases_fail_save")
            fail_test_ += each + "\n\t"
        melScript = melScript.replace("// <-- fail -->", fail_test_)

    if lastStatus == "no scene":
        fail_test = original_tests.split("@")[startFrom:]
        fail_test_ = ""
        for each in fail_test:
            each = each.replace("check_test_cases", "check_test_cases_fail_save")
            fail_test_ += each + "\n\t"
        melScript = melScript.replace("// <-- fail -->", fail_test_)

    with open(os.path.join(args.output, 'script.mel'), 'w') as file:
        file.write(melScript)

    system_pl = platform.system()
    if system_pl == 'Windows':
        cmdRun = '''
        set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log 
        set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
        "{tool}" -command "source script.mel; evalDeferred -lp (main());"''' \
            .format(tool=args.tool)

        cmdScriptPath = os.path.join(args.output, 'script.bat')
        with open(cmdScriptPath, 'w') as file:
            file.write(cmdRun)
    elif system_pl == 'Darwin':
        cmdRun = '''
        export MAYA_CMD_FILE_OUTPUT=$PWD/renderTool.log
        export MAYA_SCRIPT_PATH=$PWD:$MAYA_SCRIPT_PATH
        "{tool}" -command "source script.mel; evalDeferred -lp (main());"'''\
        .format(tool=args.tool)

        cmdScriptPath = os.path.join(args.output, 'script.sh')
        with open(cmdScriptPath, 'w') as file:
            file.write(cmdRun)
        os.system('chmod +x {}'.format(cmdScriptPath))

    os.chdir(args.output)
    p = psutil.Popen(cmdScriptPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    rc = -1

    core_config.main_logger.info("go to infinity")
    while True:
        try:
            rc = p.wait(timeout=5)
            core_config.main_logger.info("go to infinity")

        except psutil.TimeoutExpired as err:
            fatal_errors_titles = ['maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor',
                'Autodesk Maya 2017 Error Report', 'Autodesk Maya 2017 Error Report', 'Autodesk Maya 2017 Error Report']
            core_config.main_logger.info(str(fatal_errors_titles))
            core_config.main_logger.info(str(get_windows_titles()))
            if set(fatal_errors_titles).intersection(get_windows_titles()):
                rc = -1
                try:
                    error_screen = pyscreenshot.grab()
                    error_screen.save(os.path.join(args.output, 'error_screenshot.jpg'))
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


if __name__ == "__main__":

    args = createArgsParser().parse_args()

    try:
        os.makedirs(args.output)
    except OSError as e:
        pass

    def getJsonCount():
        return len(list(filter(lambda x: x.endswith('RPR.json'), os.listdir(args.output))))

    def totalCount():
        try:        
            with open(os.path.join(os.path.dirname(__file__),  args.template)) as f:
                script_template = f.read()
            return len(script_template.split("@")) - 1 # -1 because first element is "" (split)
        except OSError as e:
            return -1

    total_count = totalCount()
    fail_count = 0 
    current_test = 1 # start from 1st test
    last_status = 0 # 0 - success status
    it = 0

    while current_test <= total_count:

        it += 1

        with open(os.path.join(args.output, 'log_status.txt'), 'a') as f:
            f.write("Iter:" + str(it) + " | current test: " + str(current_test) + " | fail count: " + \
                str(fail_count) + " | last_status: " + str(last_status) + " | json: " + \
                str(getJsonCount()) + " | total count: " + str(total_count) + "\n")

        if last_status and fail_count == 3:
            rc = main(args, current_test, "fail") # Start from n+1 test. n - fail.
        elif last_status and fail_count == -1:
            rc = main(args, current_test, "last_fail") # last test - fail.
        else:
            rc = main(args, current_test, "ok") # Start from 1st test (ok - random word)

        if current_test != getJsonCount() + 1: # count to zero if failes another test
            fail_count = 0

        last_status = rc
        if not last_status: 
            if not getJsonCount():
                rc = main(args, current_test, "no scene")
            exit(rc) # finish work. 0 - success status.
        elif last_status and fail_count == 2:
            if total_count < getJsonCount() + 2: # last test failed
                fail_count = -1
                current_test = getJsonCount() + 1
            else: # not last test failed
                fail_count += 1
                current_test = getJsonCount() + 2 # mark as fail test and go to next test 
        elif last_status:
            if getJsonCount() == total_count:
                exit(rc)
            fail_count += 1 # count of failes + 1 (for current test)
            current_test = getJsonCount() + 1
    
    exit(0)
