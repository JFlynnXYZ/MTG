import os
import sys
import time
import subprocess
from functools import partial as par
import threading
import Queue

try:
    import maya.cmds as cmds
    import maya.OpenMaya as Om
    import maya.mel as mel
    import maya.utils as mu
except:
    pass

import mayaSnippet.mayaFuncs as Mf
import mtg.terrainWave as Tw
import mtg.mtgMain as Main

CLIFF_COLOUR = (0.41, 0.311468, 0.26937)
GRASS_COLOUR = (0.15478, 0.494, 0.138814)
SNOW_COLOUR = (1, 1, 1)


if sys.platform == 'win32':
    def open_file(fileDir):
        """Used to open a file with the default program on Windows32 OS system

        Parameter:
            fileDir [str] : The directory of the file to be opened.

        On Exit:
            Opens the file with the default program on the system."""
        try:
            os.startfile(fileDir)
            return True, None, None
        except WindowsError:
            return False, 0, fileDir
        except Exception as e:
            return False, None, e.args
elif sys.platform == "darwin":
    def open_file(file_directory):
        """Used to open a file with the default program on a Darwin OS system

        Parameter:
            file_directory [str] : The directory of the file to be opened.

        On Exit:
            Opens the file with the default program on the system."""
        try:
            subprocess.call(["open", file_directory])
        except Exception as e:
            return False, None, e.args
else:
    def open_file(file_directory):
        """Used to open a file with the default program on a Linux OS system

        Parameter:
            file_directory [str] : The directory of the file to be opened.

        On Exit:
            Opens the file with the default program on the system."""
        try:
            subprocess.call(["xdg-open", file_directory])
        except Exception as e:
            return False, None, e.args


class GenerateTerrainThread(threading.Thread):
    def __init__(self, queue, songInfo, deformMag, pObjectNam, axis, sSelect, falloffCurve, falloffMode, falloffRadius,
                 negativeValues, separateDeformDirection, reverseSong, refresh):
        threading.Thread.__init__(self)
        self.daemon = False
        self.q = queue
        self.signal = False
        self.songInfo = songInfo
        self.deformMag = deformMag
        self.pObjectNam = pObjectNam
        self.axis = axis
        self.sSelect = sSelect
        self.falloffCurve = falloffCurve
        self.falloffMode = falloffMode
        self.falloffRadius = falloffRadius
        self.negativeValues = negativeValues
        self.separateDeformDir = separateDeformDirection
        self.reverse = reverseSong
        self.refresh = refresh


    def run(self):
        mu.executeInMainThreadWithResult(Main.music_displace, self.songInfo, self.deformMag, self.pObjectNam, self.axis, self.sSelect, self.falloffCurve,
                            self.falloffMode, self.falloffRadius, self.negativeValues, self.separateDeformDir,
                            self.reverse, self.refresh, self.q)

