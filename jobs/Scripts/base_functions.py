import maya.mel as mel
import maya.cmds as cmds
import glob
import datetime
import time
import json
import re
import os.path as path
import os
from shutil import copyfile, move
import fireRender.rpr_material_browser

WORK_DIR = '{work_dir}'
TEST_TYPE = '{testType}'
RENDER_DEVICE = '{render_device}'
RES_PATH = '{res_path}'
PASS_LIMIT = {pass_limit}
RESOLUTION_X = {resolution_x}
RESOLUTION_Y = {resolution_y}
SPU = {SPU}
THRESHOLD = {threshold}
ENGINE = '{engine}'
RETRIES = {retries}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')


def event(name, start, case):
    with open(path.join('events', str(glob.glob('events/*.json').__len__() + 1) + '.json'), 'w') as f:
        f.write(json.dumps({{'name': name, 'time': datetime.datetime.utcnow().strftime(
            '%d/%m/%Y %H:%M:%S.%f'), 'start': start, 'case': case}}, indent=4))


def logging(message):
    print(' >>> [RPR TEST] [' +
          datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message)

def extract_img_from(folder, case):
    src_dir = path.join(WORK_DIR, 'Color', folder)
    img_name = cmds.renderSettings(firstImageName=True)[0]
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        try:
            move(path.join(src_dir, img_name), path.join(WORK_DIR, 'Color'))
            logging('Extract {{}} from {{}} folder'.format(img_name, folder))
        except Exception as ex:
            logging('Error while extracting {{}} from {{}}: {{}}'.format(img_name, folder, ex))
    else:
        logging("{{}} doesn't exist or isn't a folder".format(folder))

def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    if case['status'] == 'inprogress':
        case['status'] = 'done'
        logging(case['case'] + ' done')
        report['test_status'] = 'passed'
        report['group_timeout_exceeded'] = False
    else:
        report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']))
    if case['status'] == 'error':
        number_of_tries = case.get('number_of_tries', 0)
        if number_of_tries == RETRIES:
            error_message = 'Testcase wasn\'t executed successfully (all attempts were used). Number of tries: {{}}'.format(str(number_of_tries))
        else:
            error_message = 'Testcase wasn\'t executed successfully. Number of tries: {{}}'.format(str(number_of_tries))
        report['message'] = [error_message]
    else:
        report['message'] = []

    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    report['render_time'] = render_time
    report['test_group'] = TEST_TYPE
    report['test_case'] = case['case']
    report['difference_color'] = 0
    report['script_info'] = case['script_info']
    report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
    report['scene_name'] = case.get('scene', '')
    if case['status'] != 'skipped':
        report['file_name'] = case['case'] + case.get('extension', '.jpg')
        report['render_color_path'] = path.join('Color', report['file_name'])

    # save metrics which can be received witout call of functions of Maya
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))

    try:
        report['tool'] = mel.eval('about -iv')
    except Exception as e:
        logging('Failed to get Maya version. Reason: {{}}'.format(str(e)))
    try:
        report['render_version'] = mel.eval('getRPRPluginVersion()')
    except Exception as e:
        logging('Failed to get render version. Reason: {{}}'.format(str(e)))
    try:
        report['core_version'] = mel.eval('getRprCoreVersion()')
    except Exception as e:
        logging('Failed to get core version. Reason: {{}}'.format(str(e)))

    # save metrics which can't be received witout call of functions of Maya (additional measures to avoid stucking of Maya)
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def validateFiles():
    logging('Repath scene')
    cmds.filePathEditor(refresh=True)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)))
    logging('Start repath scene')
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=RES_PATH, recursive=True, ra=1)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)))
    logging('Repath finished')


def enable_rpr(case):
    if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
        cmds.loadPlugin('RadeonProRender', quiet=True)
        logging('Load rpr')


def rpr_render(case, mode='color'):
    validateFiles()
    logging('Prerender done')
    
    
