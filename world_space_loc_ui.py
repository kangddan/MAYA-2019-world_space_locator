# coding=utf-8
import sys
from functools import partial

import maya.api.OpenMaya as om
import maya.cmds as cmds


class Utils(object):
    
    
    @classmethod
    def obj_exists(cls, lst):
        '''
        接收一组列表对象，逐一检查对象是否存在 
        return: true or false
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
        向量标准化
        obj: 接收一个对象
        get_type: 指定需要获取改对象的属性来标准化('t','r','s')
        return： 标准化向量
        '''
        vec = om.MVector(cmds.getAttr('{}.{}'.format(obj,get_type))[0])
        vec.normalize()
        
        return vec
    
    @classmethod
    def cond_switch(cls, lst, func):
        '''
        用来判定多个条件，执行一段动态方法
        lst: 接收一组条件列表
        func: 接收一个函数
        '''
        for cond in lst:
            if cmds.objExists(cond):
                pass
            else:
                func()
                            
    @classmethod
    def bake_obj(cls, obj, keys=True):
        '''
        烘焙关键帧，对象需要被约束才能正常运行
        obj: 烘焙对象，可以是一组列表
        keys: 是否烘焙每一帧
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
        添加属性
        nodes: 接收一个列表，批量添加对象
        attrs：接收一个列表，批量设置属性
        value: 接收一个列表，批量设置参数
        '''     
        for n in nodes:
            for ids, i in enumerate(attrs):
                if isinstance(value[ids], (list, tuple)):
                    cmds.setAttr('{}.{}'.format(n,i), *value[ids]) # 如果是向量就解包
                else:
                    cmds.setAttr('{}.{}'.format(n,i), value[ids])
                                        
    @classmethod
    def lock_attr(cls, nodes, attrs, v=False):
        '''
        锁定属性
        nodes: 接收一个列表，批量添加对象
        attrs：接收一个列表，批量锁定属性
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
                    cmds.setAttr('{}.{}'.format(n,i), l=False, k=False, cb=v)
            
    @classmethod
    def create_loc(cls, obj, prefix):
        '''
        创建一个定位器，获取obj旋转顺序，并且隐藏一系列属性
        obj: 获取该对象命名
        prefix：添加前缀
        return： 定位器对象
        '''
        ro = cmds.getAttr('{}.rotateOrder'.format(obj))
        loc = cmds.spaceLocator(n='{}{}'.format(prefix, obj))
        cmds.setAttr('{}.rotateOrder'.format(loc[0]), ro)
        
        cls.lock_attr([loc[0]], ['v', 'lpx', 'lpy', 'lpz', 'lsx', 'lsy', 'lsz'], v=False)
        return loc[0]
            
    @classmethod
    def scale_loc(cls, obj, value):
        '''
        缩放定位器
        obj: 定位器对象
        value: 缩放值
        '''
        try: # 没有形状节点pass
            if cmds.nodeType(cmds.listRelatives(obj, s=True)[0]) == 'locator':
                x = cmds.getAttr('{}.{}'.format(obj, 'lsx'))
                Utils.set_attr([obj], ['lsx', 'lsy', 'lsz'], [x*value for i in range(3)])
                
            else:
                shapes = cmds.listRelatives(obj, s=True)
                for i in shapes:
                    points = cmds.ls(i + '.cv[*]')[0]
                    
                    # if sys.version_info.major >= 3:
                    #     cmds.scale(*[value for i in range(3)], points, r=1, ocp=1)
                    
                    cmds.scale(value,value,value, points, r=1, ocp=1)
            
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
        

    def bake_loc(self, every_frame, *args):
        '''
        烘焙所选对象动画到定位器
        every_frame： 是否烘焙每一帧
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
        定位器父子约束控制器，包含一系列约束判断
        offset: 保持偏移
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
        定位器点约束控制器，包含一系列约束判断
        offset: 保持偏移
        '''
        s_lst = cmds.ls(sl=True)

        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):
                    # 检查约束类型
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
        定位器旋转约束控制器，包含一系列约束判断
        offset: 保持偏移
        '''
        s_lst = cmds.ls(sl=True)
        
        if s_lst:
            for obj in s_lst:
                if cmds.objExists('{}{}'.format(self.prefix, obj)):
                    # 检查约束类型
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
        选择当前对象的定位器
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
 
            
    def delect_constr(self):
        '''
        删除所选对象wspace约束
        '''
        s_lst = cmds.ls(sl=True)
        constr_prefix_lst = [self.parent_constr, self.point_constr, self.orient_constr, 
                             self.aim_constr]
        
        if s_lst:
            for obj in s_lst:                
                for n in constr_prefix_lst:
                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, n)):
                        cmds.delete('{}{}{}'.format(self.prefix, obj, n), cn=True)
                        # 目标约束
                        if '{}{}{}'.format(self.prefix, obj, n) == '{}{}{}'.format(self.prefix, obj, 
                                                                                    self.aim_constr):
                            cmds.delete('{}{}'.format(self.aim_prefix, obj), 
                                        '{}{}'.format(self.up_prefix, obj))
                # 目标约束组
                if cmds.objExists('{}{}'.format(self.aim_grp_prefix, obj)):
                    cmds.delete('{}{}'.format(self.aim_grp_prefix, obj))


    def bake_ctrl(self, every_frame):
        '''
        烘焙控制器动画，删除约束
        every_frame： 是否烘焙每一帧
        '''    
        s_lst = cmds.ls(sl=True)
        bake_lst = []
        constr_lst = []
        
        # 目标约束各种组件
        aim_lst = []
        
        # 约束后缀
        constr_prefix_lst = [self.parent_constr, self.point_constr, self.orient_constr, 
                             self.aim_constr]
        
        if s_lst:
            for obj in s_lst:    
                # 遍历约束列表
                for n in constr_prefix_lst:
                    # 如果存在改约束
                    if cmds.objExists('{}{}{}'.format(self.prefix, obj, n)):
                        bake_lst.append(obj)
                        constr_lst.append('{}{}{}'.format(self.prefix, obj, n))
                        
                        # 如果是目标约束，单独处理两个定位器
                        if '{}{}{}'.format(self.prefix, obj, n) == '{}{}{}'.format(self.prefix, obj, 
                                                                                    self.aim_constr):
                            aim_lst.extend(['{}{}'.format(self.aim_prefix, obj), 
                            '{}{}'.format(self.up_prefix, obj)])
                        
            Utils.bake_obj(bake_lst, keys=every_frame)
            cmds.delete(constr_lst, cn=True)
            # 清理目标约束定位器
            if aim_lst:
                cmds.delete(aim_lst)


    def scale_loc_add(self):
        '''
        放大定位器
        ''' 
        s_lst = cmds.ls(sl=True)
        if s_lst:
            for obj in s_lst:
                Utils.scale_loc(obj, 1.3)
    
                    
    def scale_loc_sub(self):
        '''
        缩小定位器
        ''' 
        s_lst = cmds.ls(sl=True)
        if s_lst:
            for obj in s_lst:
                Utils.scale_loc(obj, 0.8)
        
     
    def aim_loc(self):
        '''
        创建目标约束定位器   
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
                    
                    grp = cmds.group(aim_loc, up_loc, n='{}{}'.format(self.aim_grp_prefix,obj))            
                    cmds.parentConstraint(obj, grp, w=1.0, mo=False,
                                              n='{}{}{}'.format(self.prefix, obj, self.parent_constr))
                    cmds.select(aim_loc)
                    
                    
    def bake_aim(self, every_frame):
        '''
        烘焙目标约束定位器，并且执行目标约束
        every_frame： 是否烘焙每一帧
        '''
        s_lst = cmds.ls(sl=True)
        normal_lst = []
        bake_lst = []
        
        if s_lst:
            for obj in s_lst:
                if Utils.obj_exists(['{}{}'.format(self.aim_grp_prefix, obj), '{}{}'.format(self.aim_prefix,obj), 
                                     '{}{}'.format(self.up_prefix,obj)]):
                    
                    # 获取定位器的标准化向量
                    normal_lst.append(Utils.get_norm_vec('{}{}'.format(self.aim_prefix,obj)))
                    normal_lst.append(Utils.get_norm_vec('{}{}'.format(self.up_prefix,obj)))
                    
                    # 解组约束
                    cmds.parent('{}{}'.format(self.aim_prefix,obj),
                                '{}{}'.format(self.up_prefix,obj), w=True)
                    cmds.delete('{}{}'.format(self.aim_grp_prefix, obj))
                    
                    cmds.parentConstraint(obj, '{}{}'.format(self.aim_prefix, obj), w=1.0, mo=True, 
                                          n='{}{}{}'.format(self.prefix, obj, self.target_constr))
                    cmds.parentConstraint(obj, '{}{}'.format(self.up_prefix, obj), w=1.0, mo=True, 
                                          n='{}{}{}'.format(self.prefix, obj, self.up_constr))
                    bake_lst.extend(['{}{}'.format(self.aim_prefix,obj), 
                                    '{}{}'.format(self.up_prefix,obj)])
                                    
                    Utils.bake_obj(bake_lst, every_frame)
                    cmds.delete('{}{}'.format(self.aim_prefix,obj), '{}{}'.format(self.up_prefix,obj), cn=True)
                    
                    cmds.aimConstraint('{}{}'.format(self.aim_prefix,obj), obj, aim=normal_lst[0], u=normal_lst[1], 
                                        mo=False, w=1.0, wut='object', wuo='{}{}'.format(self.up_prefix,obj), 
                                        n='{}{}{}'.format(self.prefix, obj, self.aim_constr))
                    
                    normal_lst = []
                    cmds.select(s_lst)
                                
    
    def set_color(self, colorid):  
        '''
        批量设置控制器颜色
        colorid： 颜色id
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


