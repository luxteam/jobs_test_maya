def save_viewport(case):
    for i in range(0,30):
        cmds.refresh(currentView=True, fe='png', fn=WORK_DIR+'/Color/'+case['case']+'.jpg')