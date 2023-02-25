import maya.cmds as cmds


###############################################    Ui    #########################################################


def wspace_loc_ui():
    name = 'World_Space_Loc'

    if cmds.window(name, exists=1):
        cmds.deleteUI(name)
    cmds.window(name, rtf=1, w=280, h=280, t=name, s=1)
    cmds.columnLayout(rs=3, adj=1, )

    cmds.rowColumnLayout(nc=2, adj=1)
    every_frame = cmds.checkBox(l='Bake every frame', value=False, )
    offset_con = cmds.checkBox(l='Maintain Offset', value=False)

    cmds.setParent('..')
    cmds.button(l='Bake to Locators', h=40, c=lambda *a: bake_loc(every_frame))

    cmds.rowColumnLayout(nc=1, adj=1)
    cmds.button(l='Parent constr to locator', h=40, c=lambda *a: parent_loc(offset_con))

    cmds.button(l='Point constr to locator', w=115, h=25, c=lambda *a: point_loc(offset_con))
    cmds.button(l='Orient constr to locator', w=115, h=25, c=lambda *a: orient_loc(offset_con))

    cmds.setParent('..')
    cmds.button(l='Select Locators', h=40, c=lambda *a: sel_loc())
    cmds.rowColumnLayout(nc=2, adj=2, )
    cmds.button(l='locator  +  ', w=115, h=35, c=lambda *a: scale_loc_max())
    cmds.button(l='locator  -  ', w=115, h=35, c=lambda *a: scale_loc_low())

    cmds.setParent('..')
    cmds.button(l='Delete Constraint', h=40, c=lambda *a: del_ctrl_constraint())
    cmds.button(l='Bake Controls', h=40, c=lambda *a: bake_ctrl(every_frame))

    # cmds.separator(height=1)
    cmds.text(label='KANG DAN DAN - 2023', w=40, h=10, )
    cmds.separator(height=1)

    cmds.showWindow(name)


#############################################    bake_loc    #####################################################


def bake_loc(every_frame):
    j = cmds.checkBox(every_frame, q=True, value=True)
    if j:
        bake_frame = False
    else:
        bake_frame = True

    open_key = cmds.playbackOptions(query=True, animationStartTime=True, )
    end_key = cmds.playbackOptions(query=True, animationEndTime=True, )

    bake_obj = []

    obj = cmds.ls(selection=True)

    if obj:

        for tag_obj in obj:

            if cmds.objExists('WSpace_loc_' + tag_obj):
                cmds.warning('One is enough')
            else:

                new_loc = cmds.spaceLocator(name='WSpace_loc_' + tag_obj)

                cmds.parentConstraint(tag_obj, new_loc, weight=1.0, maintainOffset=False)

                bake_obj.append(new_loc[0])

        if bake_obj:
            cmds.bakeResults(bake_obj, time=(open_key, end_key), smart=(bake_frame, 0),
                             simulation=False, preserveOutsideKeys=True, sparseAnimCurveBake=False,
                             removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False,
                             minimizeRotation=True, controlPoints=False, shape=True)

            cmds.delete(bake_obj, constraints=True)
    else:
        cmds.warning('Please select one object bake locator ')

    cmds.select(obj)


############################################    parent_loc    ####################################################


def parent_loc(offset_con):
    of = cmds.checkBox(offset_con, q=True, value=True)
    if of:
        Offseta = True
    else:
        Offseta = False

    select_obj = cmds.ls(selection=True)

    if select_obj:

        for objs in select_obj:

            if cmds.objExists('WSpace_loc_' + objs):

                if cmds.objExists('WSpace_loc_' + objs + '_parentConstraint'):
                    cmds.warning('There is a parent constraint')
                elif cmds.objExists('WSpace_loc_' + objs + '_pointConstraint'):
                    cmds.warning('There is a point constraint')
                elif cmds.objExists('WSpace_loc_' + objs + '_orientConstraint'):
                    cmds.warning('There is a orient constraint')


                else:
                    cmds.parentConstraint('WSpace_loc_' + objs, objs, weight=1.0, maintainOffset=Offseta,
                                          name='WSpace_loc_' + objs + '_parentConstraint')

            else:
                cmds.warning('The object doesn\'t have a space locator yet')

    else:
        cmds.warning('Please select an object that needs to be constrained by a space locator')


############################################    point_loc    #####################################################


def point_loc(offset_con):
    of = cmds.checkBox(offset_con, q=True, value=True)
    if of:
        Offseta = True
    else:
        Offseta = False

    select_obj = cmds.ls(selection=True)

    if select_obj:

        for objs in select_obj:

            if cmds.objExists('WSpace_loc_' + objs):

                if cmds.objExists('WSpace_loc_' + objs + '_parentConstraint'):
                    cmds.warning('There is a parent constraint')

                else:
                    if cmds.objExists('WSpace_loc_' + objs + '_pointConstraint'):
                        cmds.warning('There is a point constraint')
                    else:
                        cmds.pointConstraint('WSpace_loc_' + objs, objs, weight=1.0, maintainOffset=Offseta,
                                             name='WSpace_loc_' + objs + '_pointConstraint')

            else:
                cmds.warning('The object doesn\'t have a space locator yet')

    else:
        cmds.warning('Please select an object that needs to be constrained by a space locator')


############################################    orient_loc    #####################################################


