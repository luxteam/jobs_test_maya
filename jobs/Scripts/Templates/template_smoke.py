def check_test_cases_fail_save(test_case, passCount, script_info, scene):
    test = "{testCases}"
    tests = test.split(',')

    if (test != "all"):
        for test in tests:
            if test == test_case:
                rpr_fail_save(test_case, script_info)
    else:
        rpr_fail_save(test_case, script_info)


def check_test_cases(test_case, passCount, script_info, scene):
    test = "{testCases}"
    tests = test.split(',')
    if (test != "all"):
        for test in tests:
            if test == test_case:
                prerender(test_case, passCount, script_info, scene)
    else:
        prerender(test_case, passCount, script_info, scene)


def prerender(test_case, passCount, script_info, scene):
    scene_name = cmd.file(q=True, sn=True, shn=True)
    if (scene_name != scene):
        if (mel.eval('catch (`file -f -options "v=0;"  -ignoreVersion -o ' + scene + '`)')):
            cmd.evalDeferred("cmd.quit(abort=True)")
        else:
            activate_jpg_format()
    validateFiles()

    if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
        mel.eval('loadPlugin RadeonProRender')

    if(cmd.pluginInfo('fbxmaya', query=True, loaded=True) == 0):
        mel.eval('loadPlugin fbxmaya')

    cmd.setAttr("defaultRenderGlobals.currentRenderer",
                type="string" "FireRender")
    cmd.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", passCount)

    dictionary = json.load(
        open("{work_dir}" + "/../../../../jobs/Tests/Smoke/Dictionary.json"))

    try:
        for command in dictionary[test_case[-3:]]:
            eval(command)
    except:
        rpr_render(test_case, script_info)


def check_rpr_load():
    if(cmd.pluginInfo('RadeonProRender', query=True, loaded=True) == 0):
        mel.eval('loadPlugin RadeonProRender')
    if(cmd.pluginInfo('fbxmaya', query=True, loaded=True) == 0):
        mel.eval('loadPlugin fbxmaya')

    cmd.setAttr("defaultRenderGlobals.currentRenderer",
                type="string" "FireRender")


def open_rpr_scene():
    cmd.file(f-True, options="v=0;", ignoreVersion=True,
             o="Lamborginhi_Aventador.ma")


def import_fbx():
    mel.eval('FBXImport -f ("{res_path}" + "/sourceimages/park_bench1.fbx")')


def delete_fbx():
    cmd.delete('Default')


def create_IBL():
    cmd.hide('ground')
    iblNode = cmd.createNode('RPRIBL', n='RPRIBLShape')
    parent = cmd.listRelatives(p='iblNode')
    cmd.setAttr((parent[0] + ".scaleX"), 1001.25663706144)
    cmd.setAttr((parent[0] + ".scaleY"), 1001.25663706144)
    cmd.setAttr((parent[0] + ".scaleZ"), 1001.25663706144)
    cmd.rename(parent[0], 'RPRIBL')


def update_IBL_hdr():
    mel.eval(
        'setAttr -type "string" RPRIBLShape.filePath ("{res_path}" + "/sourceimages/Tropical_Beach_3k.hdr")')


def update_IBL_exr():
    mel.eval(
        'setAttr -type "string" RPRIBLShape.filePath ("{res_path}" + "/sourceimages/ibl_test.exr")')


def delete_IBL():
    cmd.showHidden('ground')
    cmd.delete('RPRIBL')


def create_sun_sky():
    SkyNode = cmd.createNode('RPRSky', n='RPRSkyShape')
    cmd.setAttr("RPRSkyShape.turbidity", 30)
    cmd.setAttr("RPRSkyShape.intensity", 6)


def delete_sun_sky():
    cmd.delete('RPRSky')


def create_ies_light():
    mel.eval('source shelfCommands.mel; createIESLight()')
    cmd.setAttr(type="string" "RPRIESLight.iesFile" (
        "{res_path}" + "/sourceimages/1.IES"))
    cmd.select('RPRIES1', r=True)
    cmd.move(400, 0, r=0)
    cmd.rotate(90, 0, r=True, os=True, fo=0)
    cmd.setAttr("RPRIESLight.intensity", 20)


def delete_ies_light():
    cmd.delete('RPRIES1')


def create_physical_light():
    mel.eval('source shelfCommands.mel; createPhysicalLight()')
    cmd.select('RPRPhysicalLight1', r=True)
    cmd.setAttr("RPRPhysicalLight1.translateY", 400)
    cmd.setAttr("RPRPhysicalLight1.rotateX", 270)
    cmd.setAttr("RPRPhysicalLight1Shape.lightIntensity", 100)
    cmd.setAttr("RPRPhysicalLight1Shape.intensityUnits", 0)


