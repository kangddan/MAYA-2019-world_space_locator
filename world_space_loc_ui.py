# coding=utf-8
from functools import partial
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math


###############################################    Ui    #########################################################


def wspace_loc_ui():
    name = 'World_Space_Loc'

    if cmds.window(name, exists=1):
        cmds.deleteUI(name)
    window = cmds.window(name, rtf=1, w=280, h=280, t=name, s=1)
    #ly0 = cmds.columnLayout(adj=True,parent=window)
    ly1 = cmds.columnLayout(rs=5, adj=1,parent = window)

    ly2 = cmds.rowColumnLayout(nc=2, adj=1,parent = ly1)
    every_frame = cmds.checkBox(l='Bake every frame', value=False,parent=ly2 )
    offset_con = cmds.checkBox(l='Maintain Offset', value=False,parent=ly2 )


    ly3 = cmds.rowColumnLayout(nc=1, adj=1,parent = ly1)
    cmds.button(l='Bake to Locators', h=40, c=lambda *a: bake_loc(every_frame),parent=ly3,annotation='烘焙一个定位器')
    

    ly4 = cmds.rowColumnLayout(nc=1, adj=1,parent = ly1)
    cmds.button(l='Parent constr to locator', h=40, c=lambda *a: parent_loc(offset_con),parent=ly4)
    cmds.button(l='Point constr to locator', w=115, h=25, c=lambda *a: point_loc(offset_con),parent=ly4)
    cmds.button(l='Orient constr to locator', w=115, h=25, c=lambda *a: orient_loc(offset_con),parent=ly4)
    
    ly5 = cmds.rowColumnLayout(nc=2, adj=2,parent = ly4 )
    cmds.button(l='Add  aim constr', w=115, h=25,c=lambda *a: aim_obj(),parent=ly5 )
    cmds.button(l='Bake aim group', w=115, h=25,c=lambda *a: bake_aim(every_frame),parent=ly5)
    cmds.setParent('..')
    
    ly6 = cmds.rowColumnLayout(nc=1, adj=1,parent = ly1)
    cmds.button(l='Delete Constraint', h=40, c=lambda *a: del_ctrl_constraint(),parent=ly6)
    cmds.button(l='Select Locators', h=50, c=lambda *a: sel_loc(),parent=ly6)
    ly7 = cmds.frameLayout(l='Color Picker',collapsable=True,parent=ly6)
    ly8 = cmds.rowColumnLayout(nc=9,adj=5,parent = ly7)
    ######################################################################################################
    color_lis=[(1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0), 
                    (0.0, 1.0, 0.0), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), 
                    (1.0, 0.5, 0.5), (0.75, 0.75, 0.75), (1.0, 1.0, 1.0)]
    null_id = []
    for idd,i in enumerate(range(1,10)):
        id = cmds.button(l='ID'+str(idd+1), w=26,h=20,bgc=color_lis[idd],parent=ly8)
        null_id.append(id)
    '''id1 = cmds.button(l='ID1', w=26,h=20,bgc=color_lis[0],parent=ly8)
    id2 = cmds.button(l='ID2', w=26,h=20,bgc=color_lis[1],parent=ly8)
    id3 = cmds.button(l='ID3', w=26,h=20,bgc=color_lis[2],parent=ly8)
    id4 = cmds.button(l='ID4', w=26,h=20,bgc=color_lis[3],parent=ly8)
    id5 = cmds.button(l='ID5', w=26,h=20,bgc=color_lis[4],parent=ly8)
    id6 = cmds.button(l='ID6', w=26,h=20,bgc=color_lis[5],parent=ly8)
    id7 = cmds.button(l='ID7', w=26,h=20,bgc=color_lis[6],parent=ly8)
    id8 = cmds.button(l='ID8', w=26,h=20,bgc=color_lis[7],parent=ly8)
    id9 = cmds.button(l='ID9', w=26,h=20,bgc=color_lis[8],parent=ly8)
    '''
    ######################################################################################################
    color_index=[13,24,17,14,18,6,20,3,16]
    for idd,i in enumerate(range(1,10)):
        id = cmds.button(null_id[idd], edit=True,command = partial(set_color,color_index[idd]))
        
    
    '''
    cmds.button(id1,edit=True,command = partial(set_color,13))
    cmds.button(id2,edit=True,command = partial(set_color,24))
    cmds.button(id3,edit=True,command = partial(set_color,17))
    cmds.button(id4,edit=True,command = partial(set_color,14))
    cmds.button(id5,edit=True,command = partial(set_color,18))
    cmds.button(id6,edit=True,command = partial(set_color,6))
    cmds.button(id7,edit=True,command = partial(set_color,20))
    cmds.button(id8,edit=True,command = partial(set_color,3))
    cmds.button(id9,edit=True,command = partial(set_color,16))
    '''
    
    
    
    
    
    
    ######################################################################################################
    ly9 = cmds.rowColumnLayout(nc=2, adj=2,parent = ly6 )
    cmds.button(l='locator  +  ', w=115, h=35, c=lambda *a: scale_loc_max(),parent = ly9)
    cmds.button(l='locator  -  ', w=115, h=35, c=lambda *a: scale_loc_low(),parent = ly9)
   
    

    
    ly10 = cmds.rowColumnLayout(nc=1, adj=1,parent = ly1 )
    cmds.button(l='Bake Controls', h=40, c=lambda *a: bake_ctrl(every_frame),parent=ly10)
    

    
    cmds.text(label='World - Space - Locator - v1.3', w=40, h=13, )
    #cmds.separator(height=1)
    # by_kangddan 20230227

    cmds.showWindow(name)



