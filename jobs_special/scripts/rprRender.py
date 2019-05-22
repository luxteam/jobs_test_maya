import argparse
import sys
import os
import subprocess
import psutil
import ctypes
import pyscreenshot
import json
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import main_logger
from jobs_launcher.core.config import RENDER_REPORT_BASE


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
    parser.add_argument('--tests_list', required=True, metavar="<path>")
    parser.add_argument('--render_path', required=True, metavar="<path>")
    parser.add_argument('--scene_path', required=True, metavar="<path")
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--test_group', required=True)
    return parser.parse_args()


def main():
    args = createArgsParser()

    tests_list = {}
    tests = ""
    with open(args.tests_list, 'r') as file:
        tests_list = json.loads(file.read())

    if not os.path.exists(os.path.join(args.output_dir, 'Color')):
        os.makedirs(os.path.join(args.output_dir, 'Color'))

    tests = []
    for test in tests_list:
        if test['status'] == 'active':
            tests.append(test['name'])
            with open(os.path.join(args.output_dir, test['name'] + '_RPR.json'), 'w') as report_template:
                json.dump(RENDER_REPORT_BASE.update({"test_case": test['name'],
                                                     "test_status": "error"}), report_template, indent=4)

    with open(os.path.join(os.path.dirname(__file__), 'main_template.py'), 'r') as file:
        py_script = file.read().format(tests=tests, work_dir=args.output_dir.replace('\\', '/'),
                                       res_path=args.scene_path.replace('\\', '/'), test_group=args.test_group)

    with open(os.path.join(args.output_dir, 'script.py'), 'w') as file:
        file.write(py_script)

    cmd_script = '''
    set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log
    set PYTHONPATH=%cd%;PYTHONPATH
    set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
    "{}" -command "python(\\"import script as tester_script\\"); python(\\"tester_script.main()\\");" '''.format(args.render_path)

    cmd_script_path = os.path.join(args.output_dir, 'renderRPR.bat')

    try:
        with open(cmd_script_path, 'w') as file:
            file.write(cmd_script)
    except OSError as err:
        main_logger.error(str(err))
        return 1
    else:
        rc = -1
        os.chdir(args.output_dir)
        p = psutil.Popen(cmd_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        while True:
            try:
                rc = p.wait(timeout=5)
            except psutil.TimeoutExpired as err:
                fatal_errors_titles = ['maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor']
                if set(fatal_errors_titles).intersection(get_windows_titles()):
                    rc = -1
                    try:
                        error_screen = pyscreenshot.grab()
                        error_screen.save(os.path.join(args.output_dir, 'error_screenshot.jpg'))
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
    exit(main())
