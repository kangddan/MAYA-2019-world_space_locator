# -*- coding: utf-8 -*-
import sys
from maya      import cmds
from PySide2   import QtWidgets
from PySide2   import QtCore
from PySide2   import QtGui
from functools import partial
from maya.api  import OpenMaya as om2

class Utils(object):
    @classmethod
    def add_undo(cls, func):
        def undo(*args, **kwargs):
            cmds.undoInfo(openChunk=True)
            func(*args, **kwargs)
            cmds.undoInfo(closeChunk=True)
        return undo
    
    @classmethod
    def mayaWindow(cls):
        from maya.OpenMayaUI import MQtUtil
        from shiboken2       import wrapInstance
        if sys.version_info.major >= 3:
            return wrapInstance(int(MQtUtil.mainWindow()), QtWidgets.QMainWindow)
        else:
            return wrapInstance(long(MQtUtil.mainWindow()), QtWidgets.QMainWindow)

    @classmethod
    def obj_exists(cls, lst):
        '''
        Check if a list of objects exists one by one.
        return: True or False
               
        '''
        for i in lst:
            if not cmds.objExists(i):
                break
        else:
            return True

        return False

    @classmethod
    def get_norm_vec(cls, obj, get_type='t'):
        '''
        Normalize a vector.
        obj: Object to get the attribute from2.
        get_type: Specify the attribute to get from the object ('t', 'r', 's').
        return: Normalized vector.
        
        '''
        vec = om2.MVector(cmds.getAttr('{}.{}'.format(obj, get_type))[0])
        vec.normalize()

        return vec

    @classmethod
    def cond_switch(cls, lst, func):
        '''
        Evaluate multiple conditions and execute a dynamic function.
        lst: List of conditions.
        func: Function to be executed.
        
        '''
        for cond in lst:
            if cmds.objExists(cond):
                pass
            else:
                func()

    @classmethod
    def bake_obj(cls, obj, keys=True):
        '''
        Bake keyframes. The object needs to be constrained for this to work properly.
        obj: Object to be baked, can be a list.
        keys: Whether to bake every frame.
        
        '''
        start_key = cmds.playbackOptions(q=True, ast=True)
        end_key = cmds.playbackOptions(q=True, aet=True)
        if obj:
            cmds.bakeResults(obj, t=(start_key, end_key), sr=[keys, 0],
                             sm=False, pok=False, sac=False, ral=False,
                             bol=False, mr=True, cp=False, s=True)

    @classmethod
    def set_attr(cls, nodes, attrs, value):
        '''
        Add attributes to nodes.
        nodes: List of objects to add attributes to.
        attrs: List of attributes to be added.
        value: List of values to set for the attributes.
        
        '''
        for n in nodes:
            for ids, i in enumerate(attrs):
                if isinstance(value[ids], (list, tuple)):
                    cmds.setAttr('{}.{}'.format(n, i), *value[ids])
                else:
                    cmds.setAttr('{}.{}'.format(n, i), value[ids])

    @classmethod
    def lock_attr(cls, nodes, attrs, v=False):
        '''
        Lock attributes on nodes.
        nodes: List of objects to lock attributes on.
        attrs: List of attributes to be locked.
        v: Value for lock and keyable properties.
        
        '''
        if isinstance(nodes and attrs, list):
            if 't' in attrs:
                attrs.remove('t')
                attrs.extend(['tx', 'ty', 'tz'])
            if 'r' in attrs:
                attrs.remove('r')
                attrs.extend(['rx', 'ry', 'rz'])
            if 's' in attrs:
                attrs.remove('s')
                attrs.extend(['sx', 'sy', 'sz'])

            for n in nodes:
                for i in attrs:
                    cmds.setAttr('{}.{}'.format(n, i), l=False, k=False, cb=v)

    @classmethod
    def create_loc(cls, obj, prefix):
        '''
        Create a locator, get the object's rotate order, and hide a series of attributes.
        obj: The object to get the name from2.
        prefix: The prefix to be added.
        return: Locator object.
        
        '''
        ro = cmds.getAttr('{}.rotateOrder'.format(obj))
        loc = cmds.spaceLocator(n='{}{}'.format(prefix, obj))
        cmds.setAttr('{}.rotateOrder'.format(loc[0]), ro)

        cls.lock_attr([loc[0]], ['v', 'lpx', 'lpy', 'lpz', 'lsx', 'lsy', 'lsz'], v=False)
        return loc[0]

    @classmethod
    def scale_loc(cls, obj, value):
        '''
        Scale the locator.
        obj: The locator object.
        value: Scale value.
        
        '''
        try: 
            if cmds.nodeType(cmds.listRelatives(obj, s=True)[0]) == 'locator':
                x = cmds.getAttr('{}.{}'.format(obj, 'lsx'))
                Utils.set_attr([obj], ['lsx', 'lsy', 'lsz'], [x * value for i in range(3)])

            else:
                shapes = cmds.listRelatives(obj, s=True)
                for i in shapes:
                    points = cmds.ls(i + '.cv[*]')[0]
                    #     cmds.scale(*[value for i in range(3)], points, r=1, ocp=1)

                    cmds.scale(value, value, value, points, r=1, ocp=1)

        except:
            pass


