r'''Module of procedures and variables for creating terrain from music. 

   The idea behind this module is to make a deform polyagonal objects from 
   the song amplitudes from wave music files. There is also a function to 
   create custom terrain from a selection of image files in the 'TEX_DIRECTORY'.
   
   If this code is run from the Maya terminal, then the example code at the 
   bottom of this code will be run. For testing purposes, it an examaple has
   also been placed here.
   
       >>> import maya.cmds as cmds
       >>> import terrainWave as tw
       >>> obj = cmds.polyPlane(name='terraign', w=24, h=24, sx=30, sy=70)
       >>> befBbox = cmds.exactWorldBoundingBox(obj[0])
       >>> #change musicLocation to a song in your directory to test the functions
       >>> song = 'D:\\Users\\Jon\\workspace\\Terraign Generator\\01 Window.wav'
       >>> songInfo = tw.TerrainWaveFile(song)
       >>> music_displace(songInfo, 4, obj[0], vtxDire='y')
       >>> befBbox != cmds.exactWorldBoundingBox(obj[0])
       True
       >>> tInfo = create_texture('arid')
       >>> assign_terrain_shader(tInfo['lambert'][1], obj[0], tInfo['placements'])
       >>> cmds.select(tInfo['lambert'][1])
       >>> appObj = cmds.ls(selection=True)
       >>> appObj == cmds.listRelatives(obj[0], shapes=True)
       True
       >>> # cleanup
       >>> cmds.file(f=True, new=True)
       >>>
       
    To test/execute the examples in the module documentation make sure that 
    you have an empty scene first, then once you have imported the 
    mayaFuncs module:
    import doctest
    nfail, ntests = doctest.testmod(mtgMain)
    
'''


import os
import random as rand

try:
    import maya.cmds as cmds
    import mayaSnippet.mayaFuncs as mf
    import maya.utils as mu
    mf.mel_file_import('AEplace3dTextureTemplate')  
except:
    print 'ERROR importing modules'
    
import terrainWave as tw

FILE_DIR = os.path.abspath(__file__)
MTG_DIRECTORY = os.path.split(FILE_DIR)[0]
TEX_DIRECTORY = os.path.join(MTG_DIRECTORY, 'textures')
CLIFF_TEX_DIR = os.path.join(TEX_DIRECTORY, 'cliff_Textures')
GRASS_TEX_DIR = os.path.join(TEX_DIRECTORY, 'grass_Textures')

class COLOUR_SPACES:
    linear = 1
    srgb = 2

COLOUR_SPACE_VALUES = {1: 1.0, 2: 2.2}



def terrain_random_noise():
    '''Creates a random noise texture which is most effective at creating and 
    blending layered textures.
    
    On Exit:
        Creates and returns the noise and place2dTexture node
        
    '''
    noise = mf.create_shader_node('noise', asTexture=True, ratio=rand.random(),
                               frequencyRatio=rand.uniform(1, 10), 
                               depthMax=rand.randint(1,8), time=rand.random(),
                               frequency=rand.uniform(2,15), 
                               spottyness=rand.random(), 
                               sizeRand=rand.random(), 
                               falloff=rand.randint(0,2))
    noise2d = mf.create_shader_node('place2dTexture', asUtility=True)
    cmds.defaultNavigation(ce=True, source=noise2d, destination=noise)
    return (noise, noise2d)


def create_file_node(imgLoca, name, uRep, vRep, uNoise, vNoise):
    '''Creates a file node for an image in a directory and apply options to
    it.
    
    Parameters:
        imgLoca [str]  : The image location on the disc drive. Should be in the
                         format that is created by 'os.path.abspath'.
        name [str]     : The name of the file node.
        uRep [float]   : The number of repetitions of the texture in the U-axis 
                         (Y).
        vRep [float]   : The number of repetitions of the texture in the V-axis
                         (X).
        uNoise [float] : The amplitude of the noise effect on the texture in 
                         the U-axis (Y).
        vNoise [float] : The amplitude of the noise effect on the texture in 
                         the V-axis (X).
    On Exit:
        Creates a file and file2d texture from the 'imgLoca' with the options 
        in the parameters. It is then returned in a tuple at the end of the
        function.
    '''
    file_ = mf.create_shader_node('file', asTexture=True, name=name, 
                                  fileTextureName=imgLoca, filterType=1)
    file2d = mf.create_shader_node('place2dTexture', asUtility=True, 
                                   repeatU=uRep, repeatV=vRep, noiseU=uNoise, 
                                   noiseV=vNoise)
    cmds.defaultNavigation(ce=True, source=file2d, destination=file_)
    return (file_,file2d)

