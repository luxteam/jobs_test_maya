import maya.mel as mel
import maya.cmds as cmds
import glob
import datetime
import time
import json
import re
import os.path as path
import os
from shutil import copyfile
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


def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    if case['status'] == 'inprogress':
        report['test_status'] = 'passed'
        report['group_timeout_exceeded'] = False
    else:
        report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']))
  
    report['tool'] = mel.eval('about -iv')
    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    report['render_version'] = mel.eval('getRPRPluginVersion()')
    report['core_version'] = mel.eval('getRprCoreVersion()')
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
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def validateFiles():
    logging('Repath scene')
    # TODO: repath from folder with group
    unresolved_files = cmds.filePathEditor(
        query=True, listFiles='', unresolved=True, attributeOnly=True)
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=RES_PATH, recursive=True, ra=1)


def enable_rpr(case):
    if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
        cmds.loadPlugin('RadeonProRender', quiet=True)
        logging('Load rpr')


def rpr_render(case, mode='color'):
    logging('Render image')


def prerender(case):
    logging('Prerender')
    enable_rpr(case)

    # cmds.setAttr('RadeonProRenderGlobals.detailedLog', True)
    mel.eval('athenaEnable -ae false')

    if ENGINE == 'Tahoe':
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 1)
    elif ENGINE == 'Northstar':
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 2)
    elif ENGINE == 'Hybrid_Low':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 3)
    elif ENGINE == 'Hybrid_Medium':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 2)
    elif ENGINE == 'Hybrid_High':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 1)

    cmds.optionVar(rm='RPR_DevicesSelected')
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['gpu', 'dual'])))
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['cpu', 'dual'])))

    if RESOLUTION_X and RESOLUTION_Y:
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    # cmds.setAttr('defaultRenderGlobals.currentRenderer',
    #              type='string' 'FireRender')
    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', THRESHOLD)
    cmds.setAttr(
        'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)
    cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
    cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][:rpr_render_index + 1]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))

# place for extension functions


def post_render(case_num):
    logging('Postrender')
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][rpr_render_index + 1:]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))

    case_time = (datetime.datetime.now() - datetime.datetime.strptime(case['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    case['time_taken'] = case_time

    #TODO Calculate rendering time somehow
    reportToJSON(case, case_time)
    if case['status'] == 'inprogress':
        case['status'] = 'done'
        logging(case['case'] + ' done')

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    # ? Not sure if it's needed
    # Athena need additional time for work before close maya
    # if TEST_TYPE not in ['Athena']:
    #     cmds.quit(abort=True)
    # else:
    #     cmds.evalDeferred('cmds.quit(abort=True)')


def main(case_num):
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    event('Open tool', False, case['case'])

    if case['status'] in ['active', 'fail', 'skipped']:
        if case['status'] == 'active':
            case['status'] = 'inprogress'

    case['start_time'] = str(datetime.datetime.now())

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    prerender(case)