def delete_physical_light():
    cmd.delete('RPRPhysicalLight1')


def import_obj():
    cmd.file(i=True, type="OBJ", options="mo=-1",
             pr=("{res_path}" + "/sourceimages/example.obj"))
    cmd.rename("polySurface1", "Shader_Ball")
    cmd.setAttr("Shader_Ball.translate" - 3.774 - 1.4 - 3.865)
    cmd.setAttr("Shader_Ball.scale", 2, 2, 2)


def delete_obj():
    cmd.delete('Shader_Ball')


def activate_tone_mapping():
    cmd.setAttr("RadeonProRenderGlobals.applyGammaToMayaViews", 1)
    cmd.setAttr("RadeonProRenderGlobals.toneMappingWhiteBalanceEnabled", 1)


def deactivate_tone_mapping():
    cmd.setAttr("RadeonProRenderGlobals.applyGammaToMayaViews", 0)
    cmd.setAttr("RadeonProRenderGlobals.toneMappingWhiteBalanceEnabled", 0)


def activate_render_stamp():
    cmd.setAttr("RadeonProRenderGlobals.useRenderStamp", 1)


def deactivate_render_stamp():
    cmd.setAttr("RadeonProRenderGlobals.useRenderStamp", 0)


def activate_wireframe_mode():
    cmd.setAttr("RadeonProRenderGlobals.renderMode", 4)


def deactivate_wireframe_mode():
    cmd.setAttr("RadeonProRenderGlobals.renderMode", 1)


def activate_medium_quality():
    cmd.setAttr("RadeonProRenderGlobals.samples", 8)
    cmd.setAttr("RadeonProRenderGlobals.maxRayDepth", 15)


def deactivate_medium_quality():
    cmd.setAttr("RadeonProRenderGlobals.samples", 1)
    cmd.setAttr("RadeonProRenderGlobals.maxRayDepth", 5)


def change_image_size_hd720():
    cmd.setAttr("defaultResolution.width", 1280)
    cmd.setAttr("defaultResolution.height", 720)
    cmd.setAttr("defaultResolution.dotsPerInch", 72)
    cmd.setAttr("defaultResolution.deviceAspectRatio", 1.778)
    cmd.setAttr("defaultResolution.pixelAspect", 1.00)


def change_image_size_custom():
    cmd.setAttr("defaultResolution.width", 1500)
    cmd.setAttr("defaultResolution.height", 1125)


def change_image_size_standart():
    cmd.setAttr("defaultResolution.width", 1480)
    cmd.setAttr("defaultResolution.height", 800)
    cmd.setAttr("defaultResolution.dotsPerInch", 72)
    cmd.setAttr("defaultResolution.deviceAspectRatio", 1.850)
    cmd.setAttr("defaultResolution.pixelAspect", 1.00)


def activate_jpg_format():
    cmd.setAttr("defaultRenderGlobals.imageFormat", 8)


def activate_png_format():
    cmd.setAttr("defaultRenderGlobals.imageFormat", 32)


def activate_denoiser_bilateral():
    cmd.setAttr("RadeonProRenderGlobals.denoiserEnabled", 1)
    cmd.setAttr("RadeonProRenderGlobals.denoiserType", 0)
    cmd.setAttr("RadeonProRenderGlobals.denoiserRadius", 1)


def activate_denoiser_lwr():
    cmd.setAttr("RadeonProRenderGlobals.denoiserEnabled", 1)
    cmd.setAttr("RadeonProRenderGlobals.denoiserType", 1)


def activate_denoiser_eaw():
    cmd.setAttr("RadeonProRenderGlobals.denoiserEnabled", 1)
    cmd.setAttr("RadeonProRenderGlobals.denoiserType", 2)


def deactivate_denoiser():
    cmd.setAttr("RadeonProRenderGlobals.denoiserEnabled", 0)


def import_rpr_matlib():
    libraryPath = fireRender.rpr_material_browser.getLibPath()
    material = "Fiberglass"
    material_path = libraryPath + "/" + material
    xml = mel.eval('getFileList -folder '+material_path+' -filespec "*.xml"')
    material_path = material_path + "/" + xml[0]

    mel.eval('RPRXMLImport -file '+material_path +
             ' -ii false -mn "materialTestNode"')
    cmd.select('Lamborginhi_Aventador', r=True)
    cmd.sets(e=True, forceElement="materialTestNodeSG")


def create_area_light():
    cmd.defaultAreaLight(1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0)
    cmd.setAttr("areaLightShape1.intensity", 20)
    cmd.setAttr("areaLight1.translateY", 400)
    cmd.setAttr("areaLight1.rotateX", 270)


def delete_area_light():
    cmd.delete('areaLight1')


def activate_uv():
    cmd.setAttr("RadeonProRenderGlobals.aovDisplayedInRenderView", 3)