def tex_types(texType, nOfTexs=1, randTexs=False):
    '''Finds and collects the relevant texture file locations from the texture
    directories.
    
    Parameters:
        texType [tuple] : 2 tuple str of texture type folder followed by 
                          category e.g. ("cliff_textures", "arid")
        nOfTexs [int]   : The number of textures to be used by the material.
                          If the number is greater then the number in the
                          directory, then repeat textures will be used.
        randTexs [bool] : If True, textures from all the directory type will be
                          used. For example, if the texType had its first entry
                          be "cliff_textures", then textures will be used from
                          all available files in that folder.
    
    On Exit:
        Stores and returns 'nOfTexs' random texture locations of the specific 
        texture type.
    '''
    texPath = os.path.join(TEX_DIRECTORY, *texType)
    if not(os.path.exists(texPath)):
        return ValueError('%s path doesn\'t exist' % texPath)
    textures  = []
    if randTexs:
        texPath = os.path.join(TEX_DIRECTORY, texType[0])
        for root, _, filenames in os.walk(texPath):
            if os.path.split(root)[1] == '.mayaSwatches':
                continue
            textures.extend([os.path.join(root,f) for f in filenames])
    else:
        textures = [os.path.join(texPath,f) for f in os.listdir(texPath)\
                    if os.path.isfile(os.path.join(texPath,f))]
        
    if len(textures) < nOfTexs:
        print 'The number of textures supplied is fewer then the' \
        ' requested amount. Repeat textures will be used'
    
    tmpTexs = textures[:]
    texturesUsed = {}
    for x in range(nOfTexs):
        if tmpTexs == []:
            tmpTexs = textures[:]
        i = rand.randint(0, len(tmpTexs)-1)
        image = tmpTexs.pop(i)
        if texturesUsed.has_key(image):
            texturesUsed[image].append(x)
        else:
            texturesUsed[image] = [x]
    return texturesUsed
        

def create_files(imgLocations, lTexture, nOfTexs, name, uRep, vRep, uNoise, 
                 vNoise):
    '''Creates all the file node from the imgLocations and combine it into a
    layered texture using noise as alphas.
    
    Parameters:
        imgLocations [str] : A list of image locations for all the images that
                             will be used in a single layer texture.
        lTexture [str]     : The name of the layered texture which will hold
                             all the images.
        nOfTexs [int]      : This is the number of  textures that will be 
                             used.
        name [str]         : This is the name of the file nodes that will be 
                             created.
        uRep [float]       : The number of repetitions of the file texture in 
                             the U-axis (Y).
        vRep [float]       : The number of repetitions of the file texture in 
                             the V-axis (X).
        uNoise [float]     : The amplitude of the noise effect on the file 
                             texture in the U-axis (Y).
        vNoise [float]     : The amplitude of the noise effect on the file 
                             texture in the V-axis (X).
                             
    On Exit:
        Returns a list of all the file info in the format of (fInfo, noise)
        with both being a 2 tuple of their respective node and place2dTexture
        node.
    
    '''
    allFiles = []
    for x, (img,positions) in enumerate(imgLocations.items()):
        fInfo = create_file_node(img, name+str(x), uRep, vRep, uNoise, vNoise)
        for pos in positions:
            mf.connect_attributes(fInfo[0], lTexture, 
                                 ('outColor', 'inputs[%d].color' % pos))
            if x < nOfTexs-1:
                noise = terrain_random_noise()
                mf.connect_attributes(noise[0], lTexture,
                                      ('outAlpha', 'inputs[%d].alpha' % pos))
                allFiles.append((fInfo,noise))
            else:
                allFiles.append((fInfo,None))
    return allFiles


