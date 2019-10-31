import json
import os 

class RPR_report_json:
    def __init__(self, render_device = '', file_name = '', render_color_path = '', render_time = '', scene_name = '', test_group = '', test_case = '', difference_color = '', test_status = '', script_info = ''):
        self.render_device = render_device
        #self.tool = mel.eval('about -version')
        #self.date_time = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        #self.render_version = mel.eval('getRPRPluginVersion()')
        #self.core_version = mel.eval('getRprCoreVersion()')
        self.file_name = file_name
        self.render_color_path = "Color/MAYA_SM_000.jpg"
        self.render_time = 0
        self.scene_name = scene_name
        self.test_group = test_group
        self.test_case = test_case
        self.difference_color = difference_color
        self.test_status = test_status
        self.script_info = script_info

    def toJSON(self):
        json.dumps(self)


filePath = "C:/Users/Kataderon/Documents/projects/jobs_test_maya/Work/Results/Maya/Smoke" + "/" + 'test_case' + "_RPR.json"

report = RPR_report_json()
report.render_device = 'render_device_name'
report.file_name = 'test_case' + ".jpg"
report.render_color_path = "Color/" + 'test_case' + ".jpg"
report.render_time = 10
report.scene_name = 'scene_name'
report.test_group = "{testType}"
report.test_case = 'test_case'
report.difference_color = "not compared yet"
report.test_status = "passed"
report.script_info = 'script_info'

f = open(filePath, 'a')
f.write(report.toJSON())
f.close