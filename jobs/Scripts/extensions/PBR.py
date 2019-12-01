def resetAttributes():
	cmd.setAttr('R_PBRMat.color', 0.0719, 0.31, 0.0719, type='double3')
	cmd.setAttr('R_PBRMat.metalness', 0)
	cmd.setAttr('R_PBRMat.specular', 1)
	cmd.setAttr('R_PBRMat.roughness', 0.1)
	try:
		cmd.connectAttr('RPRNormal4.out', 'R_PBRMat.normalMap', f=True)
	except:
		pass
	cmd.setAttr('file14.fileTextureName', 'sourceimages/normal.tif', type='string' )
	cmd.setAttr('R_PBRMat.glass', 1)
	cmd.setAttr('R_PBRMat.glassIOR', 1.2)
	cmd.setAttr('R_PBRMat.emissiveColor', 0.5, 0.5, 0.5, type='double3')
	cmd.setAttr('R_PBRMat.emissiveWeight', 0)
	cmd.setAttr('R_PBRMat.subsurfaceWeight', 0)
	cmd.setAttr('R_PBRMat.subsurfaceColor', 0.436, 0.227, 0.131, type='double3')
	cmd.setAttr('R_PBRMat.subsurfaceRadius0', 3.67)
	cmd.setAttr('R_PBRMat.subsurfaceRadius1', 1.37)
	cmd.setAttr('R_PBRMat.subsurfaceRadius2', 0.68)


def setAttribute(pbr_attr, file_attr, value):
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
	
	cmd.connectAttr(file + "." + file_attr, "R_PBRMat." + pbr_attr, force=True)
	cmd.setAttr(file + ".fileTextureName", value, type="string")

	return file