def create_texture(cliffType, nOfCTex=5, cliffPos=(0.75, 0.5), cRandTexs=False, 
                   snow=True, snowPos=(1,), grass=True, grassPos=(0,), 
                   grassType='lush', nOfGTex=5, gRandTexs=False, uRep=1.25, 
                   vRep=1.25, uNoise=0.01, vNoise=0.01, bDepth=0.3, 
                   rampType=0, rampInterp=4, rampUWave=0, rampVWave=0, 
                   rampNoise=0, rampFreq=0, colSpace=COLOUR_SPACES.srgb,
                   rendSpace=COLOUR_SPACES.srgb):
    '''Creates a lambert material for the terrain with a certain style 
    dependent on the parameters passed to the function.
    
    Parameters:
        cliffType [str]   : The type of cliff texture the terrain will have. 
                            The valid values for this are the names of the 
                            folders in CLIFF_TEX_DIR.
        nOfCTex [int]     : The number of cliff textures that will be used 
                            together to create the cliff texture.
        cliffPos [tuple]  : The positions on the ramp shader used. Ranges from
                            0.0 to 1.0.
        cRandTexs [bool]  : If True, the textures will not be of 'cliffType' 
                            but from all of the files in CLIFF_TEX_DIR.
        snow [bool]       : If True, a snow texture will be used with the 
                            following options:

            snowPos [tuple] : The positions on the ramp shader used. Ranges 
                              from 0.0 to 1.0.
                              
        grass [bool]      : If True, a grass texture will be used with the 
                            following options:
                            
            grassPos [tuple] : The positions on the ramp shader used. Ranges 
                               from 0.0 to 1.0.
            grassType [str]  : The type of grass texture the terrain will have.
                               The value values for this are the names of the 
                               folders in GRASS_TEX_DIR.
            nOfGTex [int]    : The number of grass textures that will be used
                               together to create the grass texture.
            gRandTexs [str]  : If True, the textures will not be of 'grassType'
                               but from all of the files in GRASS_TEX_DIR.
                               
        uRep [float]      : The number of repetitions of each of the file 
                            textures in the U-axis (Y).
        vRep [float]      : The number of repetitions of each of the file 
                            textures in the V-axis (X).
        uNoise [float]    : The amplitude of the noise effect on each of the 
                            file texture in the U-axis (Y).
        vNoise [float]    : The amplitude of the noise effect on each of the 
                            file texture in the V-axis (X).
        bDepth [float]    : The bump depth used on the material.
        rampType [int]    : The type of rendering the ramp will take. This 
                            involves the direction mainly. The value used 
                            relates to the location in the option menu in the 
                           ramp options.
        rampInterp [int]  : The interpolation of the ramp used to organise the 
                            textures on the terrain. The value used relates to
                            the location in the option menu in the ramp 
                            options.
        rampUWave [float] : The ramp textures U wave that will be applied to 
                            the final terrain texture.
        rampVWave [float] : The ramp textures V wave that will be applied to 
                            the final terrain texture.
        rampNoise [float] : The ramp noise that will applied to the 
                            positioning of each of the textures on the terrain.
        rampFreq [float]  : The ramp noise frequency. The higher this value,
                            the larger area effect the noise will have.
        colSpace [float]  : Sets the colour of the texture to be in linear colour
                            if needed
                            
        On Exit:
            Creates all of the texture files and returns a texture dictionary 
            of all the texture files created by this function.
        '''

    texInfo = {'placements': []}
    ramp = mf.create_shader_node('ramp', asTexture=True, uWave=rampUWave,
                                 interpolation=rampInterp, vWave=rampVWave,
                                 type=rampType, noise=rampNoise, 
                                 noiseFreq=rampFreq)
    cmds.removeMultiInstance('%s.colorEntryList[1]' % ramp)
    cmds.removeMultiInstance('%s.colorEntryList[2]' % ramp)
    ramp2d = mf.create_shader_node('place2dTexture', asUtility=True)
    mf.connect_attributes(ramp2d, ramp, ('outUV', 'uv'))
    
    cliffTexImgs = tex_types(('cliff_Textures',cliffType), nOfCTex,
                          cRandTexs)
    cLayeredTex = mf.create_shader_node('layeredTexture', asTexture=True)
    cFileNodes = create_files(cliffTexImgs, cLayeredTex, nOfCTex, 
                           'cliff', uRep, vRep, uNoise, vNoise)

    if snow:
        snowTex = mf.create_shader_node('snow', asTexture=True, threshold=0.25)
        snowTex3d = mf.create_shader_node('place3dTexture', asUtility=True)
        mf.connect_attributes(snowTex3d, snowTex, ('wim[0]', 'pm'))
        mf.connect_attributes(cLayeredTex, snowTex, ('outColor', 'surfaceColor'))
        texInfo['snow'] = [snowTex, snowTex3d]
        texInfo['placements'].append(snowTex3d)
    else:
        texInfo['snow'] = [None, None]
    
    if grass:
        grassTexImgs = tex_types(('grass_Textures',grassType), nOfGTex, 
                                 gRandTexs)
        gLayeredTex = mf.create_shader_node('layeredTexture', asTexture=True)
        gFileNodes = create_files(grassTexImgs, gLayeredTex, nOfGTex, 
                                  'grass', uRep, vRep, uNoise, vNoise)
        texInfo['grass'] = [gLayeredTex, gFileNodes]
    else:
        texInfo['grass'] = [None, None]
        
    projection = mf.create_shader_node('projection', asUtility=True, vAngle=90, 
                                       uAngle=180, projType=1)
    projection3d = mf.create_shader_node('place3dTexture', asUtility=True)
    mf.connect_attributes(projection3d, projection, ('wim[0]', 'pm'))

    multiplyCol = mf.create_shader_node('multiplyDivide', asUtility=True)
    colourMult = COLOUR_SPACE_VALUES[colSpace]/COLOUR_SPACE_VALUES[rendSpace]

    mf.connect_attributes(ramp, multiplyCol, ('outColor', 'input1'))
    cmds.setAttr('%s.input2X' % multiplyCol, colourMult)
    cmds.setAttr('%s.input2Y' % multiplyCol, colourMult)
    cmds.setAttr('%s.input2Z' % multiplyCol, colourMult)

    mf.connect_attributes(multiplyCol, projection, ('output', 'image'))
    
    bump = mf.create_shader_node('bump3d', asUtility=True, bumpDepth=bDepth)
    mf.connect_attributes(projection, bump, ('outAlpha', 'bumpValue'))
    
    lambert = mf.create_shader_node('lambert', asShader=True, 
                                    name='mtg_terrainMaterial')
    lambertSG = mf.create_shading_group(lambert)
    mf.connect_attributes(lambert, lambertSG, ('outColor', 'surfaceShader'))
    mf.connect_attributes(bump, lambert, ('outNormal', 'normalCamera'))
    mf.connect_attributes(projection, lambert, ('outColor', 'color'))
    
    eListNum = 0
    if snow or grass:
        for c in cliffPos:
            mf.connect_attributes(cLayeredTex, ramp, 
                                  ('outColor', 
                                   'colorEntryList[%d].color' % eListNum))
            mf.set_attributes(ramp, 
                              **{'colorEntryList[%d].position' % eListNum: c})
            eListNum += 1
    else:
        mf.connect_attributes(cLayeredTex, ramp, 
                                  ('outColor', 'colorEntryList[0].color'))
        mf.set_attributes(ramp, **{'colorEntryList[0].position': 0})
    
    if snow:
        for s in snowPos:
            mf.connect_attributes(snowTex, ramp, 
                                  ('outColor', 
                                   'colorEntryList[%d].color' % eListNum))
            mf.set_attributes(ramp, 
                              **{'colorEntryList[%d].position' % eListNum: s})
            eListNum += 1
            
    if grass:
        for g in grassPos:
            mf.connect_attributes(gLayeredTex, ramp, 
                          ('outColor', 'colorEntryList[%d].color' % eListNum))
            mf.set_attributes(ramp, 
                              **{'colorEntryList[%d].position' % eListNum: g})
            eListNum += 1
    
    texInfo['ramp'] = [ramp, ramp2d]
    texInfo['cliff'] = [cLayeredTex, cFileNodes]
    texInfo['projection'] = [projection, projection3d]
    texInfo['bump'] = bump
    texInfo['lambert'] = [lambert, lambertSG]
    texInfo['placements'].append(projection3d)
    return texInfo
    

