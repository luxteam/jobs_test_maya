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
    parser.add_argument('--gpumode', required=True)
    parser.add_argument('--output', required=True, metavar="<dir>")
    parser.add_argument('--testType', required=True)
    parser.add_argument('--projectPath', required=True)

    return parser


def main():
    args = createArgsParser().parse_args()
    stage_report = [{'status': 'INIT'}, {'log': ['simpleRender.py start']}]

    testsList = None
    script_template = None
    cmdScriptPath = None

    try:
        with open(args.tests, 'r') as file:
            testsList = file.read()
    except OSError as e:
        stage_report[0]['status'] = 'ERROR'
        stage_report[1]['log'].append('OSError while read tests list. ' + str(e))
        return 1

    try:
        os.makedirs(args.output)
        os.mkdir(os.path.join(args.output, 'Color'))
        os.mkdir(os.path.join(args.output, 'Opacity'))
    except OSError as e:
        stage_report[0]['status'] = 'ERROR'
        stage_report[1]['log'].append('OSError while create folders. ' + str(e))
        return 1

    try:
        # with open(os.path.join(os.path.dirname(sys.argv[0]), 'template.mel')) as f:
        with open(os.path.join(os.path.dirname(__file__), 'template.mel')) as f:
            script_template = f.read()
    except OSError as e:
        stage_report[0]['status'] = 'ERROR'
        stage_report[1]['log'].append('OSError while read mel template. ' + str(e))
        return 1

    outputFolder = os.path.abspath(args.output).replace('\\', '/')
    basePath = os.path.abspath(args.projectPath).replace('\\', '/')
    melScript = script_template.format(outputFolder=outputFolder,
                                       testsList=testsList,
                                       testType=args.testType,
                                       projectBase=basePath)
    melScriptPath = args.output
    melScriptFile = os.path.join(args.output, 'script.mel')
    with open(melScriptFile, 'w') as f:
        f.write(melScript)

    copyfile(os.path.join(os.path.dirname(__file__), 'common.mel'),
             os.path.join(args.output, 'maya_benchmark_common.mel'))

    cmdRun = '''
    set MAYA_CMD_FILE_OUTPUT=%cd%/scriptEditorTrace.txt 
    set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
    "{tool}" -command "source script.mel; evalDeferred -lp (mayaBenchmark({{{gpumode}}}));"''' \
        .format(tool=args.tool, gpumode=args.gpumode)

    try:
        cmdScriptPath = os.path.join(args.output, 'script.bat')
        with open(cmdScriptPath, 'w') as f:
            f.write(cmdRun)
        stage_report[1]['log'].append('Templates is formated, starting execution')
    except OSError as e:
        stage_report[0]['status'] = 'ERROR'
        stage_report[1]['log'].append('OSError while write mel script. ' + str(e))
        return 1

    os.chdir(args.output)

    p = psutil.Popen(os.path.join(args.output, 'script.bat'), stdout=subprocess.PIPE)
    rc = -1

    while True:
        try:
            rc = p.wait(timeout=20)
        except psutil.TimeoutExpired as err:
            rc = -1
            error_screen = pyscreenshot.grab()
            error_screen.save(os.path.join(args.output, 'error_screenshot.jpg'))
            if "maya" in get_windows_titles():
                for child in reversed(p.children(recursive=True)):
                    child.terminate()
                p.terminate()
                break
        else:
            break

    if rc == 0:
        print('passed')
        stage_report[0]['status'] = 'OK'
        stage_report[1]['log'].append('subprocess PASSED')
    else:
        print('failed')
        stage_report[0]['status'] = 'TERMINATED'
        stage_report[1]['log'].append('subprocess FAILED and was TERMINATED')

    with open(os.path.join(args.output, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')

    return rc


if __name__ == "__main__":
    rc = main()
    exit(rc)