class WorldSpaceLoc(object):

    def __init__(self):
        self.prefix = 'WSpace_loc_'

        self.aim_grp_prefix = 'WSpace_loc_aim_grp_'
        self.aim_prefix = 'WSpace_loc_aim_target_'
        self.up_prefix = 'WSpace_loc_aim_up_'

        self.parent_constr = '_parentConstraint'
        self.point_constr = '_pointConstraint'
        self.orient_constr = '_orientConstraint'
        self.aim_constr = '_aimConstraint'
        self.target_constr = 'target_aimConstraint'
        self.up_constr = 'up_aimConstraint'

    def bake_loc(self, every_frame):
        '''
        Bake the animation of the selected objects to locators.
        every_frame: Whether to bake every frame.
        
        '''
        s_lst = cmds.ls(sl=True)
        bake_lst = []

        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):
                    cmds.delete('{}{}'.format(self.prefix, obj))

                loc = Utils.create_loc(obj, self.prefix)
                bake_lst.append(loc)

                cmds.parentConstraint(obj, loc, w=1.0, mo=False)

            Utils.bake_obj(bake_lst, every_frame)
            cmds.delete(bake_lst, cn=True)
            cmds.select(s_lst)

    def parent_loc(self, offset):
        '''
        Parent the locators to the controllers using various constraint types.
        offset: Preserve offset.
        
        '''
        s_lst = cmds.ls(sl=True)

        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):

                    def constr_func():
                        cmds.parentConstraint('{}{}'.format(self.prefix, obj), obj, w=1.0, mo=offset,
                                              n='{}{}{}'.format(self.prefix, obj, self.parent_constr))

                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, self.parent_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.point_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.orient_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.aim_constr)):
                        pass
                    else:
                        constr_func()

    def point_loc(self, offset):
        '''
        Point constrain the locators to the controllers using various constraint types.
        offset: Preserve offset.
        
        '''
        s_lst = cmds.ls(sl=True)

        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):
                    # Check constraint types
                    def constr_func():
                        cmds.pointConstraint('{}{}'.format(self.prefix, obj), obj, w=1.0, mo=offset,
                                             n='{}{}{}'.format(self.prefix, obj, self.point_constr))

                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, self.point_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.parent_constr)):
                        pass
                    else:
                        constr_func()

    def orient_loc(self, offset):
        '''
        Orient constrain the locators to the controllers using various constraint types.
        offset: Preserve offset.
        
        '''
        s_lst = cmds.ls(sl=True)

        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):
                    # Check constraint types
                    def constr_func():
                        cmds.orientConstraint('{}{}'.format(self.prefix, obj), obj, w=1.0, mo=offset,
                                              n='{}{}{}'.format(self.prefix, obj, self.orient_constr))

                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, self.parent_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.orient_constr)):
                        pass
                    elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.aim_constr)):
                        pass
                    else:
                        constr_func()

    def select_loc(self):
        '''
        Select locators for the currently selected objects.
        
        '''
        s_lst = cmds.ls(sl=True)
        prefix_lst = [self.aim_prefix, self.up_prefix, self.prefix]

        loc_lst = []

        if s_lst:
            for obj in s_lst:
                for n in prefix_lst:
                    if cmds.objExists('{}{}'.format(n, obj)):
                        loc_lst.append('{}{}'.format(n, obj))

            cmds.select(loc_lst)

    def delete_constr(self):
        '''
        Delete world space constraints on selected objects.
        
        '''
        s_lst = cmds.ls(sl=True)
        constr_prefix_lst = [self.parent_constr, self.point_constr, self.orient_constr,
                             self.aim_constr]

        if s_lst:
            for obj in s_lst:
                for n in constr_prefix_lst:
                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, n)):
                        cmds.delete('{}{}{}'.format(self.prefix, obj, n), cn=True)
                        # Delete target constraints
                        if '{}{}{}'.format(self.prefix, obj, n) == '{}{}{}'.format(self.prefix, obj,
                                                                                   self.aim_constr):
                            cmds.delete('{}{}'.format(self.aim_prefix, obj),
                                        '{}{}'.format(self.up_prefix, obj))
                # Delete target constraint groups
                if cmds.objExists('{}{}'.format(self.aim_grp_prefix, obj)):
                    cmds.delete('{}{}'.format(self.aim_grp_prefix, obj))

    def bake_ctrl(self, every_frame):
        '''
        Bake the animation of the controllers and delete the constraints.
        every_frame: Whether to bake every frame.
        
        '''
        s_lst = cmds.ls(sl=True)
        bake_lst = []
        constr_lst = []

        # Target constraint components
        aim_lst = []

        # Constraint suffixes
        constr_prefix_lst = [self.parent_constr, self.point_constr, self.orient_constr,
                             self.aim_constr]

        if s_lst:
            for obj in s_lst:
                # Loop through constraint list
                for n in constr_prefix_lst:
                    # If the constraint exists
                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, n)):
                        bake_lst.append(obj)
                        constr_lst.append('{}{}{}'.format(self.prefix, obj, n))

                        # If it's the aim constraint, handle the two locators separately
                        if '{}{}{}'.format(self.prefix, obj, n) == '{}{}{}'.format(self.prefix, obj,
                                                                                   self.aim_constr):
                            aim_lst.extend(['{}{}'.format(self.aim_prefix, obj),
                                            '{}{}'.format(self.up_prefix, obj)])

            Utils.bake_obj(bake_lst, keys=every_frame)
            cmds.delete(constr_lst, cn=True)
            # Clean up aim constraint locators
            if aim_lst:
                cmds.delete(aim_lst)

    def scale_loc_add(self, num):
        '''
        Scale the locators by a given value.
        '''
        s_lst = cmds.ls(sl=True)
        if s_lst:
            for obj in s_lst:
                Utils.scale_loc(obj, num)

    def aim_loc(self):
        '''
        Create aim constraint locators. 
        
        '''
        s_lst = cmds.ls(sl=True)
        if s_lst:
            for obj in s_lst:

                if cmds.objExists('{}{}'.format(self.aim_grp_prefix, obj)):
                    pass
                elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.parent_constr)):
                    pass
                elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.aim_constr)):
                    pass
                elif cmds.objExists('{}{}{}'.format(self.prefix, obj, self.orient_constr)):
                    pass
                else:
                    aim_loc = Utils.create_loc(obj, self.aim_prefix)
                    up_loc = Utils.create_loc(obj, self.up_prefix)

                    grp = cmds.group(aim_loc, up_loc, n='{}{}'.format(self.aim_grp_prefix, obj))
                    cmds.parentConstraint(obj, grp, w=1.0, mo=False,
                                          n='{}{}{}'.format(self.prefix, obj, self.parent_constr))
                    cmds.select(aim_loc)

    def bake_aim(self, every_frame):
        '''
        Bake aim constraint locators and apply aim constraints.
        every_frame: Whether to bake every frame.
        
        '''
        s_lst = cmds.ls(sl=True)
        normal_lst = []
        bake_lst = []

        if s_lst:
            for obj in s_lst:
                if Utils.obj_exists(['{}{}'.format(self.aim_grp_prefix, obj), '{}{}'.format(self.aim_prefix, obj),
                                     '{}{}'.format(self.up_prefix, obj)]):
                    # Get the normalized vectors of the locators
                    normal_lst.append(Utils.get_norm_vec('{}{}'.format(self.aim_prefix, obj)))
                    normal_lst.append(Utils.get_norm_vec('{}{}'.format(self.up_prefix, obj)))

                    # Unparent the constraints
                    cmds.parent('{}{}'.format(self.aim_prefix, obj),
                                '{}{}'.format(self.up_prefix, obj), w=True)
                    cmds.delete('{}{}'.format(self.aim_grp_prefix, obj))

                    cmds.parentConstraint(obj, '{}{}'.format(self.aim_prefix, obj), w=1.0, mo=True,
                                          n='{}{}{}'.format(self.prefix, obj, self.target_constr))
                    cmds.parentConstraint(obj, '{}{}'.format(self.up_prefix, obj), w=1.0, mo=True,
                                          n='{}{}{}'.format(self.prefix, obj, self.up_constr))
                    bake_lst.extend(['{}{}'.format(self.aim_prefix, obj),
                                     '{}{}'.format(self.up_prefix, obj)])

                    Utils.bake_obj(bake_lst, every_frame)
                    cmds.delete('{}{}'.format(self.aim_prefix, obj), '{}{}'.format(self.up_prefix, obj), cn=True)

                    cmds.aimConstraint('{}{}'.format(self.aim_prefix, obj), obj, aim=normal_lst[0], u=normal_lst[1],
                                       mo=False, w=1.0, wut='object', wuo='{}{}'.format(self.up_prefix, obj),
                                       n='{}{}{}'.format(self.prefix, obj, self.aim_constr))

                    normal_lst = []
                    cmds.select(s_lst)

    def set_color(self, colorid):
        '''
        Batch set controller color.
        colorid: Color ID.
        
        '''
        s_lst = cmds.ls(sl=True)
        shape = cmds.listRelatives(s_lst, c=True)
        for obj in s_lst:

            if cmds.nodeType(obj) == 'joint':
                Utils.set_attr([obj], ['overrideEnabled', 'overrideColor'], [1, colorid])
                continue

            for s in shape:
                if cmds.objectType(s, isa='shape'):
                    Utils.set_attr([s], ['overrideEnabled', 'overrideColor'], [1, colorid])