class WorldSpaceLocUi(object):
    def __init__(self):
        self.__name = 'World_Space_Locator'
        self.windows()
        self.layout()
        self.button()
    
    def windows(self):
        if cmds.window(self.__name, exists=1):
            cmds.deleteUI(self.__name)
        self.window = cmds.window(self.__name, rtf=1, w=280, h=280, t=self.__name, s=1)
        cmds.showWindow(self.__name)

    def layout(self):

        self.ly1 = cmds.columnLayout(rs=5, adj=1, p=self.window)
        self.ly2 = cmds.rowColumnLayout(nc=2, adj=1, p=self.ly1)
        self.ly3 = cmds.rowColumnLayout(nc=1, adj=1, p=self.ly1)
        self.ly4 = cmds.rowColumnLayout(nc=1, adj=1, p=self.ly1)
        
        self.button_test1()
        
        self.ly5 = cmds.rowColumnLayout(nc=2, adj=2, p=self.ly4)     
        self.ly6 = cmds.rowColumnLayout(nc=1, adj=1, p=self.ly1)
       
        self.button_test2()       
       
        self.ly7 = cmds.frameLayout(l='Color Picker', cll=True, cl=True, p=self.ly6)
        self.ly8 = cmds.rowColumnLayout(nc=9, adj=5, p=self.ly7)
        
        self.ly9 = cmds.rowColumnLayout(nc=2, adj=2, p=self.ly6 )
        self.ly10 = cmds.rowColumnLayout(nc=1, adj=1, p=self.ly1)

    
    # 要定义一个方法才能正确的放置按钮顺序
    def button_test1(self):
        cmds.button(l='Parent Locator', h=40, c=self.parent_loc, p=self.ly4, ann='添加父子约束')
        cmds.button(l='Point Locator', h=25, c=self.point_loc, p=self.ly4, ann='添加点约束')
        cmds.button(l='Orient Locator', h=25, c=self.orient_loc, p=self.ly4, ann='添加旋转约束')
    # 同上
    def button_test2(self):
        cmds.button(l='Delete Constraint', h=40, c=self.delect_constr, p=self.ly6, ann='删除约束')
        cmds.button(l='Select Locators', h=50, c=self.select_loc, p=self.ly6, ann='选择所属定位器')
        
    def button(self):
        self.every_frames_bool = cmds.checkBox(l='Smart Bake', v=False, p=self.ly2, ann='是否烘焙每一帧')
        self.offset_con = cmds.checkBox(l='Maintain Offset', v=False, p=self.ly2, ann='约束是否保持偏移')

        cmds.button(l='Bake Locators', h=40, c=self.bake_loc, p=self.ly3,ann='烘焙一个定位器')
        
        cmds.button(l='Aim Locator', w=115, h=25, c=self.aim_loc, p=self.ly5, ann='添加目标约束定位器')
        cmds.button(l='Bake Aim', w=115, h=25, c=self.bake_aim, p=self.ly5, ann='目标约束到对象')

        color_lis=[(1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0), 
                    (0.0, 1.0, 0.0), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), 
                    (1.0, 0.5, 0.5), (0.75, 0.75, 0.75), (1.0, 1.0, 1.0)]
        null_id = []
        for idd,i in enumerate(range(1,10)):
            id = cmds.button(l='ID'+str(idd+1), w=26, h=20, bgc=color_lis[idd], p=self.ly8)
            null_id.append(id)
            
        color_index=[13,24,17,14,18,6,20,3,16]
        for idd,i in enumerate(range(1,10)):
            id = cmds.button(null_id[idd], edit=True, c = partial(self.set_color, color_index[idd]), p=self.ly8, ann='设置颜色')
            
        cmds.button(l='locator  +  ', w=115, h=35, c=self.scale_loc_add, p=self.ly9, ann='缩放控制器')
        cmds.button(l='locator  -  ', w=115, h=35, c=self.scale_loc_sub, p=self.ly9, ann='缩放控制器')
        

        cmds.button(l='Bake Controls', h=40, c=self.bake_ctrl, p=self.ly10, ann='烘焙控制器动画')
        cmds.text(label='World - Space - Locator - v1.5', w=40, h=13, p=self.ly10)
        

    
    
    def bake_loc(self, *args):
        keys = not cmds.checkBox(self.every_frames_bool, q=True, value=True)
        WorldSpaceLoc().bake_loc(every_frame=keys)
        
    def parent_loc(self, *args):
        keys = cmds.checkBox(self.offset_con, q=True, value=True)
        WorldSpaceLoc().parent_loc(offset=keys) 
    
    def point_loc(self, *args):
        keys = cmds.checkBox(self.offset_con, q=True, value=True)
        WorldSpaceLoc().point_loc(offset=keys)
        
    def orient_loc(self, *args):
        keys = cmds.checkBox(self.offset_con, q=True, value=True)
        WorldSpaceLoc().orient_loc(offset=keys)  
    
    def aim_loc(self, *args):
        WorldSpaceLoc().aim_loc()
        
    def bake_aim(self, *args):
        keys = not cmds.checkBox(self.every_frames_bool, q=True, value=True)
        WorldSpaceLoc().bake_aim(every_frame=keys) 
    
    def delect_constr(self, *args):
        WorldSpaceLoc().delect_constr()
    
    def select_loc(self, *args):
        WorldSpaceLoc().select_loc() 
    
    def scale_loc_add(self, *args):
        WorldSpaceLoc().scale_loc_add()
    
    def scale_loc_sub(self, *args):
        WorldSpaceLoc().scale_loc_sub() 
    
    def bake_ctrl(self, *args):
        keys = not cmds.checkBox(self.every_frames_bool, q=True, value=True)
        WorldSpaceLoc().bake_ctrl(every_frame=keys)
    
    def set_color(self, colorid, *args):
        WorldSpaceLoc().set_color(colorid)

            
if __name__ == '__main__':         
    WorldSpaceLocUi()

