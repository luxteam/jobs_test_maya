try:
	with open(path.join(WORK_DIR, 'renderTool.log')) as f: 
		if 'successfully uploaded data to AWS!' in f.read(): 
			cmds.sysFile(path.join(WORK_DIR, '..', '..', '..', '..', 'jobs', 'Tests', 'pass.jpg'), copy=path.join(WORK_DIR, 'Color', 'MAYA_SM_043.jpg'))
except:pass