def assign_terrain_shader(sg, object, placements):
    '''Used to assign a material to an object to the shading group, fit and 
    parent any necessary 3d placements to the objects so they resize when the 
    objects are.
    
    Parameters:
        sg [str]           : The name of the materials shading group.
        object [str]       : A name of an object that will be applied the 
                             material linked to the shading group.
        placements [tuple] : The 3d placements that will be parented under the
                             object.
                             
    On Exit:
        Applies the shader to the object and parents the placements under it.
        
    '''
    mf.apply_shader(sg, object)
    if isinstance(placements, (str,unicode)):
        placer=[placements]
    for placer in placements:
        mf.fit_to_group_bbox(placer, sg)
    cmds.parent(placements, object)


def move_vtx_positions(vals, pObject, axis='y', reverse=False, 
                       seprAxisMv=False, refresh=True, queue=None):
    '''Used to move the vertex positions of an object 'pObject' in an axis
    direction.
    
    Parameters:
        vals [list]         : A list of float values for the relative move 
                              positions.
        pObject [str]       : The name of the polygonal object in the scene.
        axis [str]          : The direction for the moved vertex for the value.
                              Valid values are x,y,z,n with 'n' being normals.
        reverse [bool]      : If True, the values in the list 'vals' will be 
                              reversed.
        seprAxisMv [bool]   : If True, each of the move axis values will be
                              moved separately instead of in one move command 
                              apart from 'n' which is always done separately.
                              
    On Exit:
        Moves each of the vertexes of of 'pObject' with relative values from
        'vals' in the direction(s) of 'axis'.
    
    '''
    
    nVtx = cmds.polyEvaluate(pObject, vertex=True)
    
    nAxis = axis.lower()

    if not(isinstance(vals, (list,tuple))):
        raise ValueError('vals is not a list or tuple. Got %s' % vals)
    if not(cmds.objExists(pObject)):
        raise ValueError('%s is not an object that exists in the scene' 
                         % pObject)
    if not(mf.poly_check(pObject)):
        raise ValueError('MTG only works with poly objects. %s is not' 
                         % pObject)
    if not(all([True if l in ('x','y','z','n') and \
            nAxis.count(l) == 1 else False for l in axis])):
        raise ValueError('%s is an invalid axis. Must contain (x,y,z,n)' 
                         ' and only one of each' % axis)
        
    if isinstance(vals, tuple):
        vals = list(vals)
    if reverse:
        vals.reverse()
    
    if 'n' in nAxis:
        if queue:
            queue.put(('Moving Terrain in Normal direction', nVtx))
        normalDirs = mf.get_vertex_normals(pObject)
         
        for i,val in enumerate(vals[:nVtx]):
            if queue:
                queue.put(i)
            cmds.select('%s.vtx[%d]' % (pObject, i), replace=True)
            dir_ = normalDirs[i]
            nOfVerts = len(mf.soft_selection())
            cmds.moveVertexAlongDirection(direction=[dir_]*nOfVerts,
                                          magnitude=[val]*nOfVerts)
            if refresh:
                cmds.refresh(cv=True)

    if any([True if l in ('x','y','z') else False for l in nAxis]):
        tmpAxis = nAxis.replace('n', '')
        if seprAxisMv:
            for a in tmpAxis:
                if queue:
                    queue.put(('Moving Terrain in %s axis' % a, nVtx))
                move = {'move'+a.upper(): True}
                for i,val in enumerate(vals[:nVtx]):
                    queue.put(i)
                    cmds.select('%s.vtx[%d]' % (pObject, i), replace=True)
                    cmds.move(val, relative=True, **move)
                    if refresh:
                        cmds.refresh(cv=True)
        else:
            if queue:
                queue.put(('Moving Terrain in %s axis' % tmpAxis.upper(), nVtx))
            move = {'move'+tmpAxis.upper(): True}
            for i,val in enumerate(vals[:nVtx]):
                if queue:
                    queue.put(i)
                val = (val,)*len(tmpAxis)
                cmds.select('%s.vtx[%d]' % (pObject, i), replace=True)
                cmds.move(*val, relative=True, **move)
                if refresh:
                    cmds.refresh(cv=True)


