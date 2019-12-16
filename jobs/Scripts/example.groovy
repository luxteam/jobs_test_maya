def executeRender(osName, gpuName, Map options) {
    
	timeout(time: 65, unit: 'MINUTES') {
		switch(osName) {
			case 'Windows':
				try {
					// Clean up work folder
					bat '''
						@echo off
						del /q *
						for /d %%x in (*) do @rd /s /q "%%x"
					''' 
					
					// unzip
					try {
						bat """
							7z x "${options.scene_name}"
						"""
						}
					} catch(e) {
						print e
					}
					
					switch(tool) {
						case 'Blender':  
							// copy necessary scripts for render
							bat """
								copy "${CIS_TOOLS}\\${options.cis_tools}\\blender_render.py" "."
								copy "${CIS_TOOLS}\\${options.cis_tools}\\launch_blender.py" "."
							"""
							// Launch render
							try {
								python3("launch_blender.py --tool ${version} --django_ip \"${options.django_url}/\" --id ${id} --build_number ${currentBuild.number} --min_samples ${options.Min_Samples} --max_samples ${options.Max_Samples} --noise_threshold ${options.Noise_threshold} --width ${options.Width} --height ${options.Height} --startFrame ${options.startFrame} --endFrame ${options.endFrame} ")
							} catch(e) {
								print e
								bat """
									mkdir "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
									copy "*" "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
								"""
							}
							break;

						case 'Max':
							// copy necessary scripts for render
							bat """
								copy "${CIS_TOOLS}\\${options.cis_tools}\\max_render.ms" "."
								copy "${CIS_TOOLS}\\${options.cis_tools}\\launch_max.py" "."
							"""
							// Launch render
							try {
								python3("launch_max.py --tool ${version} --django_ip \"${options.django_url}/\" --id ${id} --build_number ${currentBuild.number} --min_samples ${options.Min_Samples} --max_samples ${options.Max_Samples} --noise_threshold ${options.Noise_threshold} --width ${options.Width} --height ${options.Height} --startFrame ${options.startFrame} --endFrame ${options.endFrame} ")
							} catch(e) {
								print e
								bat """
									mkdir "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
									copy "*" "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
								"""
							}
							break;

						case 'Maya':
							// copy necessary scripts for render	
							bat """
								copy "${CIS_TOOLS}\\${options.cis_tools}\\maya_render.py" "."
								copy "${CIS_TOOLS}\\${options.cis_tools}\\launch_maya.py" "."
							"""
							// Launch render
							try {
								python3("launch_maya.py --tool ${version} --django_ip \"${options.django_url}/\" --id ${id} --build_number ${currentBuild.number} --min_samples ${options.Min_Samples} --max_samples ${options.Max_Samples} --noise_threshold ${options.Noise_threshold} --width ${options.Width} --height ${options.Height} --startFrame ${options.startFrame} --endFrame ${options.endFrame} ")
							} catch(e) {
								print e
								bat """
									mkdir "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
									copy "*" "..\\..\\RenderServiceStorage\\failed_${scene_name}_${id}_${currentBuild.number}"
								"""
							}
							break;

						

						}   
				} catch(e) {
					currentBuild.result = 'FAILURE'
					print e
					print(python3("${CIS_TOOLS}\\${options.cis_tools}\\send_render_results.py --django_ip \"${options.django_url}/\" --build_number ${currentBuild.number} --status ${currentBuild.result} --fail_reason \"${fail_reason}\" --id ${id}"))
				} 
			  	break;
		}
    }
}

def main(String PCs, Map options) {

	timestamps {

	    String PRJ_PATH="${options.PRJ_ROOT}/${options.PRJ_NAME}"
	    String JOB_PATH="${PRJ_PATH}/${JOB_NAME}/Build-${BUILD_ID}".replace('%2F', '_')
	    options['PRJ_PATH']="${PRJ_PATH}"
	    options['JOB_PATH']="${JOB_PATH}"

	    boolean PRODUCTION = true

		def testTasks = [:]
		List tokens = PCs.tokenize(':')
		String osName = tokens.get(0)
		String deviceName = tokens.get(1)
		String renderDevice = "gpu${deviceName}"
	  
		
		try {
			echo "Scheduling Render ${osName}:${deviceName}"
			testTasks["Render-${osName}-${deviceName}"] = {
				node("${osName} && RenderService && ${renderDevice}") {
					stage("Render") {
						timeout(time: 65, unit: 'MINUTES') {
							ws("WS/${options.PRJ_NAME}_Render") {
								executeRender(osName, deviceName, options)
							}
						}
					}
				}
			}

			parallel testTasks
		    
	    } catch(e) {
			println(e.toString());
			println(e.getMessage());
			println(e.getStackTrace());
			currentBuild.result = "FAILED"
			print e
	    } 
	}    
    
}
    
def call(String PCs = '',
    String id = '',
    String Tool = '',
    String Scene = '',  
    String sceneName = '',
    String Min_samples = '',
    String Max_samples = '',
    String Noise_threshold = '',
    String startFrame = '',
    String endFrame = '',
    String Width = '',
    String Height = ''
    ) {
	String PRJ_ROOT='RenderServiceRenderJob'
	String PRJ_NAME='RenderServiceRenderJob'  
	main(PCs,[
	    enableNotifications:false,
	    PRJ_NAME:PRJ_NAME,
	    PRJ_ROOT:PRJ_ROOT,
	    id:id,
	    Tool:Tool,
	    Scene:Scene,
	    sceneName:sceneName,
	    Min_Samples:Min_Samples,
	    Max_Samples:Max_Samples,
	    Noise_threshold:Noise_threshold,
	    startFrame:startFrame,
	    endFrame:endFrame,
	    Width:Width,
	    Height:Height
	    ])
    }
