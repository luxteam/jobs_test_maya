import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
from shutil import copyfile


def get_windows_titles():
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


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--stage_report', required=True)
    parser.add_argument('--tool', required=True, metavar="<path>")
    parser.add_argument('--tests', required=True)
    parser.add_argument('--render_device', required=True)
    parser.add_argument('--output', required=True, metavar="<dir>")
    parser.add_argument('--testType', required=True)
    parser.add_argument('--template', required=True)
    parser.add_argument('--res_path', required=True)
    parser.add_argument('--pass_limit', required=True)
    parser.add_argument('--resolution_x', required=True)
    parser.add_argument('--resolution_y', required=True)
    parser.add_argument('--testCases', required=True)


    return parser


def main():
    def rewrite_stage_report():
        with open(os.path.join(args.output, args.stage_report), 'w') as file:
            json.dump(stage_report, file, indent=' ')

    args = createArgsParser().parse_args()
    stage_report = [{'status': 'INIT'}, {'log': ['Maya simpleRender.py started;']}]

    testsList = None
    script_template = None
    cmdScriptPath = None

    try:
        with open(args.tests, 'r') as file:
            testsList = file.read()
            testsList = testsList.replace("\n","")
    except OSError as e:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('OSError while read tests list. ' + str(e))
        rewrite_stage_report()
        return 1

    try:
        os.makedirs(args.output)
        # os.mkdir(os.path.join(args.output, 'Color'))
        # os.mkdir(os.path.join(args.output, 'Opacity'))
    except OSError as e:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('OSError while create folders. ' + str(e))
        rewrite_stage_report()
        return 1


    try:
        # with open(os.path.join(os.path.dirname(sys.argv[0]), 'template.mel')) as f:
        with open(os.path.join(os.path.dirname(__file__),  args.template)) as f:
            script_template = f.read()
        with open(os.path.join(os.path.dirname(__file__), "Templates", "base_function.mel")) as f:
            base = f.read()
    except OSError as e:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('OSError while read mel template. ' + str(e))
        rewrite_stage_report()
        return 1

    res_path = args.res_path
    res_path = res_path.replace('\\', '/')
    mel_template = base + script_template
    work_dir = os.path.abspath(args.output).replace('\\', '/')
    melScript = mel_template.format(work_dir=work_dir,
                                       testsList=testsList,
                                       testType=args.testType,
                                       render_device = args.render_device, res_path=res_path,
                                       pass_limit = args.pass_limit, resolution_x = args.resolution_x,
                                       resolution_y = args.resolution_y, testCases = args.testCases)

    cmdRun = '''
    set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log 
    set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
    "{tool}" -command "source script.mel; evalDeferred -lp (main());"''' \
        .format(tool=args.tool)

    try:
        with open(os.path.join(args.output, 'script.bat'), 'w') as f:
            f.write(cmdRun)
        stage_report[1]['log'].append('cmd template formatted and saved as script.bat;')

        with open(os.path.join(args.output, 'script.mel'), 'w') as f:
            f.write(melScript)
        stage_report[1]['log'].append('mel template formatted and saved as script.mel;')

    except OSError as e:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('OSError while write scripts file saving. ' + str(e))
        rewrite_stage_report()
        return 1

    os.chdir(args.output)
    p = psutil.Popen(os.path.join(args.output, 'script.bat'), stdout=subprocess.PIPE)
    stage_report[1]['log'].append('subprocess started;')
    rc = -1

    while True:
        try:
            rc = p.wait(timeout=5)
        except psutil.TimeoutExpired as err:
            fatal_errors_titles = ['maya', 'Radeon ProRender Error', 'Script Editor']
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
            break

    if rc == 0:
        print('passed')
        stage_report[0]['status'] = 'OK'
        stage_report[1]['log'].append('subprocess PASSED;')
    else:
        print('failed')
        stage_report[0]['status'] = 'TERMINATED'
        stage_report[1]['log'].append('subprocess FAILED and was TERMINATED;')

    rewrite_stage_report()
    return rc


if __name__ == "__main__":
    rc = main()
    #os.system("taskkill /f /im  DADispatcherService.exe")
    exit(rc)
