'''Module of procedures and variables for general Maya usage. 

   The idea behind this module is to make a lot of complex and commonly used 
   procedures in one file to be used in any of my own scripting projects.
   
   For example, a very useful procedure is 'soft_selection' which returns the
   names of the vertices selected with soft select.
   
       >>> import maya.cmds as cmds
       >>> pPlane = cmds.polyPlane(w=48, h=48, sx=24, sy=24)
       >>> cmds.softSelect(sse=1, ssr=True, ssd=2.5)
       >>> cmds.select('%s.vtx[240]' % pPlane[0])
       >>> verts = soft_selection()
       >>> verts[:3]
       [u'|pPlane1.vtx[215]', u'|pPlane1.vtx[239]', u'|pPlane1.vtx[240]']
       >>> # clean up
       >>> cmds.delete(pPlane)
       
    To test/execute the examples in the module documentation make sure that 
    you have an empty scene first, then once you have imported the 
    mayaFuncs module:
    import doctest
    nfail, ntests = doctest.testmod(mayaFuncs)
    
'''

import time
import random as rand

try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    import maya.mel as mel
except:
    pass

from multi_key_dict import multi_key_dict

uAll_NODES = cmds.allNodeTypes()

uALL_SHADING_NODES = cmds.listNodeTypes('shader') + \
                     cmds.listNodeTypes('texture') + \
                     cmds.listNodeTypes('light') + \
                     cmds.listNodeTypes('postProcess') + \
                     cmds.listNodeTypes('utility')
                     
UNPACK_TYPES = [u'short2', u'short3', u'long2', u'long3', u'float2', u'float3',
                u'double2', u'double3', u'matrix', u'pointArray', 
                u'vectorArray', u'stringArray', u'cone', u'reflectanceRGB', 
                u'spectrumRGB', u'componentList']

PACKED_TYPES = [u'Int32Array', u'doubleArray', u'attributeAlias']

TIME_VALS = ['hour','min','sec','millisec','game','film',
             'pal','ntsc','show','palf','ntscf']

SSELECT_CURVES = multi_key_dict()
SSELECT_CURVES['soft', 0] = '1,0,2, 0,1,2'
SSELECT_CURVES['medium', 1] = '1,0.5,2, 0,1,2, 1,0,2'
SSELECT_CURVES['linear', 2] = '0,1,0, 1,0,1'
SSELECT_CURVES['hard', 3] = '1,0,0, 0,1,0'
SSELECT_CURVES['crater', 4] = '0,0,2, 1,0.8,2, 0,1,2'
SSELECT_CURVES['wave', 5] = '1,0,2, 0,0.16,2, 0.75,0.32,2, 0,0.48,2,' \
                            '0.25,0.64,2, 0,0.8,2, 0,1,2'
SSELECT_CURVES['stairs', 6] = '1,0,1, 0.75,0.25,1, 0.5,0.5,1, 0.75,0.25,1,' \
                            '0.25,0.75,1, 1,0.249,1, 0.749,0.499,1,' \
                            '0.499,0.749,1'
SSELECT_CURVES['ring', 7] = '0,0.25,2, 1,0.5,2, 0,0.75,2'
SSELECT_CURVES['sine', 8] = '1,0,2, 0,0.16,2, 1,0.32,2, 0,0.48,2,' \
                             '1,0.64,2, 0,0.8,2, 0,1,2'
                             
SHADER_NODE_FLAGS = {'asLight': bool, 'asPostProcess': bool, 
                     'asRendering': bool, 'asShader': bool, 'asTexture': bool, 
                     'asUtility': bool, 'name': str, 'parent': str}
    
def find_empty_entry_value(eList):
    '''Used to find an empty value in an entry list used in Maya. This is 
    primarily used for ramp colour entry lists and used so that excess entries
    are not created in an entry list
    
    Parameters:
        eList [tuple] : This is a list of the current index entry values. This 
                        value can be found using 
                        "cmds.getAttr('%s.colorEntryList' % ramp, mi=True)"
    
    On Exit:
        Returns the int of the lowest available entry value for the entry list.
        
    '''
    if eList[0] != 0:
        return 0
    else:
        for i in range(1, len(eList)):
            if eList[i-1]+1 != eList[i]:
                return eList[i-1]+1
        else:
            return len(eList)