#############################################    set color   #####################################################

def set_color(colorid,*args):  
    s_list = cmds.ls(selection = True,flatten=True)
    c = cmds.listRelatives (s_list, children = 1)
    for shape in s_list:  
        # 如果是关节，单独设置
        if cmds.nodeType(shape) == 'joint':
            cmds.setAttr(shape+'.overrideEnabled',1)
            cmds.setAttr(shape+'.overrideColor',colorid)
            continue
            
        # 如果这个对象是shape节点就设置颜色(主要给多个shape节点的ctrl设置颜色)
        
        for cc in c:
            if cmds.objectType(cc,isAType ='shape'):
                #shapes = cmds.listRelatives(cc, s=True)
                cmds.setAttr(cc+'.overrideEnabled',1)
                cmds.setAttr(cc+'.overrideColor',colorid)   
            
#############################################    select_obj    #####################################################

#  获取所选对象的函数，返回所选对象列表

def select_obj():
    s_list = cmds.ls(selection = True)
    return s_list

s_obj = select_obj()

#############################################    get time    #####################################################

#  获取当前动画时长的函数，返回s最小开始值和最大结束值

def pbo():
    get_time_list = []
    get_time_list.append(cmds.playbackOptions(query=True, animationStartTime=True))
    get_time_list.append(cmds.playbackOptions(query=True, animationEndTime=True))
    return get_time_list
    
start_t = pbo()[0]
end_t = pbo()[1]


#############################################    bake_loc    #####################################################


