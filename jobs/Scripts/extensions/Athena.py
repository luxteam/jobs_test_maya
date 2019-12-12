import os.path as path
from shutil import copyfile
import sys


try:
	with open(path.join(sys.argv[1], 'renderTool.log')) as f: 
		if 'successfully uploaded data to AWS!' in f.read(): 
			copyfile(path.join(sys.argv[1], '..', '..', '..', '..', 'jobs', 'Tests', 'pass.jpg'), path.join(sys.argv[1], 'Color', 'MAYA_SM_043.jpg'))
except:pass