def closest_colour(colour, cColours):
    '''Used to compare a list of colours to one colour and returns the colour
    that matches it the most.
    
    Parameters:
        colour [tuple]   : A 3 tuple float value containing the RGB values for
                           the colour. This is the colour that the other 
                           colours will be compared to.
        cColours [tuple] : A tuple of 3 tuple float RGBs that will be compared 
                           to the 'colour'
    
    On Exit:
        Returns the 3 tuple of the colour that most closly matches 'colour 
        from the tuple 'cColours'
        
    '''
    compare = [sum([abs(colC[i]-colour[i]) for i in range(3)]) for colC in cColours]
    return cColours[compare.index(min(compare))]


def setup_graph_values(gVals):
    '''Used to organise string graph values to then be stored in a Maya Option 
    Variable.
    
    Parameters:
        gVals [str] : A string returned from or used by a graph. This can
                      be a value from a soft select curve or any other
                      curve values. The formatting is 
                      ouput,input,interpolation all being int values in a 
                      string. See the dictionary SSELECT_CURVES for an example.
    
    On Exit:
        Returns a list with each curve point stored in a separate string.
    
    '''
    split = gVals.split(',')
    return [','.join(split[i:i+3]).strip() for i in range(0,len(split),3)]


def setup_key_frames(node, attr, vals, fp=0):
    '''Used to setup a list of values to a nodes attribute and keyframe them 
    with optional padding.
    
    Parameters:
        node [str]   : The name of the node or object to which the attribute
                       'attr' applies to.
        attr [str]   : The name of the attribute to which all the values will
                       be assigned to.
        vals [tuple] : This is a list of values to be assigned to the 
                       attribute.
        fp [int]     : The number of frames in-between each of the keyframes
                       for which the values will be set to.
                       
    On Exit:
        Sets the values to the nodes attribute and keyframes it. It will also
        framepad for any value higher then 0.
    
    '''
    if isinstance(vals, (tuple,list)):
        for i in range(len(vals)):
            if fp >= 1:
                time = (1+fp)*i+1
            else:
                time = 1+i
            cmds.setKeyframe(node, time=time, attribute=attr,
                            value=vals[i])
    else:
        raise ValueError('%s is not a list or tuple type' % vals)

   
def mel_file_import(name):
    '''Used to import mel scripts into the Maya scene so they can be used by 
    the programming for use later.
    
    Parameters:
        name [str] : The name of the source script inside the Maya directory
                     to be imported.
    
    On Exit:
        The Maya script will be imported into the scene.
        
    '''
    mel.eval('source %s.mel' % name)


def poly_check(dagObj):
    '''Used to check if the specified object is a polygon object.
    
    Parameters:
        dagObj [str] : The name of the DAG object from the scene.
    
    On Exit:
        Returns True if the object is a polygon object. Else, it returns False.
        
    '''
    return True if cmds.listRelatives(dagObj, type='mesh') != None else False


def fit_to_group_bbox(obj, group):
    '''Used to scale and translate a 3d placement node used for 
    onto the size of a group or object.
    
    Parameters:
        obj [str]   : is the name of the object or projection you want to 
                      resize
        group [str] : is the name of the object or group (usually Shading 
                      Group) from which the bounding box will be retrieved and 
                      that will be used to fit to.
                      
    On Exit: 
        The "obj" is resized to the exact world bounding box of "group"
    '''
    bbox = cmds.exactWorldBoundingBox(group)
    scl = []
    trn = []
    for i in range(3):
      scl.append(float( (bbox[i+3] - bbox[i]) ) / 2)
      trn.append(float( (bbox[i+3] + bbox[i]) ) / 2)
    cmds.setAttr(*['%s.scale' % obj]+scl, type='double3')
    cmds.setAttr(*['%s.translate' % obj]+trn, type='double3')


def get_obj_attr(obj, **kwargs):
    '''Creates a dictionary of attributes and values for an object. Mainly
    used to query an attributes value and type for ease of scripting.

    Parameters:
        obj [str] : Is the name of the object or node you want the current 
                    attributes, values and type from.
        **kwargs  : The keyword parameters for the function 'cmds.listAttr'.
                    This is so all the object attributes listed are retrieved 
                    from the object.
                       
    On Exit: return a dictionary with 'dict[attribute]' = 'dict[value]'
            and 'dict[type]'
              
    '''
    if kwargs.has_key('shortNames'):
        shortNames=kwargs['shortNames']
        del(kwargs['shortNames'])
    elif kwargs.has_key('sn'):
        shortNames=kwargs['sn']
        del(kwargs['sn'])
    else:
        shortNames=False
    
    ls = cmds.listAttr(obj, **kwargs)
    if shortNames:
        kwargs['sn'] = True
        ls += cmds.listAttr(obj, **kwargs)
        
    attrVals = {}
    for atr in ls:
        try:
            attrVals[atr] = {'value': cmds.getAttr('%s.%s' %(obj,atr)), 
                             'type': cmds.getAttr('%s.%s' %(obj,atr), type=True)}
        except RuntimeError:
            attrVals[atr] = {'value': 'Mixed Type Elements', 
                             'type': cmds.getAttr('%s.%s' %(obj,atr), type=True)}
        except ValueError:
            pass
    return attrVals