def bake_loc(every_frame):
    j = cmds.checkBox(every_frame, q=True, value=True)
    if j:
        bake_frame = False
    else:
        bake_frame = True

    bake_obj = []

    obj = cmds.ls(selection=True)

    if obj:

        for tag_obj in obj:

            if cmds.objExists('WSpace_loc_' + tag_obj):
                cmds.warning('One is enough')
            else:
                ro = cmds.getAttr(tag_obj+'.rotateOrder')
                new_loc = cmds.spaceLocator(name='WSpace_loc_' + tag_obj)
                cmds.setAttr(new_loc[0]+'.rotateOrder',ro)
                
                ##
                shape = cmds.listRelatives(new_loc, shapes=True)[0]
                cmds.setAttr('{}.{}'.format(new_loc[0],'v'), lock=True, keyable=False, channelBox=False)
                null_lis = ['lpx','lpy','lpz','lsx','lsy','lsz']
                for i in null_lis:
                    cmds.setAttr('{}.{}'.format(shape,i),keyable=False,channelBox=False)
                
                ###
                

                cmds.parentConstraint(tag_obj, new_loc, weight=1.0, maintainOffset=False)

                bake_obj.append(new_loc[0])

        if bake_obj:
            cmds.bakeResults(bake_obj, time=(start_t, end_t), smart=(bake_frame, 0),
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
            if cmds.objExists('WSpace_loc_aim_target_' + slobj) and cmds.objExists('WSpace_loc_aim_up_' + slobj) and cmds.objExists('WSpace_loc_' + slobj):
                null_loc_name.append('WSpace_loc_aim_up_' + slobj)
                null_loc_name.append('WSpace_loc_aim_target_' + slobj)
                null_loc_name.append('WSpace_loc_' + slobj)
            
            
            elif cmds.objExists('WSpace_loc_aim_target_' + slobj) and cmds.objExists('WSpace_loc_aim_up_' + slobj):
                null_loc_name.append('WSpace_loc_aim_up_' + slobj)
                null_loc_name.append('WSpace_loc_aim_target_' + slobj)
            
            elif cmds.objExists('WSpace_loc_' + slobj):

                null_loc_name.append('WSpace_loc_' + slobj)
                    
            else:
                cmds.warning('That object does not have a space locator ')

        cmds.select(null_loc_name)

    else:
        cmds.warning('Please select an object that is constraints by a space locator')

#  20230226 add select aim loc


###############################################    del_ctrl_con    #####################################################


def del_ctrl_constraint():
    del_constraint_obj = cmds.ls(selection=True)

    if del_constraint_obj:

        for del_con in del_constraint_obj:

            if cmds.objExists('WSpace_loc_' + del_con + '_parentConstraint') and cmds.objExists(
                    'WSpace_loc_aim_grp_' + del_con):
                cmds.delete('WSpace_loc_' + del_con + '_parentConstraint', constraints=True)
                cmds.delete('WSpace_loc_aim_grp_' + del_con, constraints=False)
            
            
                
            elif cmds.objExists('WSpace_loc_' + del_con + '_parentConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_parentConstraint', constraints=True)

            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint') and cmds.objExists(
                    'WSpace_loc_' + del_con + '_orientConstraint') and cmds.objExists('WSpace_loc_aim_grp_' + del_con):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)
                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
                cmds.delete('WSpace_loc_aim_grp_' + del_con, constraints=False)

            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint') and cmds.objExists(
                    'WSpace_loc_aim_grp_' + del_con):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)

                cmds.delete('WSpace_loc_aim_grp_' + del_con, constraints=False)

            elif cmds.objExists('WSpace_loc_' + del_con + '_orientConstraint') and cmds.objExists(
                    'WSpace_loc_aim_grp_' + del_con):

                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
                cmds.delete('WSpace_loc_aim_grp_' + del_con, constraints=False)

            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint') and cmds.objExists(
                    'WSpace_loc_' + del_con + '_orientConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)
                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
                
            elif cmds.objExists('WSpace_loc_' + del_con + '_orientConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_orientConstraint', constraints=True)
                
            elif cmds.objExists('WSpace_loc_' + del_con + '_pointConstraint'):
                cmds.delete('WSpace_loc_' + del_con + '_pointConstraint', constraints=True)
                
            elif cmds.objExists('WSpace_loc_aim_grp_' + del_con):
                cmds.delete('WSpace_loc_aim_grp_' + del_con, constraints=False)
            
            elif cmds.objExists(del_con + '_aim_Constraint') and cmds.objExists('WSpace_loc_aim_target_' + del_con) and cmds.objExists('WSpace_loc_aim_up_' + del_con): 
                cmds.delete(del_con + '_aim_Constraint', constraints=False) 
                cmds.delete('WSpace_loc_aim_target_' + del_con, constraints=False) 
                cmds.delete('WSpace_loc_aim_up_' + del_con, constraints=False)
            
            elif cmds.objExists('WSpace_loc_aim_target_' + del_con) and cmds.objExists('WSpace_loc_aim_up_' + del_con):                 
                cmds.delete('WSpace_loc_aim_target_' + del_con, constraints=False) 
                cmds.delete('WSpace_loc_aim_up_' + del_con, constraints=False)
                
            elif cmds.objExists(del_con + '_aim_Constraint') and cmds.objExists('WSpace_loc_aim_target_' + del_con): 
                cmds.delete(del_con + '_aim_Constraint', constraints=False) 
                cmds.delete('WSpace_loc_aim_target_' + del_con, constraints=False) 
            
            elif cmds.objExists('WSpace_loc_aim_up_' + del_con):               
                cmds.delete('WSpace_loc_aim_up_' + del_con, constraints=False)    
                
            else:
                cmds.warning('The object has not been constrained by a space locator yet')


    else:
        cmds.warning('Please select an object that needs to have its constraints removed')