def music_displace(songInfo, terrainHeight, pObject, vtxDire='n', 
                   sSelect=False, sSelectCurve=None, sSelectMode=0,
                   sSelectRadius=5, dips=False, seprAxisMv=False, 
                   reverse=False, refresh=True, queue=None):
    '''Used to gather the song values from the songInfo 'TerrainWaveFile' 
    class file and then use the values to move the 'pObjects' vertices.
    
    Parameters:
        songInfo [object]      : 'TerrainWaveFile' class object from the 
                                 'terrainWave' file.
        terrainHeight [float]  : The maximum height of the vertex movement and 
                                 the value to which all other values will 
                                 range from.
        pObject [str]          : The name of the poly object in the scene.
        vtxDire [str]          : The vertex direction to which each point will 
                                 be moved in. This can be a single or 
                                 combination of x,y,z,and n with n being 
                                 normal.
        sSelect [bool]         : If True, soft select is enabled with the 
                                 following options:
            
            sSelectCurve [str]    : The soft select falloff curve used for the 
                                    soft select.
            sSelectMode [int]     : The type of falloff mode will have. The 
                                    value used relates to the location in the 
                                    option menu in the soft select options.
            sSelectRadius [float] : The radius of the soft select area from 
                                    which points it will select from the 
                                    centre of the selection.
        
        dips [bool]            : If True, negative values from the 'songInfo' 
                                 will be used. Else, all the values created 
                                 will be positive.
        seprAxisMv [bool]      : If True, each of the axis moves ill be 
                                 seperated and not merged into one move 
                                 command. This doesn't effect the 'n' option 
                                 since this uses a different move command to 
                                 the options x, y, and z.
        reverse [bool]         : If True, the song will be reverse, starting 
                                 from the end rather than the beginning.
        
    On Exit:
        The 'pObject's vertices will be moved in relation to the song's 
        amplitude, in relation to the 'terrainHeight'.
    '''
    nVtx = cmds.polyEvaluate(pObject, v=True)
    if sSelect:
        if sSelectCurve == None:
            cmds.softSelect(sse=1,ssc=mf.SSELECT_CURVES[0], ssf=sSelectMode, 
                            ssd=sSelectRadius)
        else:
            cmds.softSelect(sse=1,ssc=sSelectCurve, ssf=sSelectMode, 
                            ssd=sSelectRadius)
    else:
        cmds.softSelect(sse=0)
    move_vtx_positions(songInfo.createheightvals(nVtx, terrainHeight, dips),
                        pObject, vtxDire, reverse, seprAxisMv, refresh, queue)
    if queue:
        queue.put('Complete')
    