def set_attributes(obj, **kwargs):
    '''Used to set multiple attributes of a single object with ease instead of
    continuously writing out lines of code.
    
    Parameters:
        obj [str] : The name of the object to which you wish to set attributes
                    to.
        **kwargs  : Any name of the an attribute followed by the value to 
                    assign.
    On Exit:
        Sets the attributes specified with the specified values to the object.
    
    '''
        
    defaultVals = get_obj_attr(obj, read=True, write=True, multi=True, 
                               shortNames=True)
    checkAttr = list(set(kwargs) - set(defaultVals))
    if checkAttr != []:
        raise ValueError('%s are not attribute(s) that can be applied to the '
                         'shader.'%str(checkAttr)[1:-1])
        
    for key,value in kwargs.items():
        print key,value
        if defaultVals[key]['type'] in UNPACK_TYPES:
            cmds.setAttr('%s.%s' %(obj, key), *value, 
                         type=defaultVals[key]['type'])
        elif defaultVals[key]['type'] in PACKED_TYPES or \
        not(isinstance(value, (int,float,long))):
            cmds.setAttr('%s.%s' %(obj, key), value, 
                         type=defaultVals[key]['type'])
        else:
            cmds.setAttr('%s.%s' %(obj, key), value)

def check_shader_node(sNode):
    '''Checks if the named node is a shading node.

    Parameters:
        sNode [str] : The name of the shading node.
        
    On Exit:
        Returns True if 'sNode' is a shader node, else returns False
        
    '''
    return True if unicode(sNode) in uALL_SHADING_NODES else False
        

def create_shader_node(node, flags=False, **kwargs):
    '''Combines the creation of a node with the setting of attributes of the 
    newly created shader.
    
    Parameters:
        node [str]   : The name of the shading node type. An example of this is
                       'lambert'
        flags [bool] : If True, then the node will not be created but the flags
                       for the node type will be returned instead.
        **kwargs     : Combining both the nodes for creating a shader node and
                       the setting of attributes. The flags for creating the
                       shader are as follows: 
                       {'asLight': bool, 'asPostProcess': bool, 
                       'asRendering': bool, 'asShader': bool, 
                       'asTexture': bool, 'asUtility': bool, 'name': str, 
                       'parent': str}
    
    On Exit:
        Creates the shader node, sets the specified attributes and returns
        the name of the shader
        
    '''
    tempNode = cmds.shadingNode(node, asShader=True)
    
    defaultNodeFlags = get_obj_attr(tempNode,read=True, write=True, multi=True, 
                                    shortNames=True)
    cmds.delete(tempNode)
    del(tempNode)
    if flags:
        return defaultNodeFlags
    
    usedShaderFlags = {}
    setNodeFlags = {}
    
    for k,v in kwargs.items():
        if SHADER_NODE_FLAGS.has_key(k):
            if not(isinstance(v,SHADER_NODE_FLAGS[k])):
                raise ValueError('Value %s for %s is incorrect. It should be a'
                                 '%s type' % (k,v,SHADER_NODE_FLAGS[k]))
            else:
                usedShaderFlags[k] = v
        elif defaultNodeFlags.has_key(k):
            setNodeFlags[k] = v
        else:
            raise ValueError('%s is not a valid parameter for the function' 
                             % k)
                
    shader = cmds.shadingNode(node, **usedShaderFlags)
    
    set_attributes(shader, **setNodeFlags)
                
    return shader

def create_shading_group(shdrName, name=None):
    '''Creates a shading group for the specified shader. 
    
    Parameters:
        shdrName [str] : The name of the shader in the scene.
        name [str]     : The name you wish to give the new shader (followed by
                         'SG' for 'Shading Group'
                         
    On Exit:
        Returns the name of the shading group.
        
    '''
    if name == None:
        shaderGroup = cmds.sets(shdrName, renderable=True, 
                                noSurfaceShader=True, empty=True, 
                                name='%sSG' % shdrName)
    else:
        shaderGroup = cmds.sets(shdrName, renderable=True, 
                                noSurfaceShader=True, empty=True, 
                                name= name)
    return shaderGroup