#  20230226 add delete aim grp


#################################################    bake_ctrl    ######################################################


def bake_ctrl(every_frame):
    j = cmds.checkBox(every_frame, q=True, value=True)
    if j:
        bake_frame = False
    else:
        bake_frame = True

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
            
            elif cmds.objExists(obj_name + '_aim_Constraint') and cmds.objExists(
                    'WSpace_loc_' + obj_name + '_pointConstraint'):
                parent_list.append(obj_name + '_aim_Constraint')
                parent_list.append('WSpace_loc_' + obj_name + '_pointConstraint')
                bake_list.append(obj_name)
            
            elif cmds.objExists(obj_name + '_aim_Constraint'):
                parent_list.append(obj_name + '_aim_Constraint')
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
                cmds.bakeResults(bake_list, time=(start_t, end_t), smart=(True, 0), simulation=False,
                                 preserveOutsideKeys=True, sparseAnimCurveBake=False,
                                 removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False,
                                 minimizeRotation=True, controlPoints=False, shape=True)

                cmds.delete(parent_list, constraints=True)

            else:
                cmds.bakeResults(bake_list, time=(start_t, end_t), smart=(False, 0), )

                cmds.delete(parent_list, constraints=True)
            
            if cmds.objExists('WSpace_loc_aim_target_' + obj_name) and cmds.objExists('WSpace_loc_aim_up_' + obj_name):
                cmds.delete('WSpace_loc_aim_target_' + obj_name)
                cmds.delete('WSpace_loc_aim_up_' + obj_name)
                
            if cmds.objExists('WSpace_loc_aim_target_' + obj_name): 
                cmds.delete('WSpace_loc_aim_target_' + obj_name)
            
                    


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

############################################    add aim constr    #####################################################

def aim_obj():

    select_obj = cmds.ls(selection=True)
    
    if select_obj:
        
        for objs in select_obj:
            
            if cmds.objExists('WSpace_loc_aim_grp_' + objs):
                cmds.warning('An aim group already exists')
            
            else:
                
                if cmds.objExists('WSpace_loc_' + objs + '_parentConstraint'):
                    cmds.warning('There is a parent constraint')
                    
                elif cmds.objExists('WSpace_loc_' + objs + '_orientConstraint'):
                    cmds.warning('There is a orient constraint')
                
                else:
                    aim_grp = cmds.createNode('transform',name='WSpace_loc_aim_grp_' + objs)
                
                    aim_loc = cmds.spaceLocator(name='WSpace_loc_aim_target_' + objs)
                    cmds.setAttr(aim_loc[0]+'.overrideEnabled',1)
                    cmds.setAttr(aim_loc[0]+'.overrideColor',17)
                    cmds.parent(aim_loc,aim_grp)
                 
                    up_loc = cmds.spaceLocator(name='WSpace_loc_aim_up_' + objs)
                    cmds.setAttr(up_loc[0]+'.overrideEnabled',1)
                    cmds.setAttr(up_loc[0]+'.overrideColor',14)
                    cmds.parent(up_loc,aim_grp)
                
                    cmds.parentConstraint(objs, aim_grp, weight=1.0, maintainOffset=False,
                                          name='WSpace_loc_aim_' + objs + '_parentConstraint')
                                      
                    cmds.select(aim_loc[0])
    
    else:
        cmds.warning('Please select an object that needs to be constrained by a aim locator')