if __name__=='__main__': 
    obj = cmds.polyPlane(name='terrain', width=24, height=24, sx=30, sy=70)
    # change musicLocation to a song in your directory to test the functions
    musicLocation = 'D:\\Users\\Jon\\workspace\\Terraign Generator\\01 Window.wav'
    songInfo = tw.TerrainWaveFile(musicLocation)
    
    music_displace(songInfo, terrainHeight=4, pObject=obj[0], vtxDire='y', 
                   sSelect=True, sSelectCurve=mf.SSELECT_CURVES[2], 
                   sSelectMode=0, sSelectRadius=2, dips=True, seprAxisMv=False, 
                   reverse=False)
    
    texInfo = create_texture('arid', nOfCTex=5, cRandTexs=False, 
                             cliffPos=(0.75,0.5), snow=True, snowPos=(1,), 
                             grass=True, grassPos=(0,), grassType='lush', 
                             nOfGTex=5, gRandTexs=False, uRep=1.25, vRep=1.25, 
                             uNoise=0.01, vNoise=0.01, bDepth=0.03, rampType=0, 
                             rampInterp=0, rampUWave=0, rampVWave=0, 
                             rampNoise=0, rampFreq=0)
    
    assign_terrain_shader(texInfo['lambert'][1], obj[0], texInfo['placements'])