def list_connectable_attributes(node):
    '''Lists the possible connectable attributes for a node.
    
    Parameters:
        node [str] : The name of the node in the scene.
        
    On Exit:
        Returns a list of the attributes that can be connected to and/or from
        the node.
        
    '''
    return cmds.listAttr(node, connectable=True, multi=True) + \
           cmds.listAttr(node, connectable=True, shortNames=True, multi=True)
           

def connect_attributes(iObject, oObject, *args):
    '''Used to connect multiple attributes from two objects with ease 
    instead of continuously writing out lines of code for each attribute.
    
    Parameters:
        iObject [str] : The name of the input object for which the attributes
                        will be input from
        oObject [str] : The name of the output object for which the input
                        attributes will be input into.
        *args [tuple] : A tuple of 2 tuple string attributes for connecting.
                        The first being the input, the second being the output.
                        
    On Exit:
        Connects any possible attributes from the 'iObject's value to the 
        'oObjects's value.
        
    '''
    
    if isinstance(args[0], (str,unicode)):
        args = (args,)
    for i,o in args:
        try:
            cmds.connectAttr('%s.%s' % (iObject, i),
                                 '%s.%s' % (oObject, o))
        except RuntimeError:
            print ('Unable to connect "%s.%s" to "%s.%s".' 
                    % (iObject, i, oObject, o))
    
def get_vertex_normals(pObject):
    '''Gathers all the normal directions for all the vertices of a poly object.
    
    Parameters:
        pObject [str] : The name of a polygonal object from the scene.
    
    On Exit:
        Returns a list of all the vertex normals, averaged from each adjacent
        face normal.
    
    '''
    lsVtxNormals = []
    nVtx = cmds.polyEvaluate(pObject, vertex=True)
    for i in range(nVtx):
        xyzNorm = cmds.polyNormalPerVertex('%s.vtx[%d]' % (pObject, i), q=True, xyz=True)
        vtxNormal = [sum([xyzNorm[i] for i in range(0+x, len(xyzNorm), 3)]) / \
                     (len(xyzNorm)/3) for x in range(3)]
        lsVtxNormals.append(vtxNormal)
    return lsVtxNormals
    
def point_positions(pObject):
    '''Finds the location of all the vertex points of a polygonal object in
    world space.
    
    Parameters:
        pObject [str] : The name of a polygonal object from the scene.
    
    On Exit:
        Returns a list of all the vertex point positions of the object.
        
    '''
    nOfVerts = cmds.polyEvaluate(pObject, vertex=True)
    return [cmds.pointPosition('%s.vtx[%d]' % (pObject,i), w=True) \
            for i in range(nOfVerts)]
  
def soft_selection():
    '''Returns the currently selected or influenced vertex points from the use
    of soft select.
    
    Parameters:
        In Maya, soft select must be enabled and used to select an object.
        Otherwise, the result will be an empty list.
        
    On Exit:
        Returns a list of all the vertices in range or influence by the soft
        selects rolloff distance and curve.
        
    '''
    selection = om.MSelectionList()  
    softSelection = om.MRichSelection()  
    om.MGlobal.getRichSelection(softSelection)  
    softSelection.getSelection(selection)  
      
    dagPath = om.MDagPath()  
    component = om.MObject()  
    
    itr = om.MItSelectionList(selection,om.MFn.kMeshVertComponent)  
    
    elements = []  
    while not itr.isDone():   
        itr.getDagPath(dagPath, component)  
        dagPath.pop()  
        node = dagPath.fullPathName()  
        fnComp = om.MFnSingleIndexedComponent(component)     
                  
        for i in range(fnComp.elementCount()):  
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))  
        itr.next()  
    return elements  

def apply_shader(shdrGroup, objs):
    '''Applies a shader to a object or list of objects

    Parameters:
        shdrGroup [str] : is the name of the Shader Set used to apply the 
                          shader to an object.
        objs [tuple]    : can be the name or list names of objects that the
                          shader will be applied to.
                    
    On Exit: 
        The object is added to the shader group connected to the shader.
              
    '''
    cmds.select(objs, replace=True)
    cmds.sets(forceElement=shdrGroup)
    
    