#################################################    bake aim    ######################################################


def bake_aim(every_frame):
    
    #############################
    j = cmds.checkBox(every_frame, q=True, value=True)
    if j:
        bake_frame = False
    else:
        bake_frame = True
    
    select_obj = cmds.ls(selection=True)
    bake_obj = []
    aim_ver = []
    if select_obj:
        
        for aim_obj in select_obj:
            if cmds.objExists('WSpace_loc_aim_target_'+aim_obj) and cmds.objExists('WSpace_loc_aim_up_'+aim_obj):
            
                ##########################################      aim     ################################################        
                # get aim loc position
                aim_p = cmds.xform('WSpace_loc_aim_target_'+aim_obj,query=True,translation=True,worldSpace=False)
                # get up loc position
                up_p = cmds.xform('WSpace_loc_aim_up_'+aim_obj,query=True,translation=True,worldSpace=False)
                # get aim loc vector len
                len_aim_p = math.sqrt(aim_p[0]**2 + aim_p[1]**2 + aim_p[2]**2)
                # get aim loc vector len
                len_up_p = math.sqrt(up_p[0]**2 + up_p[1]**2 + up_p[2]**2)
                # norma aim vec
                norm_aim_move = [int(aim_p[0]/len_aim_p), int(aim_p[1]/len_aim_p), int(aim_p[2]/len_aim_p)]
                # norma up vec
                norm_up_move = [int(up_p[0]/len_up_p), int(up_p[1]/len_up_p), int(up_p[2]/len_up_p)]
                # add norma vec to list
                aim_ver.append(norm_aim_move)
                aim_ver.append(norm_up_move)
                
                
                 
                # decomposition
                cmds.parent('WSpace_loc_aim_target_'+aim_obj,'WSpace_loc_aim_up_'+aim_obj,world=True)
                cmds.delete('WSpace_loc_aim_grp_'+aim_obj)
                cmds.parentConstraint(aim_obj, 'WSpace_loc_aim_target_'+aim_obj, weight=1.0, maintainOffset=True,
                name ='WSpace_loc_aim_target_'+aim_obj+'_parentConstraint' )
                cmds.parentConstraint(aim_obj, 'WSpace_loc_aim_up_'+aim_obj, weight=1.0, maintainOffset=True,
                name ='WSpace_loc_aim_up_'+aim_obj+'_parentConstraint')
                bake_obj.append('WSpace_loc_aim_target_'+aim_obj)
                bake_obj.append('WSpace_loc_aim_up_'+aim_obj)
        
        if len(bake_obj)>1:        
            cmds.bakeResults(bake_obj, time=(start_t, end_t), smart=(bake_frame, 0),
                                         simulation=False, preserveOutsideKeys=True, sparseAnimCurveBake=False,
                                         removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False,
                                         minimizeRotation=True, controlPoints=False, shape=True)
                                 
            for aim_obj in select_obj:
                cmds.delete('WSpace_loc_aim_target_' + aim_obj + '_parentConstraint', constraints=True)
                cmds.delete('WSpace_loc_aim_up_' + aim_obj + '_parentConstraint', constraints=True)
                #cmds.cutKey(aim_obj,clear=True,attribute='rx',time=(start_t,end_t))
                #cmds.cutKey(aim_obj,clear=True,attribute='ry',time=(start_t,end_t)) 
                #cmds.cutKey(aim_obj,clear=True,attribute='rz',time=(start_t,end_t)) 
                cmds.aimConstraint('WSpace_loc_aim_target_'+aim_obj,aim_obj,aimVector=aim_ver[0],upVector=aim_ver[1],
                                    maintainOffset=False,weight=1, worldUpType='object' , 
                                    name = aim_obj + '_aim_Constraint',worldUpObject='WSpace_loc_aim_up_'+aim_obj )
                                    
                aim_ver.pop(0)
                aim_ver.pop(0)
    
                                                                    
                                                                                                                            
        else:
            cmds.warning('The object has no aim locator')
    
    else:
            cmds.warning('Please select an object')  



#################################################    end    ######################################################

if __name__ == '__main__':
    wspace_loc_ui()


