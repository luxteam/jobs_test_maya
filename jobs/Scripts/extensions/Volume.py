def resetAttributes():
	cmd.setAttr('RPRVolumeMaterial1.scatterColor', 1, 1, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.transmissionColor', 1, 1, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.emissionColor', 1, 0, 1, type='double3')
	cmd.setAttr('RPRVolumeMaterial1.density', 0.5)
	cmd.setAttr('RPRVolumeMaterial1.scatteringDirection', 0.096)
	cmd.setAttr('RPRVolumeMaterial1.multiscatter', 1)


def setAttribute(volume_attr, file_attr, value):
	file = cmd.shadingNode("file", asTexture=True, isColorManaged=True)
	texture = cmd.shadingNode("place2dTexture", asUtility=True)
	cmd.connectAttr(texture + ".coverage", file + ".coverage", f=True)
	cmd.connectAttr(texture + ".translateFrame", file + ".translateFrame", f=True)
	cmd.connectAttr(texture + ".rotateFrame", file + ".rotateFrame", f=True)
	cmd.connectAttr(texture + ".mirrorU", file + ".mirrorU", f=True)
	cmd.connectAttr(texture + ".mirrorV", file + ".mirrorV", f=True)
	cmd.connectAttr(texture + ".stagger", file + ".stagger", f=True)
	cmd.connectAttr(texture + ".wrapU", file + ".wrapU", f=True)
	cmd.connectAttr(texture + ".wrapV", file + ".wrapV", f=True)
	cmd.connectAttr(texture + ".repeatUV", file + ".repeatUV", f=True)
	cmd.connectAttr(texture + ".offset", file + ".offset", f=True)
	cmd.connectAttr(texture + ".rotateUV", file + ".rotateUV", f=True)
	cmd.connectAttr(texture + ".noiseUV", file + ".noiseUV", f=True)
	cmd.connectAttr(texture + ".vertexUvTwo", file + ".vertexUvTwo" , f=True)
	cmd.connectAttr(texture + ".vertexUvThree", file + ".vertexUvThree", f=True)
	cmd.connectAttr(texture + ".vertexCameraOne", file + ".vertexCameraOne", f=True)
	cmd.connectAttr(texture + ".outUV", file + ".uv", f=True)
	cmd.connectAttr(texture + ".outUvFilterSize", file + ".uvFilterSize")
	cmd.connectAttr(texture + ".vertexUvOne", file + ".vertexUvOne")
	
	cmd.connectAttr(file + "." + file_attr, "RPRVolumeMaterial1." + volume_attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file