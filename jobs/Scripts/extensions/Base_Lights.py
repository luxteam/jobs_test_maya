def removeEnvironment():
	objects = cmd.ls(g=True)
	for obj in objects:
		if cmd.objectType(obj) in ('RPRIBL', 'RPRSky'):
			transform = cmd.listRelatives(obj, p=True)[0]
			cmd.delete(transform)	