class MyCheckBox(QtWidgets.QCheckBox):
    
    def __init__(self, text=None, parent=None):
        super(MyCheckBox, self).__init__(text=text, parent=parent)
        font = QtGui.QFont('marlett') 
        font.setPointSize(font.pointSize() * 1.2) 
        label = QtWidgets.QLabel('b', self)
        label.setFont(font)
        label.move(-5, -2)
        label.hide()
        self.clicked.connect(lambda : label.show() if self.isChecked() else label.hide())
        self.setStyleSheet("""

                        QCheckBox::indicator {
                        border: 3px solid #666666;  
                        border-radius: 3px;           
                        }
                        
                        QCheckBox::indicator:hover {
                        border: 3px solid #828282;              
                        }
                        
                        QCheckBox::indicator:checked {
                        background-color: #545A99;       
                        border: 0px;       
                        }
                        
                        QCheckBox::indicator:checked:hover {
                        background-color: #8289D9;      
                        border: 0px;             
                        }
                        
                        """ 
                        )
                        
class WSpaceWindow(QtWidgets.QDialog):
    SLIDER_BASIC_VALUE = 50
    
    dig_instance = None 
    @classmethod
    def show_window(cls):
        if not cls.dig_instance: 
            cls.dig_instance = WSpaceWindow()
            
        if cls.dig_instance.isHidden():
            cls.dig_instance.show() 
        else:
            cls.dig_instance.raise_()
            cls.dig_instance.activateWindow()
            
    def __init__(self, window_parent=Utils.mayaWindow()):
        super(WSpaceWindow, self).__init__(parent=window_parent)
        self.wsl = WorldSpaceLoc()
        self.setWindowTitle('World Space Locator')
        self.main_layout = QtWidgets.QVBoxLayout()
        if sys.version_info.major < 3:
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.main_layout.addLayout(self.check_box())
        self.main_layout.addLayout(self.bake_layout())
        self.main_layout.addLayout(self.loc_layout())
        self.main_layout.setSpacing(5)
        self.main_layout.addStretch()
        
        self.main_layout.setContentsMargins(4, 5,    4, 5)
        self.setLayout(self.main_layout)
        self.geometry = None 
        
    def showEvent(self, event):
        super(WSpaceWindow, self).showEvent(event)
        if self.geometry:
            
            self.restoreGeometry(self.geometry)
    
    def closeEvent(self, event): 
        if isinstance(self, WSpaceWindow): 
            super(WSpaceWindow, self).closeEvent(event)
            self.geometry = self.saveGeometry()
    
    def check_box(self):
                            
        self.Bake_check   = MyCheckBox('Bake Every Frame   ')
        
        self.Offset_check = MyCheckBox('Maintain Offset  ')
        #self.Offset_check.setLayoutDirection(QtCore.Qt.RightToLeft)
        
        self.check_ly = QtWidgets.QHBoxLayout()
        self.check_ly.addWidget(self.Bake_check)
        self.check_ly.addStretch()
        self.check_ly.addWidget(self.Offset_check)
        return self.check_ly
    ##########################  bake ly  #################################      
    def bake_layout(self):
        self.baake_ly = QtWidgets.QVBoxLayout()
        self.baake_ly.setSpacing(1)
        self.baake_ly.addLayout(self.bake_button())
        self.baake_ly.addLayout(self.aim_button())
        return self.baake_ly
          
    def bake_button(self):
        button_names = ['Bake Locators', 'Parent Locator', 
                        'Point Locator', 'Orient Locator']
        self.button_objs = [QtWidgets.QPushButton(name) for name in button_names]
        self.button_objs[0].setMinimumSize(0, 55)
        self.button_objs[1].setMinimumSize(0, 50)
        
        self.button_objs[0].setIcon(QtGui.QIcon(':holder.svg'))
        self.button_objs[1].setIcon(QtGui.QIcon(':parentConstraint.png'))
        self.button_objs[2].setIcon(QtGui.QIcon(':pointConstraint.svg'))
        self.button_objs[3].setIcon(QtGui.QIcon(':orientConstraint.svg'))
        
        self.button_objs[0].clicked.connect(self.bake_loc)
        self.button_objs[1].clicked.connect(self.parent_loc)
        self.button_objs[2].clicked.connect(self.point_loc)
        self.button_objs[3].clicked.connect(self.orient_loc)
        

        self.bake_button_ly = QtWidgets.QVBoxLayout()
        #self.bake_button_ly.setSpacing(2)
        for ids, button in enumerate(self.button_objs):
            self.bake_button_ly.addWidget(button)
            if ids in [0, 1]:
                button.setStyleSheet("color: rgb(255, 255, 136);") 
                  
        return self.bake_button_ly
        
    def aim_button(self):
        self.add_aim_loc = QtWidgets.QPushButton(QtGui.QIcon(':aimConstraint.png'), 'Aim Locator')
        self.bake_aim    = QtWidgets.QPushButton(QtGui.QIcon(':timeplay.png'), 'Bake Aim')

        
        self.add_aim_loc.clicked.connect(self.aim_loc)
        self.bake_aim.clicked.connect(self.bake_aim_loc)
        
        self.aim_ly = QtWidgets.QHBoxLayout()
        self.aim_ly.addWidget(self.add_aim_loc)
        self.aim_ly.addWidget(self.bake_aim)
        return self.aim_ly
        
        
    ##########################  bake ly  #################################   
    
    def loc_layout(self):
        self.loc_ly = QtWidgets.QVBoxLayout()
        self.loc_ly.setSpacing(1)
        self.loc_ly.addLayout(self.loc_button())
        self.loc_ly.addLayout(self.loc_attr())
        self.loc_ly.addLayout(self.bake_con())
        
        return self.loc_ly
        
    def loc_button(self):
        self.del_button = QtWidgets.QPushButton(QtGui.QIcon(':deleteClip.png'), 'Del Constraint')
        self.del_button.setMinimumSize(0, 50)
        self.sl_loc = QtWidgets.QPushButton(QtGui.QIcon(':locator.svg'), 'Select Locators')
        self.sl_loc.setMinimumSize(0, 50)
        
        self.del_button.clicked.connect(self.delete_constr)
        self.sl_loc.clicked.connect(self.select_loc)
        
        self.v_ly = QtWidgets.QVBoxLayout()
        self.v_ly.addWidget(self.del_button)
        self.v_ly.addWidget(self.sl_loc)
        return self.v_ly
        
    def loc_attr(self):
        input_style_sheet = """
                    QSlider::groove:horizontal {    
                        border: none;
                        height: 5px;                 
                        background-color: #1C1C1C;  
                    }

                    QSlider::handle:horizontal {      
                        background-color: #FFFFFF;   
                        width: 10px;                  
      
                        margin: -5px 0px -5px 0px;   
                        border-radius: 2px;
                    }

                    QSlider::sub-page:horizontal { 
                        background-color: #8289D9;
                    }
                    """
        basic_style_sheet = """
                    QSlider::groove:horizontal {     
                        border: none;
                        height: 5px;                
                        background-color: #1C1C1C;  
                    }

                    QSlider::handle:horizontal {      
                        background-color: #B4B4B4;    
                        width: 10px;                  
      
                        margin: -5px 0px -5px 0px;  
                        border-radius: 2px;
                    }

                    QSlider::sub-page:horizontal { 
                        background-color: #545A99;
                    }
                    """
        self.loc_attr_h_ly = QtWidgets.QHBoxLayout()
        self.loc_scale_text = QtWidgets.QLabel('  Loc Scale  ')
        
        self.loc_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.loc_scale_slider.setStyleSheet(basic_style_sheet)
        self.loc_scale_slider.enterEvent = lambda event: self.loc_scale_slider.setStyleSheet(input_style_sheet)
        self.loc_scale_slider.leaveEvent = lambda event: self.loc_scale_slider.setStyleSheet(basic_style_sheet)
        
        self.loc_scale_slider.setRange(0, 100)
        self.loc_scale_slider.setValue(50)
        
        self.loc_scale_slider.sliderPressed.connect(lambda: cmds.undoInfo(openChunk=True)) 
        
        self.loc_scale_slider.sliderMoved.connect(self.scale_loc_addaa) 
        
          
        self.loc_scale_slider.sliderReleased.connect(lambda: (self.loc_scale_slider.setValue(50), 
                                                              cmds.undoInfo(closeChunk=True)))
                                                              
                                                              
        self.loc_scale_slider.sliderReleased.connect(self.resete_slider_basic_value)                                                    
       
        
        self.loc_attr_h_ly.addWidget(self.loc_scale_text)
        self.loc_attr_h_ly.addWidget(self.loc_scale_slider)
        return self.loc_attr_h_ly
        
    def bake_con(self):
        self.info = QtWidgets.QLabel('World - Space - Locator - v1.6')
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.bake_button = QtWidgets.QPushButton(QtGui.QIcon(':bakeAnimation.png'), 'Bake Controls')
        self.bake_button.setStyleSheet("color: rgb(255, 255, 136);") 
        self.bake_button.setMinimumSize(0, 60)
        self.bake_button.clicked.connect(self.bake_ctrl)

        self.bake_con_v_ly = QtWidgets.QVBoxLayout()
        self.bake_con_v_ly.setSpacing(0)
        self.bake_con_v_ly.addWidget(self.bake_button)
        self.bake_con_v_ly.addWidget(self.info)
        return self.bake_con_v_ly

    @Utils.add_undo
    def bake_loc(self):
        bl = not bool(self.Bake_check.checkState())
        self.wsl.bake_loc(every_frame=bl)
        
    @Utils.add_undo
    def parent_loc(self):
        bl = bool(self.Offset_check.checkState())
        self.wsl.parent_loc(offset=bl)
        
    @Utils.add_undo
    def point_loc(self):
        bl = bool(self.Offset_check.checkState())
        self.wsl.point_loc(offset=bl)
        
    @Utils.add_undo
    def orient_loc(self):
        bl = bool(self.Offset_check.checkState())
        self.wsl.orient_loc(offset=bl)
        
    @Utils.add_undo
    def aim_loc(self):
        self.wsl.aim_loc()
        
    @Utils.add_undo
    def bake_aim_loc(self):
        bl = not bool(self.Bake_check.checkState())
        self.wsl.bake_aim(every_frame=bl)
        
    @Utils.add_undo
    def delete_constr(self):
        self.wsl.delete_constr()
        
    @Utils.add_undo
    def select_loc(self):
        self.wsl.select_loc()
        
    def resete_slider_basic_value(self):
        SLIDER_BASIC_VALUE = 50
    
    def scale_loc_addaa(self):
        slider_value = self.loc_scale_slider.value()
        
        if slider_value > WSpaceWindow.SLIDER_BASIC_VALUE:
            self.wsl.scale_loc_add(num=1.05)        
        
        elif slider_value < WSpaceWindow.SLIDER_BASIC_VALUE:
            self.wsl.scale_loc_add(num=1 / 1.05)
            
        WSpaceWindow.SLIDER_BASIC_VALUE = slider_value 
        
    @Utils.add_undo
    def bake_ctrl(self):
        bl = not bool(self.Bake_check.checkState())
        self.wsl.bake_ctrl(every_frame=bl)
        
if __name__ == '__main__':

    try:
        wswindow.close() # pylint: disable=E0601
        wswindow.deleteLater()
    except:
        pass
        
    wswindow = WSpaceWindow()
    wswindow.show()

            