def deactivate_uv():
    cmd.setAttr("RadeonProRenderGlobals.aovDisplayedInRenderView", 0)


def maxRayDepth_15():
    cmd.setAttr("RadeonProRenderGlobals.maxRayDepth", 15)


def maxRayDepth_default():
    cmd.setAttr("RadeonProRenderGlobals.maxRayDepth", 5)


def setIterations_400():
    cmd.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 400)


def setIterations_default():
    cmd.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 50)


def duplicate_500_instances():
    cmd.select('Cube', r=True)
    mel.eval('instance; rotate -r 0 10 0; move -r 0.025 0.025 0.025; for ($i=1; $i<500; ++$i) instance -st;')


def create_and_asign_uber():
    rpr = mel.eval('shadingNode -asShader "RPRUberMaterial"')
    cmd.setAttr((rpr + ".diffuse"), 1)
    cmd.setAttr((rpr + ".diffuseColor"), 1, 0, 0)
    sge = rpr + "SG"
    cmd.sets(renderable=True, noSurfaceShader=True, empty=True, name=sge)
    cmd.connectAttr(f=(rpr + ".outColor")(sge + ".surfaceShader"))
    cmd.select('Lamborginhi_Aventador', r=True)
    sgs = mel.eval('listConnections -type shadingEngine '+rpr)
    cmd.sets(e=True, forceElement=sgs[0])


def create_and_asign_pbr():
    rpr = mel.eval('shadingNode -asShader "RPRPbrMaterial"')
    cmd.setAttr((rpr + ".color"), 0, 0, 1)
    sge = rpr + "SG"
    cmd.sets(renderable=True, noSurfaceShader=True, empty=True, name=sge)
    cmd.connectAttr(f=(rpr + ".outColor")(sge + ".surfaceShader"))
    cmd.select('Lamborginhi_Aventador', r=True)
    sgs = mel.eval('listConnections -type shadingEngine '+rpr)
    cmd.sets(e=True, forceElement=sgs[0])


def multiple_ies_lights():
    # for ($i=1; $i<13; ++$i){{
    # 	 setAttr -type "string" ("RPRIESLight" + $i +".iesFile") ("{res_path}" + "/sourceimages/1.IES");
    #	 setAttr ("RPRIESLight" + $i +".intensity") 2;
    # }}

    cmd.setAttr(type="string" ("RPRIESLight1.iesFile")
                ("{res_path}" + "/sourceimages/1.IES"))
    cmd.setAttr(("RPRIESLight1.intensity"), 2)
    cmd.setAttr(type="string" ("RPRIESLight6.iesFile")
                ("{res_path}" + "/sourceimages/1.IES"))
    cmd.setAttr(("RPRIESLight6.intensity"), 2)
    cmd.setAttr(type="string" ("RPRIESLight12.iesFile")
                ("{res_path}" + "/sourceimages/1.IES"))
    cmd.setAttr(("RPRIESLight12.intensity"), 2)


def shadow_catcher_test():
    cmd.setAttr("RadeonProRenderGlobals.aovOpacity", 1)
    cmd.setAttr("RadeonProRenderGlobals.aovBackground", 1)
    cmd.setAttr("RadeonProRenderGlobals.aovShadowCatcher", 1)
    rpr = mel.eval('shadingNode -asShader "RPRShadowCatcherMaterial"')
    sge = rpr + "SG"
    cmd.sets(renderable=True, noSurfaceShader=True, empty=True, name=sge)
    cmd.connectAttr(f=(rpr + ".outColor")(sge + ".surfaceShader"))
    cmd.select('Plane01', r=True)
    sgs = mel.eval('listConnections -type shadingEngine '+rpr)
    cmd.sets(e=True, forceElement=sgs[0])


def case_function(case, cases):
    functions = {{
        'check_test_cases': check_test_cases,
        'check_test_cases_success_save': check_test_cases_success_save
    }}
    func = cases[case]['function']
    if (cases[case]['active'] == True):
        if (func == 'check_test_cases'):
            functions[func](case, cases[case]['pass_count'],
                            cases[case]['script_info'],  cases[case]['scene'])
        elif (func == 'check_test_cases_success_save'):
            functions[func](case, cases[case]['script_info'])


def main():

    mel.eval('setProject ("C:/TestResources/MayaAssets");')

    check_rpr_load()

    cases = json.load(
        open("C:/Users/Kataderon/Documents/projects/jobs_test_maya/Work/Results/Maya/Smoke" + "/../../../../jobs/Tests/Smoke/TestCases.json"))

    for case in cases:#TODO normal order
        try:
            case_function(case, cases)
        except Exception as e:
            print(e)

    cmd.evalDeferred("cmd.quit(abort=True)")