class MTGGui:
    """Creates the Music Terrain Generator

    Parameters:
        winID [str] : The window name. This is to ensure that no two of the
                      same window exist at the same time.

    Attributes:
        win [str]                  : The actual name of the newly created
                                     window.
        wavFilter [str]            : The string used to filter files in the
                                     open file dialog.
        currentSong [str]          : The name of the current song loaded into
                                     the program.
        currentSongDir [None][str] : The current song's directory on the disc
                                     drive.
        songInfo [None][object]    : The song info class object from
                                     terrainWave.TerrainWaveFile.
        fileTextures [dict]        : Stores all the files from the file
                                     directories. The string name
                                     'cliffTextures' and 'grassTextures'
                                     are the only values currently used.
        cliffTypeFolders [list]    : The list of all the folders in the
                                     main.CLIFF_TEX folder
        self.newFileJob [str]      : The name of the script job so to close the
                                     script when a new file is created to
                                     remove the chance of errors


        polygonObjTFGrp [str]    : The name of the polygon object text field
                                   group
        songText [str]           : The name of the currently loaded song text
                                   label
        musicLoadGrp [str]       : The name of the Music Location text field
                                   button group
        loadMusicB [str]         : The name of the load music button
        playMusicB [str]         : The name of the play music button
        reloadMusicB [str]       : The name of the reload music button
        clearMusicB [str]        : The name of the clear music button
        soundScrb [str]          : The name of the Sound Scrubber preview
                                   control
        soundCtrl [str]          : Then name of the sound control to change the
                                   Sound Scrubber
        deformMagFSLGrp [str]    : The name of the Deform Magnitude Float
                                   slider group
        deformDirCBGrp [str]     : The name of the Deform Direction Check Box
                                   group
        otherOptCBGrp [str]      : The name of the Other Options Check Box
                                   group
        sSelectCB [str]          : The name of the Soft Select check box
        sSelectReset [str]       : The name of the Soft Select reset button
        falloffModeOMGrp [str]   : The name of the soft select Falloff mode
                                   Option Menu group
        falloffRadFSlGrp [str]   : The name of the soft select Falloff radius
                                   float slider group
        falloffCurveRow [str]    : The name of the soft select falloff curve
                                   row
        falloffCurveCtrl [str]   : The name of the soft select falloff curve
                                   graph control
        interpolationOMGrp [str] : The name of the curve interpolation option
                                   menu group
        curvePresetsRow [str]    : The name of the row containing all the curve
                                   preset curves
        generateTerrainB [str]   : The name of the Generate Terrain  Button
        randomCTexRow [str]      : The name of the random cliff texture row
        randomCTexCB [str]       : The name of the random cliff texture check
                                   button
        cliffTypesOMGrp [str]    : The name of the cliff types option menu
                                   group
        nOfCliffTexIF [str]      : The name of the cliff texture integer field
        texRepeatU [str]         : The name of the texture repeat U float
                                   slider
        texRepeatV  [str]        : The name of the texture repeat V float
                                   slider
        texNoiseU [str]          : The name of the texture noise U float
                                   slider
        texNoiseV [str]          : The name of the texture noise V float
                                   slider
        bDepth [str]             : The name of the bump depth float slider
        texPosFrame [str]        : The name of the texture positioning frame
        ramp [str]               : The name of the current ramp preview name in
                                   the interface
        rampPreviewImg [str]     : The name of the ramp preview swatch display
        rampType [str]           : The name of the ramp type option menu group
        rampInterpol [str]       : The name of the ramp interpolation option
                                   menu group
        rampCliffTex [str]       : The name of the ramp cliff texture colour
                                   port
        resetButton [str]        : The name of the ramp reset button
        entryTypeOMGrp [str]     : The name of the ramp entry type option menu
        cliffEntry [str]         : The name of the cliff entry menu item of
                                   entryTypeOMGrp
        snowEntry [str]          : The name of the snow entry menu item of
                                   entryTypeOMGrp
        grassEntry [str]         : The name of the grass entry menu item of
                                   entryTypeOMGrp
        createEntryButton [str]  : The name of the create entry button for the
                                   ramp preview
        uWaveSl [str]            : The name of the ramp U Wave float slider
        vWaveSl [str]            : The name of the ramp V Wave float slider
        noiseSl [str]            : The name of the ramp noise float slider
        freqSl [str]             : The name of the ramp noise frequency slider
        generateTerrainB [str]   : The name of the generate terrain button

    """
    def __init__(self, winID='mtgScriptWindow'):
        if cmds.window(winID, exists=True):
            cmds.deleteUI(winID)
        self.win = cmds.window(winID, title='MTG :: Music Terrain Generator', 
                               iconName='MTG', widthHeight=(570,770))
        
        self.wavFilter = "WAV Files (*.wav);;All Files (*.*)"
        self.currentSong = '...'
        self.currentSongDir = None
        self.songInfo = None
        self.fileTextures = {}
        self.create_interface()
        self.newFileJob = cmds.scriptJob(event=['deleteAll', self.end], 
                                         protected=True)
        self.queue = Queue.Queue()
        self.complete = False
        cmds.showWindow(self.win)
        
    def end(self):
        """Used to, when a new file is created, to close the window and end
        the scriptJob which causes it to do this.

        On Exit:
            Closes the window on a new file creation and kills the script job
            that allows it.

        """
            
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)
        cmds.scriptJob(kill=self.newFileJob, force=True)
        
    def error_message(self, errNo=None, value=''):
        """Used to create error messages or notifications to the user about a
        specific error.

        Parameters:
            errNo [None][int] : The number pertaining to the error message.
            value [str]       : The value pertaining to the error message.
                                Usually the cause of the error.
        On Exit:
            Creates a error message dialog for the user to be notified of the
            problem with the program.

        """
        if errNo == 0:
            cmds.confirmDialog(title='Error', 
                               message='The system cannot fine the file "%s".'\
                               ' The song will not be played.' % value, 
                               icon="warning")
        elif errNo == 1:
            cmds.confirmDialog(title='Error', 
                               message='No value has been entered into the '\
                               '"Music Location" field.\nPlease enter a WAV '\
                               'file directory to load.', icon="warning")
        elif errNo == 2:
            cmds.confirmDialog(title='Error', 
                               message='The file location you have entered '\
                               'into the "Music Location" field is incorrect.'\
                               '\nPlease enter a valid WAV file directory to '\
                               'load.', icon="warning")
        elif errNo == 3:
            cmds.confirmDialog(title='Error', 
                               message='The file location for the song "%s" '\
                               'has been moved or deleted.\nThe song will now'\
                               ' be unloaded from the program.' % value, 
                               icon="warning") 
        elif errNo == 4:
            cmds.confirmDialog(title='Error', 
                               message='No object has the name "%s" in the '\
                               'scene.\nPlease select another object.' % value, 
                               icon="warning") 
        elif errNo == 5:
            cmds.confirmDialog(title='Error', 
                               message='You have not selected a direction for'\
                               ' the terrain to be deformed in.\nPlease '\
                               'select one to continue.', icon="warning")
        elif errNo == 6:
            cmds.confirmDialog(title='Error', 
                               message='The current song you have loaded has'\
                               ' been moved or removed from the hard drive. '\
                               '\n Please try loading a new song. This file'\
                               ' will be unloaded', icon="warning")
        elif errNo == 7:
            cmds.confirmDialog(title='Error', 
                               message='You have not loaded a song into the'\
                               ' program.\nPlease do this before continuing.', 
                               icon="warning")
        else:
            if 'RIFF' in value[0]:
                cmds.confirmDialog(title='Error', 
                                   message='This is not a WAV file.\nPlease '\
                                   'select a valid WAV file.', icon="warning") 
            else:
                cmds.confirmDialog(title='Unknown Error', 
                                   message='This is an unknown error. Here is'\
                                   ' the message:\n%s' % value, icon="warning")
    
    def music_browse(self, *args):
        """Creates a open file dialog window to find the location of the song
        file on the disc drive.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            Finds a wave file on the disc drive and sets the text field to the
            found files location.

        """
        filename = cmds.fileDialog2(fileMode=1, caption="Import Music", 
                                    fileFilter=self.wavFilter)
        if filename != None:
            cmds.textFieldButtonGrp(self.musicLoadGrp, e=True, 
                                    fileName=filename[0])
        
    def load_song(self, *args):
        """Loads the song in the musicLoadGrp field and loads it into maya and
        creates a TerrainWaveFile with it.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            Loads the song into the program and stores the information into
            the self.songInfo variable. It also activates the buttons related
            to the newly loaded song.

        """
        filename = cmds.textFieldButtonGrp(self.musicLoadGrp, q=True,
                                           fileName=True)
        if filename == '':
            self.error_message(1, filename)
        else:
            self.clear_song()
            try:
                self.songInfo = Tw.TerrainWaveFile(os.path.abspath(filename), self.queue)
            except IOError:
                self.error_message(2, filename)
            except Exception as e:
                self.error_message(value=str(e.args))
            else:
                self.currentSong = mel.eval('doSoundImportArgList ("1", {"%s","0"})' 
                                            % filename)
                self.currentSongDir = filename
                endFrame = cmds.getAttr('%s.endFrame' % self.currentSong)
                cmds.soundControl(self.soundScrb, e=True, 
                                  sound=self.currentSong, maxTime=endFrame)
                cmds.text(self.songText, e=True, label=self.currentSong)
                self.enable_disable_widgets((self.reloadMusicB, 
                                             self.playMusicB, 
                                             self.clearMusicB), enable=True)
            
    def reload_song(self, *args):
        """Reloads the currently loaded song.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            Reloads the song into the program and stores the information into
            the self.songInfo variable.

        """
        try:
            self.songInfo = Tw.TerrainWaveFile(self.currentSongDir, self.queue)
        except IOError:
            self.error_message(3, self.currentSong)
            self.clear_song()
        except:
            self.error_message(6)
            self.clear_song()
        self.currentSong = mel.eval('doSoundImportArgList ("1", {"%s","0"})' 
                                    % self.currentSongDir)
        
    def play_song(self, *args):
        """Attempts to open the chosen song file using the systems default
        music player.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            On success, will open the file and play the song in the default
            music player.

        """
        filename = cmds.textFieldButtonGrp(self.musicLoadGrp, q=True, 
                                           fileName=True)
        check, errNo, msg = open_file(filename)
        if not(check):
            self.error_message(errNo, msg)
        
    def clear_song(self, *args):
        """Clears the currently loaded song in the program.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            Clears the song from the program aswell as the songInfo stored in
            the program. It also disables the related widgets with a loaded
            song.

        """
        if self.currentSong != '...':
            cmds.delete(self.currentSong)
            self.currentSong = '...'
            self.currentSongDir = None
            cmds.text(self.songText, e=True, label=self.currentSong)
            self.songInfo.close()
            self.songInfo = None
            self.enable_disable_widgets((self.reloadMusicB, self.playMusicB, 
                                         self.clearMusicB), enable=False)
        
    def enable_disable_widgets(self, widgets, enable=True):
        """This command is used to disable the widgets/controls passed to the
        function.

        Parameters:
            widgets [str][list] : The widget(s) that will be either enabled or
                                  disabled dependent on the 'enable' parameter.
            enable [bool]       : If True, the widgets will be enabled, else
                                  disabled

        On Exit:
            The listed widgets/controls will be disabled or enabled.

        """
        if isinstance(widgets, (str,unicode)):
            cmds.control(widgets, e=True, enable=enable)
        else:
            for widg in widgets:
                cmds.control(widg, e=True, enable=enable)
                
    def visbile_invisible_widgets(self, widgets, visible=True):
        """This command is used to change the visibility of the
        widgets/controls passed to the function.

        Parameters:
            widgets [str][list] : The widget(s) that will be either enabled or
                                  disabled dependent on the 'enable' parameter.
            visible [bool]      : If True, the widgets will be visible, else
                                  invisible
        On Exit:
            The listed widgets/controls will be visible or invisible.

        """
        if isinstance(widgets, (str,unicode)):
            cmds.control(widgets, e=True, visible=visible)
        else:
            for widg in widgets:
                cmds.control(widg, e=True, visible=visible)
            
    def toggle_sselect_widgets(self, state, *args):
        """Used to change the enable state of the soft select widgets/controls.

        Parameters:
            state [bool] : The state for which the widgets will be turned to.
            args [tuple] : Ignore value. The value is returned by the button
                           and is unused.

        On Exit:
            The soft select widgets/controls will be enabled or disabled.

        """
            
        widgets = (self.falloffModeOMGrp, self.falloffRadFSlGrp, 
                   self.falloffCurveRow, self.interpolationOMGrp, 
                   self.curvePresetsRow)
        self.enable_disable_widgets(widgets, state)
        
    def select_obj(self):
        """Used for the polygonObjTFGrp. Stores the first currently selected
        object in the Maya scene if it is a polygon object.

        Parameters:
            An object selection in Maya.

        On Exit:
            Either, changes the field to be the name of a selected poly object
            or clears the field.

        """
        obj = cmds.ls(selection=True)
        if len(obj) != 0:
            obj = obj[0]
            if Mf.poly_check(obj):
                cmds.textFieldButtonGrp(self.polygonObjTFGrp, e=True, text=obj)
        else:
            cmds.textFieldButtonGrp(self.polygonObjTFGrp, e=True, text='')
        
    def default_falloff_curve(self):
        """Sets up the option variable in Maya for the interfaces soft select
        curve graph.

        On Exit:
            Either stores the current graph values of the default falloff curve
            for soft select or re-uses the values already stored in the option
            variable.

        """
        if cmds.optionVar(q="softSelectCurve") == 0:
            graphValues = Mf.setup_graph_values(cmds.softSelect(q=True,
                                                                softSelectCurve=True))
            self.setup_falloff_curve(values=graphValues)
        else:
            pass
        
    def reset_falloff_curve(self):
        """Used to reset the soft select falloff curve curve to the default
        variable in the option variable.

        On Exit:
            Sets the current falloff curve to the graph values in the soft
            select option variable.

        """
        graphValues = cmds.optionVar(q='softSelectCurveOptionVar')
        self.change_falloff_curve_prest(values=graphValues)
    
    def setup_falloff_curve(self, values, stringValues=('softSelectCurve',
                                                        'softSelectCurveOptionVar')):
        """Sets up the falloff curve option variables with values.

        Parameters:
            values [list] : Values used to set the option variables
                                 storing the soft select falloff curves
            stringValues [str][tuple] : The name of the option variables to
                                        which the values will change for.

        On Exit:
            Stores the values in the option variables passed in 'stringValues'

        """
        if isinstance(stringValues, (str, unicode)):
            stringValues = (stringValues,)
        for optVal in stringValues:
            cmds.optionVar(stringValue=[optVal, values[0]])
        for optVal in stringValues:
            for val in values[1:]:
                cmds.optionVar(stringValueAppend=[optVal, val])
            
    def falloff_curve_change_key(self, *args):
        """Updates the interpolation of the selected soft select curve graph in
        the interpolation option menu to match the graph curve..

        Parameters:
            args [tuple] : Ignore value. The value is returned by the control
                           and is unused.
        On Exit:
            Changes the interpolation option menu to the one set on the curve

        """
        curKeyInterpVal = cmds.gradientControlNoAttr(self.falloffCurveCtrl, 
                                                     q=True, civ=True)
        cmds.optionMenuGrp(self.interpolationOMGrp, e=True, 
                           select=curKeyInterpVal+1)
        
    def change_falloff_key_interp(self, *args):
        """Changes the currently selected key of the soft select curve graph to
        the value in the interpolationOMGrp.

        Parameters:
            args [tuple] : Ignore value. The value is returned by the control
                           and is unused.

        On Exit:
            Sets the currently selected point on the soft select curve to the
            interpolation value in the interpolationOMGrp.
        """
        curKey = cmds.gradientControlNoAttr(self.falloffCurveCtrl, q=True, 
                                            ck=True)
        newInterpVal = cmds.optionMenuGrp(self.interpolationOMGrp, q=True, 
                                          select=True)
        cmds.gradientControlNoAttr(self.falloffCurveCtrl, e=True, ck=curKey, 
                                   civ=newInterpVal-1)
        self.falloff_curve_change_key()
        
    def change_falloff_curve_prest(self, preset=None, values=None):
        """Changes the falloff graph curve to one of the selected presets or
        to the values passed to the function.

        Parameters:
            preset [str][int][None] : Can either be the name of a preset or the
                                      number of the preset as the key for the
                                      mf.SSELECT_CURVES.
            values [str][None]      : Can be used instead of preset to set the
                                      value of the curve.

        On Exit:
            Sets the value of the falloff curve graph by setting the value
            of the option variable 'softSelectCurve'.

        """
        pare = cmds.gradientControlNoAttr(self.falloffCurveCtrl, q=True, 
                                          parent=True)
        cmds.deleteUI(self.falloffCurveCtrl)
        if preset != None:
            self.setup_falloff_curve(Mf.setup_graph_values(Mf.SSELECT_CURVES[preset]),
                                     'softSelectCurve')
        elif values != None:
            self.setup_falloff_curve(values, 'softSelectCurve')
        else:
            raise ValueError('No Value has been specified. Either "preset" or'\
                             ' "values" should be a non None value.')
        self.falloffCurveCtrl = cmds.gradientControlNoAttr('falloffCurveGradient', 
                                                           h=90, 
                                                           optionVar='softSelectCurve', 
                                                           width=200, 
                                                           ckc=self.falloff_curve_change_key, 
                                                           parent=pare)
        
    def reset_soft_select_options(self, *args):
        cmds.optionMenuGrp(self.falloffModeOMGrp, e=True, select=1)
        cmds.floatSliderGrp(self.falloffRadFSlGrp, e=True, value=5)
        self.reset_falloff_curve()
        
    def cycle_preview_img(self, texVar, fNode, *args):
        curImgPath = cmds.getAttr('%s.fileTextureName' % fNode)
        curImgNo = self.fileTextures[texVar].index(curImgPath)
        if curImgNo >= len(self.fileTextures[texVar])-1:
            newImgNo = 0
        else:
            newImgNo = curImgNo+1
        self.set_preview(newImgNo, texVar, fNode)
        
    def set_preview(self, num, texVar, fNode):
        imgPath = self.fileTextures[texVar][num]
        cmds.setAttr('%s.fileTextureName' % fNode,imgPath, type='string')
    
    def update_file_node_swatch(self, fNode):
        mel.eval('updateFileNodeSwatch("%s")' % fNode)
        
    def update_preview(self, texVar, imgDir, fNode, all=False, *args):
        if all:
            self.fileTextures[texVar] = []
            for root, _, filenames in os.walk(imgDir):
                if os.path.split(root)[1] == '.mayaSwatches':
                    continue
                self.fileTextures[texVar].extend([os.path.join(root,f).replace('\\','/') \
                                                  for f in filenames])
        else:
            value = cmds.optionMenuGrp(args[0], q=True, value=True)
            texPath = os.path.join(imgDir,value)
            self.fileTextures[texVar] = [os.path.join(texPath,f).replace('\\','/') \
                                         for f in os.listdir(texPath) \
                                         if os.path.isfile(os.path.join(texPath,f))]
        self.set_preview(0, texVar, fNode)
    
    def toggle_randomtex(self, texVar, imgDir, field, fNode, *args):
        state=cmds.checkBox(args[0], q=True, value=True)
        self.update_preview(texVar, imgDir, fNode, all=True)
        self.enable_disable_widgets(field, not(state))
        
    def toggle_visble_grasstex(self, state, *args):
        self.visbile_invisible_widgets(self.grassTexturesFrame, state)
        self.check_other_tex_states()
        
    def check_other_tex_states(self, *args):
        snow = cmds.checkBox(self.snowTexCB, q=True, value=1)
        grass = cmds.checkBox(self.grassTexCB, q=True, value=1)
        if snow or grass:
            self.visbile_invisible_widgets(self.texPosFrame, True)
        else:
            self.visbile_invisible_widgets(self.texPosFrame, False)
            
        if not(snow):
            self.replace_ramp_entry_type(self.ramp, SNOW_COLOUR)
        if not(grass):
            self.replace_ramp_entry_type(self.ramp, GRASS_COLOUR)
        if not(grass) and not(snow):
            self.clear_ramp(self.ramp)
            
        cmds.menuItem(self.snowEntry, e=True, enable=snow)
        cmds.menuItem(self.grassEntry, e=True, enable=grass)
        cmds.optionMenuGrp(self.entryTypeOMGrp, e=True, select=1)   
        
    def setup_preview_file(self, name):
        if cmds.optionVar(exists='mtg_%s' % name) and cmds.objExists(cmds.optionVar(q='mtg_%s' % name)):
            fileNode = cmds.optionVar(q='mtg_%s' % name)
        else:
            fileNode = cmds.createNode('file', name='mtg_%s' % name, skipSelect=True)
            cmds.lockNode(fileNode)
            cmds.optionVar(stringValue=('mtg_%s' % name, fileNode))
        return fileNode
        
    def setup_texture_pos_ramp(self):
        if cmds.optionVar(exists='mtg_texPositionRamp') and cmds.objExists(cmds.optionVar(q='mtg_texPositionRamp')):
            self.ramp = cmds.optionVar(q='mtg_texPositionRamp')
        else:
            self.ramp = cmds.createNode('ramp', name='mtg_texPositionRamp', skipSelect=True)
            cmds.lockNode(self.ramp)
            cmds.optionVar(stringValue=('mtg_texPositionRamp', self.ramp))
        self.reset_ramp(self.ramp, self.snowTexCB, self.grassTexCB)
        
    def get_tex_ramp_info(self, ramp):
        rampColPos = {'ramp': ramp}
        for index in cmds.getAttr('%s.colorEntryList' % ramp, mi=True):
            rampColPos[index] = (cmds.getAttr('%s.colorEntryList[%d].position' 
                                              % (rampColPos['ramp'], index)), 
                                 cmds.getAttr('%s.colorEntryList[%d].color' 
                                              % (rampColPos['ramp'], index))[0])
        return rampColPos
    
    def reset_ramp_colours(self, ramp):
        graphInfo = self.get_tex_ramp_info(ramp)
        for key, value in graphInfo.items():
            if key == 'ramp':
                continue
            closestColour = Mf.closest_colour(value[1], (GRASS_COLOUR,CLIFF_COLOUR,SNOW_COLOUR))
            if closestColour == GRASS_COLOUR:
                cmds.setAttr(*('%s.colorEntryList[%d].color' % (self.ramp, key),) 
                             + GRASS_COLOUR, type='double3')
            elif closestColour == CLIFF_COLOUR:
                cmds.setAttr(*('%s.colorEntryList[%d].color' % (self.ramp, key),) 
                             + CLIFF_COLOUR, type='double3')
            elif closestColour == SNOW_COLOUR:
                cmds.setAttr(*('%s.colorEntryList[%d].color' % (self.ramp, key),) 
                             + SNOW_COLOUR, type='double3')
    
    def replace_ramp_entry_type(self, ramp, remove):
        graphInfo = self.get_tex_ramp_info(ramp)
        for key, value in graphInfo.items():
            if key == 'ramp':
                continue
            closestColour = Mf.closest_colour(value[1],
                                              (GRASS_COLOUR,CLIFF_COLOUR,SNOW_COLOUR))
            if closestColour == remove:
                cmds.removeMultiInstance('%s.colorEntryList[%d]' % (ramp,key))
        self.reset_ramp_colours(ramp)
        
    def clear_ramp(self,ramp):
        entriesLs = cmds.getAttr('%s.colorEntryList' % ramp, mi=True)
        for eNum in entriesLs:
            cmds.removeMultiInstance('%s.colorEntryList[%d]' % (ramp,eNum))
        cmds.setAttr(*('%s.colorEntryList[0].color' % ramp,) + CLIFF_COLOUR, 
                     type='double3')
        
    def reset_ramp(self, ramp, snowCtrl, grassCtrl, *args):
        cmds.setAttr(*('%s.colorEntryList[0].color' % ramp,) + CLIFF_COLOUR, 
                     type='double3')
        cmds.setAttr('%s.colorEntryList[0].position' % ramp, 0.5)
        
        snow = cmds.checkBox(snowCtrl, q=True, value=True)
        grass = cmds.checkBox(grassCtrl, q=True, value=True)
        entriesLs = cmds.getAttr('%s.colorEntryList' % ramp, mi=True)
        for eNum in entriesLs:
            if eNum == 0:
                continue
            cmds.removeMultiInstance('%s.colorEntryList[%d]' % (ramp,eNum))
        
        if snow:
            cmds.setAttr(*('%s.colorEntryList[1].color' % ramp,) + SNOW_COLOUR, 
                         type='double3')
            cmds.setAttr('%s.colorEntryList[1].position' % ramp, 1)
        if grass:
            cmds.setAttr(*('%s.colorEntryList[2].color' % ramp,) + GRASS_COLOUR, 
                         type='double3')
            cmds.setAttr('%s.colorEntryList[2].position' % ramp, 0)
            
    def create_entry(self, entryType, ramp, *args):
        eType = cmds.optionMenuGrp(entryType, q=True, value=True)
        entriesLs = cmds.getAttr('%s.colorEntryList' % ramp, mi=True)
        newEntryNum = Mf.find_empty_entry_value(entriesLs)
        if eType == 'Cliff':
            color = CLIFF_COLOUR
        elif eType == 'Snow':
            color = SNOW_COLOUR
        elif eType == 'Grass':
            color = GRASS_COLOUR
        else:
            color = (0,0,0)
        cmds.setAttr(*('%s.colorEntryList[%d].color' % (ramp,newEntryNum),)+color, 
                     type='double3')
        cmds.setAttr('%s.colorEntryList[%d].position' % (ramp,newEntryNum), 0.5)
        
    def generate_terrain(self, *args):
        checkBoxOpt = {'axis': ''}
        check = True
        
        pObjectNam = cmds.textFieldButtonGrp(self.polygonObjTFGrp, q=True, 
                                             tx=True)
        deformMag = cmds.floatSliderGrp(self.deformMagFSlGrp, q=True, 
                                        v=True)
        
        for val, axis in enumerate(('x', 'y', 'z', 'n'), 1):
            if cmds.checkBoxGrp(self.deformDirCBGrp, 
                                **{"q": True, "v%d" % val: True}):
                checkBoxOpt['axis'] += axis
        for val, option in enumerate(('negativeValues', 
                                      'separateDeformDirection',
                                      'reverseSong', 'refresh'), 1):
            checkBoxOpt[option] = cmds.checkBoxGrp(self.otherOptCBGrp,
                                                   **{"q": True, "v%d" % val: True})
        
        sSelect = cmds.checkBox(self.sSelectCB, q=True, v=True)
        falloffMode = cmds.optionMenuGrp(self.falloffModeOMGrp, q=True, 
                                         sl=True)-1
        falloffRadius = cmds.floatSliderGrp(self.falloffRadFSlGrp, q=True, 
                                            v=True)
        falloffCurve = ",".join(cmds.optionVar(q='softSelectCurve'))
        
        if self.currentSongDir is not None and not(os.path.exists(self.currentSongDir)):
            self.error_message(6)
            check = False
        if self.currentSongDir is None:
            self.error_message(7)
            check = False
        if not(cmds.objExists(pObjectNam)):
            self.error_message(4, pObjectNam)
            check = False
        if checkBoxOpt['axis'] == '':
            self.error_message(5)
            check = False

        if check:
            msg = "Starting"
            ratio = 1
            currentProgress = 0
            completeMessage = "{}: {}%".format(msg, currentProgress)
            cmds.progressWindow(title='Generating Terrain', progress=currentProgress,
                                status=completeMessage, isInterruptable=False)

            thread = GenerateTerrainThread(self.queue, self.songInfo, deformMag, pObjectNam,
                                           checkBoxOpt['axis'], sSelect, falloffCurve, falloffMode, falloffRadius,
                                           checkBoxOpt['negativeValues'], checkBoxOpt['separateDeformDirection'],
                                           checkBoxOpt['reverseSong'], checkBoxOpt['refresh'])
            mu.processIdleEvents()
            thread.start()
            self.complete = False
            while not self.complete:
                while not self.queue.empty():
                    getM = self.queue.get(block=False)

                    if type(getM) == tuple:
                        ratio = 100.0/getM[1]
                        msg = getM[0]
                        currentProgress = 0
                        completeMessage = "{}: {}%".format(msg, currentProgress)
                    elif type(getM) == str and getM.lower() == "complete":
                        self.complete=True
                    elif getM == None:
                        pass
                    else:
                        currentProgress = int(getM * ratio)
                        completeMessage = "{}: {}%".format(msg, currentProgress)

                    cmds.progressWindow(edit=True, progress=currentProgress, status=completeMessage)
                cmds.pause(seconds=0.001)
                mu.processIdleEvents()
            cmds.progressWindow(endProgress=1)
            
    def generate_texture(self, *args):
        check=True
        
        pObjectNam = cmds.textFieldButtonGrp(self.polygonObjTFGrp, q=True, tx=True)
        cRandomTex = cmds.checkBox(self.randomCTexCB, q=True, value=True)
        cTexType = cmds.optionMenuGrp(self.cliffTypesOMGrp, q=True, value=True)
        cNumOfTex = cmds.intField(self.nOfCliffTexIF, q=True, value=True)
         
        snowTex = cmds.checkBox(self.snowTexCB, q=True, value=True)
         
        grassTex = cmds.checkBox(self.grassTexCB, q=True, value=True)
        gRandomTex = cmds.checkBox(self.randomGTexCB, q=True, value=True)
        gTexType = cmds.optionMenuGrp(self.grassTypesOMGrp, q=True, value=True)
        gNumofTex = cmds.intField(self.nOfGrassTexIF, q=True, value=True)
        
        texRepU = cmds.floatSliderGrp(self.texRepeatU, q=True, value=True)
        texRepV = cmds.floatSliderGrp(self.texRepeatV, q=True, value=True)
        texNoiseU = cmds.floatSliderGrp(self.texNoiseV, q=True, value=True)
        texNoiseV = cmds.floatSliderGrp(self.texNoiseV, q=True, value=True)
        imgColSpace = cmds.optionMenuGrp(self.imageColOMGrp, q=True, select=True)
        renColSpace = cmds.optionMenuGrp(self.renderColOMGrp, q=True, select=True)
        
        bDepth = cmds.floatSliderGrp(self.bDepth, q=True, value=True)
        
        rampType = cmds.getAttr('%s.type' % self.ramp)
        rampInterp = cmds.getAttr('%s.interpolation' % self.ramp)
        rampUWave = cmds.getAttr('%s.uWave' % self.ramp)
        rampVWave = cmds.getAttr('%s.vWave' % self.ramp)
        rampNoise = cmds.getAttr('%s.noise' % self.ramp)
        rampNoiseFreq = cmds.getAttr('%s.noiseFreq' % self.ramp)
        
        self.reset_ramp_colours(self.ramp)
        
        rampInfo = self.get_tex_ramp_info(self.ramp)
        cliffPos = []
        grassPos = []
        snowPos = []
        for key,value in rampInfo.items():
            if key == 'ramp':
                continue
            v = Mf.closest_colour(value[1], (GRASS_COLOUR,CLIFF_COLOUR,SNOW_COLOUR))
            if v == CLIFF_COLOUR:
                cliffPos.append(value[0])
            elif v == GRASS_COLOUR:
                grassPos.append(value[0])
            elif v == SNOW_COLOUR:
                snowPos.append(value[0])
            else:
                raise ValueError('Something has gone wrong with ramp colours')
            
        if not(cmds.objExists(pObjectNam)):
            self.error_message(4, pObjectNam)
            check = False
        
        if check:
            tInfo = Main.create_texture(cTexType, nOfCTex=cNumOfTex,
                                cRandTexs=cRandomTex, cliffPos=cliffPos, 
                                snow=snowTex, snowPos=snowPos,
                                grass=grassTex, grassPos=grassPos, 
                                grassType=gTexType, nOfGTex=gNumofTex, 
                                gRandTexs=gRandomTex, uRep=texRepU, 
                                vRep=texRepV, uNoise=texNoiseU, 
                                vNoise=texNoiseV, bDepth=bDepth, 
                                rampType=rampType, rampInterp=rampInterp,
                                rampUWave=rampUWave, rampVWave=rampVWave, 
                                rampNoise=rampNoise, rampFreq=rampNoiseFreq,
                                colSpace=imgColSpace, rendSpace=renColSpace)
             
            Main.assign_terrain_shader(tInfo['lambert'][1], pObjectNam,
                                       tInfo['placements'])
            cmds.select(tInfo['lambert'][0])
        
    def create_interface(self):
        mainForm = cmds.formLayout()
        bannerPane = cmds.paneLayout(height=140, 
                                     bgc=(0.247059, 0.278431, 0.305882))
        imageLayout = cmds.formLayout()
        bannerImg = cmds.image( image=os.path.join(Main.MTG_DIRECTORY,
                                                   'banner.jpg'))
        cmds.formLayout(imageLayout, e=True, attachForm=[(bannerImg, 'left', 0), 
                                                         (bannerImg, 'right', 0), 
                                                         (bannerImg, 'top', 0), 
                                                         (bannerImg, 'bottom', 0)])

        cmds.setParent(mainForm)
        self.polygonObjTFGrp = cmds.textFieldButtonGrp(label='Polygon Object:', 
                                                       buttonLabel='Select', 
                                                       bc=self.select_obj, 
                                                       adj=2, cw=[(1,100)], 
                                                       cat=[(2,'left', 5)])
        
        cmds.setParent('..')
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5, 
                              scr=True, cr=True)
        
        cmds.formLayout(mainForm, e=True, 
                        attachForm=[(bannerPane, 'left', 5), 
                                    (bannerPane, 'top', 5), 
                                    (bannerPane, 'right', 5), 
                                    (tabs, 'left', 5), 
                                    (tabs, 'right', 5), 
                                    (tabs, 'bottom', 5), 
                                    (self.polygonObjTFGrp, 'left', 5), 
                                    (self.polygonObjTFGrp, 'right', 5)], 
                        attachControl=[(tabs, 'top', 2, self.polygonObjTFGrp), 
                                       (self.polygonObjTFGrp, 'top', 2, bannerPane)])
        
        mainTerrainTab = cmds.columnLayout(adjustableColumn=True)
        cmds.frameLayout(label='Load Music', borderStyle='in', cll=True)
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, 
                       columnWidth2=(80, 75), 
                       columnAlign=[(1, 'right'), (2, 'left')], 
                       columnAttach=[(1, 'both', 0), (2, 'both', 0)])
        cmds.text(label='Current Song:')
        self.songText = cmds.text(label=self.currentSong, font="boldLabelFont")
        
        cmds.setParent('..')
        cmds.columnLayout(adjustableColumn=True)
        self.musicLoadGrp = cmds.textFieldButtonGrp(label='Music Location', 
                                                    buttonLabel='Browse', 
                                                    buttonCommand=self.music_browse, 
                                                    adj=2, 
                                                    columnWidth3=(80, 75, 150))
        
        musicForm = cmds.formLayout(numberOfDivisions=100)
        
        self.loadMusicB = cmds.button(label='Load', command=self.load_song, 
                                      width=70)
        self.playMusicB = cmds.button(label='Play', command=self.play_song, 
                                      width=70, enable=False)
        self.reloadMusicB = cmds.button(label='Reload', command=self.reload_song, 
                                        width=70, enable=False)
        self.clearMusicB = cmds.button(label='Clear', command=self.clear_song, 
                                       width=70, enable=False)
        
        cmds.formLayout(musicForm, edit=True, 
                        attachForm=[(self.loadMusicB, "bottom", 5), 
                                    (self.playMusicB, "bottom", 5), 
                                    (self.reloadMusicB, "bottom", 5), 
                                    (self.clearMusicB, "bottom", 5)], 
                        attachControl=[(self.loadMusicB, 'right', 5, self.playMusicB), 
                                       (self.playMusicB, 'right', 5, self.reloadMusicB), 
                                       (self.reloadMusicB, 'right', 5, self.clearMusicB)], 
                        attachPosition=[(self.loadMusicB, "left", 5, 15), 
                                        (self.playMusicB, "left", 5, 34), 
                                        (self.reloadMusicB, "left", 5, 53), 
                                        (self.clearMusicB, "left", 5, 71), 
                                        (self.clearMusicB, "right", 5, 90)], 
                        attachNone=[(self.loadMusicB, "top"), 
                                    (self.playMusicB, "top"), 
                                    (self.reloadMusicB, "top"), 
                                    (self.clearMusicB, "top")])

        cmds.setParent('..')
        cmds.frameLayout(label='Sound Scrubber', borderStyle='in', cll=True)
        
        cmds.columnLayout(adjustableColumn=True)
        self.soundScrb = cmds.soundControl(height=45, displaySound=True, 
                                           waveform='both')
        self.soundCtrl = cmds.rangeControl(minRange=1, maxRange=25, height=20)
        
        cmds.setParent(mainTerrainTab)
        cmds.frameLayout(label='Terrain Generator', borderStyle='in', cll=True)
        
        terrainOptColLayout = cmds.columnLayout(adjustableColumn=True)
        self.deformMagFSlGrp = cmds.floatSliderGrp(label='Deform Magnitude:', 
                                                   field=True, minValue=0, 
                                                   fieldMaxValue=100000, 
                                                   value=10, adj=3, 
                                                   cw=[(1,100)], 
                                                   cat=[(2,'left', 5)])
        self.deformDirCBGrp = cmds.checkBoxGrp(numberOfCheckBoxes=4, 
                                               label='Deform Direction:', 
                                               labelArray4=['X', 'Y', 'Z', 'N'], 
                                               cw=[(1,100),(2,50),(3,50),(4,50)], 
                                               cat=[(2,'left', 7)], value2=True)
        self.otherOptCBGrp = cmds.checkBoxGrp(numberOfCheckBoxes=4,
                                              label='Other Options:',
                                              labelArray4=['Negative Values',
                                                           'Separate Deform Direction',
                                                           'Reverse Song', 'Refresh on Deform'],
                                              height=23, cw=[(1,100),(3,150),(4,90)],
                                              cat=[(2,'left', 7)])
        
        cmds.frameLayout(label='Soft Select Options', borderStyle='in', 
                         cll=True)
        
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 150, 75), 
                       columnAlign=[(1, 'right'), (2, 'left'), (3, 'left')], 
                       columnAttach=[(1, 'right', 0), (2, 'left', 5), (3, 'left', 5)], 
                       height=25)
        cmds.text(label='Soft Select:')
        self.sSelectCB = cmds.checkBox(label='', cc=self.toggle_sselect_widgets, 
                                       value=1)
        self.sSelectResetB = cmds.button('Reset', width=50, 
                                         command=self.reset_soft_select_options)
        
        cmds.setParent('..')
        self.falloffModeOMGrp = cmds.optionMenuGrp(label='Falloff Mode:', 
                                                   cw=[(1,100),(3,150)], 
                                                   cat=[(2,'left', 5)])
        cmds.menuItem(label='Volume')
        cmds.menuItem(label='Surface')
        cmds.menuItem(label='Global')
        cmds.menuItem(label='Object')
        
        self.falloffRadFSlGrp = cmds.floatSliderGrp(label='Falloff radius:', 
                                                    field=True, minValue=0, 
                                                    fieldMaxValue=100000, 
                                                    value=5, precision=2, 
                                                    adj=3, cw=[(1,100)], 
                                                    cat=[(2,'left', 5)])
        
        self.falloffCurveRow = cmds.rowLayout(numberOfColumns=2, 
                                              columnWidth2=(100, 200), 
                                              columnAlign=[(1, 'right'), 
                                                           (2, 'left')], 
                                              columnAttach=[(1, 'both', 0), 
                                                            (2, 'left', 5)])
        
        self.default_falloff_curve()
        cmds.text(label='Falloff curve:')
        self.falloffCurveCtrl = cmds.gradientControlNoAttr(h=90, 
                                                           optionVar='softSelectCurve', 
                                                           width=200)
        
        cmds.setParent('..')
        self.interpolationOMGrp = cmds.optionMenuGrp(label='Interpolation:', 
                                                     cw=[(1,100),(3,150)], 
                                                     cat=[(2,'left', 5)], 
                                                     changeCommand=self.change_falloff_key_interp)
        cmds.menuItem(label='None')
        cmds.menuItem(label='Linear')
        cmds.menuItem(label='Smooth')
        cmds.menuItem(label='Spline')
        
        cmds.gradientControlNoAttr(self.falloffCurveCtrl, e=True, 
                                   ckc=self.falloff_curve_change_key)
        
        self.curvePresetsRow = cmds.rowLayout(numberOfColumns=10, 
                                              columnWidth=[(1,100)], 
                                              columnAlign=[(1, 'right')], 
                                              columnAttach=[(1, 'right', 0), 
                                                            (2, 'left', 5)], 
                                              height=25)
        cmds.text(label='Curve presets:')
        cmds.iconTextButton( style='iconOnly', image1='softCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'soft'))
        cmds.iconTextButton( style='iconOnly', image1='mediumCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'medium'))
        cmds.iconTextButton( style='iconOnly', image1='linearCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'linear'))
        cmds.iconTextButton( style='iconOnly', image1='hardCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'hard'))
        cmds.iconTextButton( style='iconOnly', image1='craterCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'crater'))
        cmds.iconTextButton( style='iconOnly', image1='waveCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'wave'))
        cmds.iconTextButton( style='iconOnly', image1='stairsCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'stairs'))
        cmds.iconTextButton( style='iconOnly', image1='ringCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'ring'))
        cmds.iconTextButton( style='iconOnly', image1='sineCurveProfile.png', 
                             c=par(self.change_falloff_curve_prest,'sine'))
        
        cmds.setParent(mainTerrainTab)
        self.generateTerrainB = cmds.button(label='Generate Terrain!', 
                                            height=29, 
                                            command=self.generate_terrain)
        cmds.setParent(tabs)
        
        ##########################################
        mainTexturingTab = cmds.columnLayout(adjustableColumn=True)
        cmds.frameLayout(label='Cliff Textures', borderStyle='in', cll=True)
        
        cliffTypesForm = cmds.formLayout()
        self.randomCTexRow = cmds.rowLayout(numberOfColumns=2, 
                                            columnWidth2=(115, 15), 
                                            columnAlign=[(1, 'right'), 
                                                         (2, 'left')], 
                                            columnAttach=[(1, 'right', 0), 
                                                          (2, 'left', 5)], 
                                            height=25)
        cmds.text(label='Random Textures:')
        self.randomCTexCB = cmds.checkBox(label='', value=0)
        
        cmds.setParent('..')
        self.cliffTypesOMGrp = cmds.optionMenuGrp(label='Cliff Types:', 
                                                  cw=[(1,110),(3,150)], 
                                                  cat=[(2,'left', 5)])
        
        self.cliffTypeFolders = [f for f in os.listdir(Main.CLIFF_TEX_DIR) \
                                 if os.path.isdir(os.path.join(Main.CLIFF_TEX_DIR,f))]
        
        for cliff in self.cliffTypeFolders:
            cmds.menuItem(label=cliff)
            
        nOfCTexRow = cmds.rowLayout(nc=2, cw=[(1,110)], cal=[(1,'right')], 
                                    cat=[(1,'right',0),(2,'left', 5)])
        cmds.text(label='Number of Textures:')
        self.nOfCliffTexIF = cmds.intField(v=3, min=1)
        cmds.setParent('..')
        
        cliffPrevText = cmds.text('Cliff Preview:')
        cliffPreviewPL = cmds.paneLayout(w=65,h=65)
        
        cliffFileNode = self.setup_preview_file('cliffTexturePreview')
        cliffPreviewImg = cmds.swatchDisplayPort(wh=(65,65), sn=cliffFileNode, 
                                                 pc=par(self.update_file_node_swatch, cliffFileNode))
        self.update_preview('cliffTextures', Main.CLIFF_TEX_DIR, cliffFileNode,
                            False, self.cliffTypesOMGrp)
        cmds.setParent('..')
        self.cycleCliffPrevB = cmds.button(label='Cycle Images', 
                                           command=par(self.cycle_preview_img, 
                                                       'cliffTextures', 
                                                       cliffFileNode))
        
        cmds.checkBox(self.randomCTexCB, e=True, 
                      cc=par(self.toggle_randomtex,'cliffTextures', 
                             Main.CLIFF_TEX_DIR, self.cliffTypesOMGrp,
                             cliffFileNode, self.randomCTexCB))
        cmds.optionMenuGrp(self.cliffTypesOMGrp, e=True, 
                           cc=par(self.update_preview, 'cliffTextures', 
                                  Main.CLIFF_TEX_DIR, cliffFileNode, False,
                                  self.cliffTypesOMGrp))
        
        cmds.formLayout(cliffTypesForm, e=True, 
                        attachForm=[(self.randomCTexRow, 'left', 0), 
                                    (self.randomCTexRow, 'top', 5), 
                                    (self.cliffTypesOMGrp, 'left', 5), 
                                    (nOfCTexRow, 'left', 5), 
                                    (cliffPreviewPL, 'top', 5), 
                                    (cliffPreviewPL, 'bottom', 5)], 
                        attachControl=[(cliffPrevText, 'left', 100, self.cliffTypesOMGrp), 
                                       (cliffPreviewPL, 'left', 5, cliffPrevText), 
                                       (nOfCTexRow, 'top', 5, self.cliffTypesOMGrp), 
                                       (self.cliffTypesOMGrp, 'top', 5, self.randomCTexRow), 
                                       (self.cycleCliffPrevB, 'left', 5, cliffPreviewPL)], 
                        attachNone=[(nOfCTexRow,'bottom'), 
                                    (self.randomCTexRow, 'right'), 
                                    (cliffPrevText, 'bottom'), 
                                    (self.cycleCliffPrevB, 'right')], 
                        attachPosition=[(self.cycleCliffPrevB, 'top', 0, 40), 
                                        (cliffPrevText, 'top', 0, 45)])
        
        cmds.setParent(mainTexturingTab)
        cmds.frameLayout(label='Other Textures', borderStyle='in', cll=True)
        
        self.snowTexRow = cmds.rowLayout(numberOfColumns=2, 
                                         columnWidth2=(115, 15), 
                                         columnAlign=[(1, 'right'), 
                                                      (2, 'left')], 
                                         columnAttach=[(1, 'right', 0), 
                                                       (2, 'left', 5)], 
                                         height=25)
        cmds.text(label='Snow Texture:')
        self.snowTexCB = cmds.checkBox(label='', value=1, 
                                       cc=self.check_other_tex_states)
        
        cmds.setParent('..')
        self.grassTexRow = cmds.rowLayout(numberOfColumns=2, 
                                          columnWidth2=(115, 15), 
                                          columnAlign=[(1, 'right'), 
                                                       (2, 'left')], 
                                          columnAttach=[(1, 'right', 0), 
                                                        (2, 'left', 5)], 
                                          height=25)
        cmds.text(label='Grass Texture:')
        self.grassTexCB = cmds.checkBox(label='', value=1, 
                                        cc=self.toggle_visble_grasstex)
        
        cmds.setParent('..')
        
        self.grassTexturesFrame = cmds.frameLayout(label='Grass Textures', 
                                                   borderStyle='in', cll=True)
        
        grassTypesForm = cmds.formLayout()
        self.randomGTexRow = cmds.rowLayout(numberOfColumns=2, 
                                            columnWidth2=(115, 15), 
                                            columnAlign=[(1, 'right'), 
                                                         (2, 'left')], 
                                            columnAttach=[(1, 'right', 0), 
                                                          (2, 'left', 5)], 
                                            height=25)
        cmds.text(label='Random Textures:')
        self.randomGTexCB = cmds.checkBox(label='', value=0)
        
        cmds.setParent('..')
        self.grassTypesOMGrp = cmds.optionMenuGrp(label='Grass Types:', 
                                                  cw=[(1,110),(3,150)], 
                                                  cat=[(2,'left', 5)])
        
        self.grassTypeFolders = [f for f in os.listdir(Main.GRASS_TEX_DIR) \
                                 if os.path.isdir(os.path.join(Main.GRASS_TEX_DIR,f))]
        
        for cliff in self.grassTypeFolders:
            cmds.menuItem(label=cliff)
        
        nOfGTexRow = cmds.rowLayout(nc=2, cw=[(1,110)], cal=[(1,'right')], 
                                    cat=[(1,'right',0),(2,'left', 5)])
        cmds.text(label='Number of Textures:')
        self.nOfGrassTexIF = cmds.intField(v=3, min=1)
        cmds.setParent('..')
        
        self.grassPrevText = cmds.text('Grass Preview:')
        self.grassPreviewPL = cmds.paneLayout(width=65, height=65)
        
        self.grassFileNode = self.setup_preview_file('grassTexturePreview')
        self.grassPreviewImg = cmds.swatchDisplayPort(wh=(65,65), 
                                                      sn=self.grassFileNode, 
                                                      pc=par(self.update_file_node_swatch, 
                                                             self.grassFileNode))
        self.update_preview('grassTextures', Main.GRASS_TEX_DIR,
                            self.grassFileNode , False, self.grassTypesOMGrp)
        cmds.setParent('..')
        cycleGrassPrevB = cmds.button(label='Cycle Images', 
                                      command=par(self.cycle_preview_img, 
                                                  'grassTextures', 
                                                  self.grassFileNode))
        
        cmds.checkBox(self.randomGTexCB, e=True, 
                      cc=par(self.toggle_randomtex,'grassTextures', 
                             Main.GRASS_TEX_DIR, self.grassTypesOMGrp,
                             self.grassFileNode, self.randomGTexCB))
        cmds.optionMenuGrp(self.grassTypesOMGrp, e=True, 
                           cc=par(self.update_preview, 'grassTextures', 
                                  Main.GRASS_TEX_DIR, self.grassFileNode,
                                  False, self.grassTypesOMGrp))
        
        cmds.formLayout(grassTypesForm, e=True, 
                        attachForm=[(self.randomGTexRow, 'left', 0), 
                                    (self.randomGTexRow, 'top', 5), 
                                    (self.grassTypesOMGrp, 'left', 5), 
                                    (nOfGTexRow, 'left', 5), 
                                    (self.grassPreviewPL, 'top', 5), 
                                    (self.grassPreviewPL, 'bottom', 5)], 
                        attachControl=[(self.grassPrevText, 'left', 85, self.grassTypesOMGrp), 
                                       (self.grassPreviewPL, 'left', 5, self.grassPrevText), 
                                       (nOfGTexRow, 'top', 5, self.grassTypesOMGrp), 
                                       (self.grassTypesOMGrp, 'top', 5, self.randomGTexRow), 
                                       (cycleGrassPrevB, 'left', 5, self.grassPreviewPL)], 
                        attachNone=[(nOfGTexRow,'bottom'), 
                                    (self.randomGTexRow, 'right'),
                                    (self.grassPrevText, 'bottom'), 
                                    (cycleGrassPrevB, 'right')], 
                        attachPosition=[(cycleGrassPrevB, 'top', 0, 40), 
                                        (self.grassPrevText, 'top', 0, 45)])

        cmds.setParent(mainTexturingTab)
        
        otherOptions = cmds.frameLayout(label='Other Options', 
                                        borderStyle='in', cll=True)
        
        self.texRepeatU = cmds.floatSliderGrp(label='Texture Repetition U:', 
                                              field=True, minValue=0, 
                                              maxValue=5, fieldMaxValue=100000, 
                                              value=1.25, precision=3, adj=3, 
                                              cw=[(1,110)], cat=[(2,'left', 5)])
        self.texRepeatV = cmds.floatSliderGrp(label='Texture Repetition V:', 
                                              field=True, minValue=0, maxValue=5, 
                                              fieldMaxValue=100000, value=1.25, 
                                              precision=3, adj=3, cw=[(1,110)], 
                                              cat=[(2,'left', 5)])
        
        self.texNoiseU = cmds.floatSliderGrp(label='Texture Noise U:', 
                                             field=True, minValue=0, 
                                             maxValue=5, fieldMaxValue=100000, 
                                             value=0.01, precision=3, adj=3, 
                                             cw=[(1,110)], cat=[(2,'left', 5)])
        self.texNoiseV = cmds.floatSliderGrp(label='Texture Noise V:', 
                                             field=True, minValue=0, 
                                             maxValue=5, fieldMaxValue=100000, 
                                             value=0.01, precision=3, adj=3, 
                                             cw=[(1,110)], cat=[(2,'left', 5)])
        
        self.bDepth = cmds.floatSliderGrp(label='Bump Depth:', field=True, 
                                          minValue=-5, maxValue=5, 
                                          fieldMaxValue=100000, 
                                          fieldMinValue=-100000, value=0.4, 
                                          precision=3, adj=3, cw=[(1,110)], 
                                          cat=[(2,'left', 5)])

        cmds.rowLayout(nc=2, cw=[(1, 210)], cal=[(1, 'right')], cat=[(1, 'right', 0), (2, 'left', 5)])

        self.imageColOMGrp = cmds.optionMenuGrp(label='Image Colour Space:',
                                                  cw=[(1,110),(3,150)],
                                                  cat=[(2,'left', 5)])

        cmds.menuItem('sRGB')
        cmds.menuItem('Linear sRGB')

        self.renderColOMGrp = cmds.optionMenuGrp(label='Render Colour Space:',
                                                  cw=[(1,110),(3,150)],
                                                  cat=[(2,'left', 5)])

        cmds.menuItem('sRGB')
        cmds.menuItem('Linear sRGB')
        
        cmds.setParent('..')
        cmds.setParent('..')
        self.texPosFrame = cmds.frameLayout(label='Texture Positioning', 
                                            borderStyle='in', cll=True)
        
        self.setup_texture_pos_ramp()
        
        sampleRow = cmds.rowLayout(numberOfColumns=2, cw=[(1,225)], 
                                   cal=[(1,'right')], cat=[(1,'right',5)])
        cmds.text('Sample')
        cmds.paneLayout(width=65, height=65)
        self.rampPreviewImg = cmds.swatchDisplayPort(wh=(65, 65), 
                                                     sn=self.ramp, 
                                                     pc=par(self.update_file_node_swatch, 
                                                            self.ramp))
        
        cmds.setParent(self.texPosFrame)
        cmds.columnLayout(adj=True)
        
        self.rampType = cmds.attrEnumOptionMenuGrp(label='Type', 
                                                   attribute='%s.type' % self.ramp, 
                                                   cw=[(1,110),(3,150)], 
                                                   cat=[(2,'left', 5)])
        self.rampInterpol = cmds.attrEnumOptionMenuGrp(label='Interpolation', 
                                                       attribute='%s.interpolation' % self.ramp, 
                                                       cw=[(1,110),(3,150)], cat=[(2,'left', 5)])
        
        rampRow = cmds.rowLayout(nc=2, cw=[(1,275)], cal=[(1,'right')], 
                                 cat=[(1,'right',5)])
        self.rampCliffTex = cmds.rampColorPort(node=self.ramp)
        self.resetButton = cmds.button(label='Reset', 
                                       command=par(self.reset_ramp, self.ramp, 
                                                   self.snowTexCB, 
                                                   self.grassTexCB))
        cmds.setParent('..')
        
        entryTypRow = cmds.rowLayout(nc=2)
        self.entryTypeOMGrp = cmds.optionMenuGrp(label='Entry Type:', 
                                                 cw=[(1,110),(3,150)], 
                                                 cat=[(2,'left', 5)])
        self.cliffEntry = cmds.menuItem(label='Cliff')
        self.snowEntry = cmds.menuItem(label='Snow')
        self.grassEntry = cmds.menuItem(label='Grass')
        self.createEntryButton = cmds.button(label='Create Entry', 
                                             command=par(self.create_entry, 
                                                         self.entryTypeOMGrp, 
                                                         self.ramp))
        cmds.setParent('..')
        selectedPosition = cmds.attrFieldSliderGrp(label='Selected Position', 
                                                   adj=3, cw=[(1,110),(3,150)], 
                                                   cat=[(2,'left', 5)])
        
        cmds.rampColorPort(self.rampCliffTex, e=True, sp= selectedPosition)
        
        self.uWaveSl = cmds.attrFieldSliderGrp(at='%s.uWave' % self.ramp, 
                                               columnWidth=(4,0), adj=3, 
                                               cw=[(1,110),(3,150)], 
                                               cat=[(2,'left', 5)])
        self.vWaveSl = cmds.attrFieldSliderGrp(at='%s.vWave' % self.ramp, 
                                               columnWidth=(4,0), adj=3, 
                                               cw=[(1,110),(3,150)], 
                                               cat=[(2,'left', 5)])
        self.noiseSl = cmds.attrFieldSliderGrp(at='%s.noise' % self.ramp, 
                                               columnWidth=(4,0), adj=3, 
                                               cw=[(1,110),(3,150)], 
                                               cat=[(2,'left', 5)])
        self.freqSl = cmds.attrFieldSliderGrp(at='%s.noiseFreq' % self.ramp, 
                                              columnWidth=(4,0), adj=3, 
                                              cw=[(1,110),(3,150)], 
                                              cat=[(2,'left', 5)])
        
        cmds.setParent(mainTexturingTab)
        self.generateTerrainB = cmds.button(label='Generate Texture!', 
                                            height=29, 
                                            command=self.generate_texture)
        cmds.tabLayout(tabs, edit=True, 
                       tabLabel=((mainTerrainTab, 'Terrain'), 
                                 (mainTexturingTab, 'Texturing')) )


def run():
    win = MTGGui('MTGWindow')
    return win
        
if __name__ == "__main__":
    window = run()
