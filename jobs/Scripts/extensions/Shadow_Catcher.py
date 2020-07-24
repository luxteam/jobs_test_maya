def alpha_render(case):
    mel.eval('renderWindowEditor -edit -displayStyle "mask" renderView')
    rpr_render(case)
    mel.eval('renderWindowEditor -edit -displayStyle "color" renderView')