def orient_loc(offset_con):
    of = cmds.checkBox(offset_con, q=True, value=True)
    if of:
        Offseta = True
    else:
        Offseta = False

    select_obj = cmds.ls(selection=True)

    if select_obj:

        for objs in select_obj:

            if cmds.objExists('WSpace_loc_' + objs):

                if cmds.objExists('WSpace_loc_' + objs + '_parentConstraint'):
                    cmds.warning('There is a parent constraint')

                else:
                    if cmds.objExists('WSpace_loc_' + objs + '_orientConstraint'):
                        cmds.warning('There is a orient constraint')
                    else:
                        cmds.orientConstraint('WSpace_loc_' + objs, objs, weight=1.0, maintainOffset=Offseta,
                                              name='WSpace_loc_' + objs + '_orientConstraint')

            else:
                cmds.warning('The object doesn\'t have a space locator yet')

    else:
        cmds.warning('Please select an object that needs to be constrained by a space locator')


###############################################    sel_loc    ########################################################


def sel_loc():
    select_ctrl = cmds.ls(selection=True)

    null_loc_name = []

    if select_ctrl:

        for slobj in select_ctrl:

            if cmds.objExists('WSpace_loc_' + slobj):

                null_loc_name.append('WSpace_loc_' + slobj)
            else:
                cmds.warning('That object does not have a space locator ')

        cmds.select(null_loc_name)

    else:
        cmds.warning('Please select an object that is constraints by a space locator')


###############################################    del_ctrl_con    #####################################################


def del_ctrl_constraint():
    del_constraint_obj = cmds.ls(selection=True)

    if del_constraint_obj:

        for del_con in del_constraint_obj:

            if cmds.objExists('WSpace_loc_' + del_con + '_parentConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_parentConstraint', constraints=True)
            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint') and cmds.objExists(
                    'WSpace_loc_' + del_con + '_orientConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)
                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
            elif cmds.objExists('WSpace_loc_' + del_con + '_orientConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)
            else:
                cmds.warning('The object has not been constrained by a space locator yet')


    else:
        cmds.warning('Please select an object that needs to have its constraints removed')


#################################################    bake_ctrl    ######################################################


def bake_ctrl(every_frame):
    j = cmds.checkBox(every_frame, q=True, value=True)
    if j:
        bake_frame = False
    else:
        bake_frame = True

    open_key = cmds.playbackOptions(query=True, animationStartTime=True, )
    end_key = cmds.playbackOptions(query=True, animationEndTime=True, )

    obj = cmds.ls(selection=True)

    parent_list = []

    bake_list = []

    no_parent_list = []

    if obj:

        for obj_name in obj:

            if cmds.objExists('WSpace_loc_' + obj_name + '_parentConstraint'):

                parent_list.append('WSpace_loc_' + obj_name + '_parentConstraint')

                bake_list.append(obj_name)

            elif cmds.objExists('WSpace_loc_' + obj_name + '_pointConstraint') and cmds.objExists(
                    'WSpace_loc_' + obj_name + '_orientConstraint'):
                parent_list.append('WSpace_loc_' + obj_name + '_pointConstraint')
                parent_list.append('WSpace_loc_' + obj_name + '_orientConstraint')
                bake_list.append(obj_name)

            elif cmds.objExists('WSpace_loc_' + obj_name + '_pointConstraint'):
                parent_list.append('WSpace_loc_' + obj_name + '_pointConstraint')
                bake_list.append(obj_name)

            elif cmds.objExists('WSpace_loc_' + obj_name + '_orientConstraint'):
                parent_list.append('WSpace_loc_' + obj_name + '_orientConstraint')
                bake_list.append(obj_name)

            else:
                no_parent_list.append(obj_name)

        if no_parent_list:

            cmds.warning('Please deselect the object that is not constrained by a space locator')

        else:

            if bake_frame:
                cmds.bakeResults(bake_list, time=(open_key, end_key), smart=(True, 0), simulation=False,
                                 preserveOutsideKeys=True, sparseAnimCurveBake=False,
                                 removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False,
                                 minimizeRotation=True, controlPoints=False, shape=True)

                cmds.delete(parent_list, constraints=True)

            else:
                cmds.bakeResults(bake_list, time=(open_key, end_key), smart=(False, 0), )

                cmds.delete(parent_list, constraints=True)


    else:
        cmds.warning('Please select the object that needs to be baked')


#################################################    loc_scale    ######################################################


def scale_loc_max():
    select_obj = cmds.ls(selection=True)
    # a=1
    if select_obj and cmds.listRelatives(select_obj[0], shapes=True) and cmds.nodeType(
            cmds.listRelatives(select_obj[0], shapes=True)[0]) == 'locator':
        for s in select_obj:
            x = cmds.getAttr(s + '.localScaleX')
            cmds.setAttr(s + '.localScaleX', x * 1.5)
            y = cmds.getAttr(s + '.localScaleY')
            cmds.setAttr(s + '.localScaleY', y * 1.5)
            z = cmds.getAttr(s + '.localScaleZ')
            cmds.setAttr(s + '.localScaleZ', z * 1.5)
    else:
        cmds.warning('Please select  locator ')


def scale_loc_low():
    select_obj = cmds.ls(selection=True)
    # a=1
    if select_obj and cmds.listRelatives(select_obj[0], shapes=True) and cmds.nodeType(
            cmds.listRelatives(select_obj[0], shapes=True)[0]) == 'locator':
        for s in select_obj:
            x = cmds.getAttr(s + '.localScaleX')
            cmds.setAttr(s + '.localScaleX', x / 1.2)
            y = cmds.getAttr(s + '.localScaleY')
            cmds.setAttr(s + '.localScaleY', y / 1.2)
            z = cmds.getAttr(s + '.localScaleZ')
            cmds.setAttr(s + '.localScaleZ', z / 1.2)
    else:
        cmds.warning('Please select  locator ')


#################################################    end    ######################################################

wspace_loc_ui()