def prerender(case):
    logging('Prerender')
    enable_rpr(case)

    # cmds.setAttr('RadeonProRenderGlobals.detailedLog', True)
    logging("mel.eval: athenaEnable -ae false")
    mel.eval('athenaEnable -ae false')

    if ENGINE == 'Tahoe':
        logging("cmds.setAttr: RadeonProRenderGlobals.tahoeVersion, 1")
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 1)
    elif ENGINE == 'Northstar':
        logging("cmds.setAttr: RadeonProRenderGlobals.tahoeVersion, 2")
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 2)
    elif ENGINE == 'Hybrid_Low':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 3")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 3)
    elif ENGINE == 'Hybrid_Medium':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 2")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 2)
    elif ENGINE == 'Hybrid_High':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 1")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 1)

    logging("cmds.optionVar: rm=RPR_DevicesSelected")
    cmds.optionVar(rm='RPR_DevicesSelected')
    logging("cmds.optionVar: iva=RPR_DevicesSelected, (RENDER_DEVICE in ['gpu', 'dual'])")
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['gpu', 'dual'])))
    logging("cmds.optionVar: iva=RPR_DevicesSelected, (RENDER_DEVICE in ['cpu', 'dual'])")
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['cpu', 'dual'])))

    if RESOLUTION_X and RESOLUTION_Y:
        logging("cmds.setAttr: defaultResolution.width, RESOLUTION_X")
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        logging("cmds.setAttr: defaultResolution.height, RESOLUTION_Y")
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    # cmds.setAttr('defaultRenderGlobals.currentRenderer',
    #              type='string' 'FireRender')
    logging("cmds.setAttr: defaultRenderGlobals.imageFormat, 8")
    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    logging("cmds.setAttr: RadeonProRenderGlobals.adaptiveThreshold, THRESHOLD")
    cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', THRESHOLD)
    logging("cmds.setAttr: RadeonProRenderGlobals.completionCriteriaIterations, PASS_LIMIT")
    cmds.setAttr(
        'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)
    logging("cmds.setAttr: RadeonProRenderGlobals.samplesPerUpdate, SPU")
    cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
    logging("cmds.setAttr: RadeonProRenderGlobals.completionCriteriaSeconds, 0")
    cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

    logging("cmds.setAttr: defaultRenderGlobals.imageFilePrefix, 0")
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", path.join(WORK_DIR, 'Color', case['case']), type="string")

    #? Different tries to apply transform to image, but it doesn't work in batch render for some reason
    # logging("cmds.colorManagementPrefs")
    # cmds.colorManagementPrefs(e=True, cmEnabled=True, outputTransformEnabled=True, viewTransformName='sRGB gamma', outputUseViewTransform=True)
    # cmds.colorManagementPrefs(e=True, cmEnabled=True, outputTransformEnabled=True, outputTransformName='sRGB gamma')
    # cmds.colorManagementPrefs(e=True, outputUseViewTransform=True)

    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][:rpr_render_index + 1]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                logging("exec: {{}}".format(function))
                exec(function)
            else:
                logging("eval: {{}}".format(function))
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))


def post_render(case_num):
    logging('Postrender')

    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][rpr_render_index + 1:]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                logging("exec: {{}}".format(function))
                exec(function)
            else:
                logging("eval: {{}}".format(function))
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))

    case_time = (datetime.datetime.now() - datetime.datetime.strptime(case['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    case['time_taken'] = case_time

    #TODO Calculate rendering time somehow
    reportToJSON(case, case_time)

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    # ? Not sure if it's needed
    # Athena need additional time for work before close maya
    # if TEST_TYPE not in ['Athena']:
    #     cmds.quit(abort=True)
    # else:
    #     cmds.evalDeferred('cmds.quit(abort=True)')


# place for extension functions


def main(case_num):

    logging('Entered main')
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    event('Open tool', False, case['case'])

    if case['status'] == 'active':
        case['status'] = 'inprogress'

    case['start_time'] = str(datetime.datetime.now())
    case['number_of_tries'] = case.get('number_of_tries', 0) + 1
    
    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    
    
    prerender(case)
