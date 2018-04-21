import argparse
import os
import json


parser = argparse.ArgumentParser()
parser.add_argument('--work_dir', required=True)
parser.add_argument('--stage_report', required=True)

args = parser.parse_args()
directory = args.work_dir
stage_report = [{'status': 'INIT'}, {'log': ['make_report_json.py start']}]

files = os.listdir(directory)
json_files = list(filter(lambda x: x.endswith('RPR.json'), files))
result_json = ""

for file in range(len(json_files)):
    stage_report[1]['log'].append('processing {}'.format(json_files[file]))

    if (len(json_files) == 1):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        result_json += text
        break

    if (file == 0):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        text = text[:-2]
        text = text + "," + "\r\n"
        result_json += text

    elif (file == (len(json_files))-1):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        text = text[2:]
        result_json += text

    else:
        f = open(os.path.join(directory, json_files[file]), 'r')    
        text = f.read()
        f.close()
        text = text[2:]
        text = text[:-2]
        text = text + "," + "\r\n"
        result_json += text

with open(os.path.join(directory, "report.json"), 'w') as file:
    file.write(result_json)

stage_report[0]['status'] = 'OK'
stage_report[1]['log'].append('report.json saved')

with open(os.path.join(directory, args.stage_report), 'w') as file:
    json.dump(stage_report, file, indent=' ')
