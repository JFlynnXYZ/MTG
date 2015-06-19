r'''Module containing a class structure for creating terrain from music.
   
   The idea behind this modules is that it includes the class 'TerrainWaveFile' 
   which inherits the 'wave.Wave_read' class which is used to read wave or 
   .WAV files. I have added to this base class to incorporate some more useful 
   variables for my script. However, a lot of the values and functions were 
   not used in the final script. Only the 'createheightvals' function is 
   really relevant, as this function creates the move distances for each 
   vertex of a poly object.
   
   For example, we can generate a list of move values by a) first creating a
   VertexWaveFile object and b) using the objects function for 
   'createheightvals' to get the required values necessary to create terrain. 
   To test the code, however, you will need to supply a song path for variable 
   'song'
   
       >>> import maya.cmds as cmds
       >>> #change musicLocation to a song in your directory to test the functions
       >>> song = 'D:\\Users\\Jon\\workspace\\Terraign Generator\\01 Window.wav'
       >>> songInfo = TerrainWaveFile(song)
       >>> pPlane = cmds.polyPlane(w=48, h=48, sx=24, sy=24)
       >>> nOfVerts = cmds.polyEvaluate(v=True)
       >>> nOfVerts
       625
       >>> tHeightVals = songInfo.createheightvals(nOfVerts, 16, False)
       >>> len(tHeightVals)
       625
       >>> "%.0f" % max(tHeightVals)
       '16'
       >>> # clean up
       >>> cmds.delete(pPlane)
       
    To test/execute the examples in the module documentation make sure that 
    you have an empty scene first, then once you have imported the 
    terrainWave module:
    import doctest
    nfail, ntests = doctest.testmod(terrainWave)
    
'''
import wave 
import struct
import datetime
import math
import itertools

class TerrainWaveFile(wave.Wave_read):
    '''Allows for the opening of a wave file with more built in variables and
    can create height values for creating terrain.
    
    Parameters:
        path [string] : This is the song path which will be read by the class
    
    Attributes:
        _samplesize [int]      : The sample size for the song. Usually 16 for
                                 stereo and 8 for mono
        _songlength [float]    : The length of the song in seconds
        _unpackstructval [str] : The number of binary values to unpack. This 
                                 is used when the amplitude values are read 
                                 from the song file
        _maxamplitude [int]    : The maximum amplitude from the signed bits
                                 read from the song
                                 
    '''
    def __init__(self, path, q=None):
        wave.Wave_read.__init__(self, path)
        self._samplesize = self._sampwidth * 8
        self._songlength = float(self._nframes) / self._framerate 
        self._unpackstructval = 'h' * ((self._nchannels*self._sampwidth) / 2)
        self._maxamplidtude = 2 ** self._samplesize/2
        self.stop = False
        self.queue = q
        self.vtxsample = 0

    def parsedata(self, i):
        if self.queue:
            self.queue.put(i)
        return struct.unpack(self._unpackstructval*self.vtxsample, self.readframes(self.vtxsample))

    def convertAbsolute(self, amps, i):
        if self.queue:
            self.queue.put(i)
        return [~x+1 if x < 0 else x for x in amps]

    def averageAmps(self, amps, i):
        if self.queue:
            self.queue.put(i)
        return sum(amps)/len(amps)

    def relativeScale(self, amps, hRatio, i):
        if self.queue:
            self.queue.put(i)
        return amps * hRatio

    def createheightvals(self, nvtx, vheight, negative=False):
        '''Samples the music and creates a list of height values. The song is
        sampled for all of the frames divided by the 'nvtx'. Then, all of 
        those values are averaged to get a final value for each vertex.
        
        Parameters:
            nvtx [int]      : The number of vertices of the object or the 
                              number of height values to be created from the 
                              song amplitudes
            vheight [float] : The value from which all the height values will 
                              be created. This will be the highest value 
                              and/or lowest if 'negative' is True.
            negative [bool] : If True, the values returned will include 
                              positive and negative values. If False, the 
                              values returned will be all positive.
                              
        On Exit:
            Returns a list of float values with length 'nvtx', with maximum 
            or minimum value of 'vheight'.
        
        '''
        self.rewind()  # Starts the song reading from the beginning
        
        self.vtxsample = math.trunc(float(self._nframes)/nvtx)
        # vtxsample stores the number of amplitude frames to average for each
        # vertex rounded up
        if self.queue:
            self.queue.put(('Reading WAV Data', nvtx))
        allAmps = [self.parsedata(i) for i in xrange(nvtx)]
        #allAmps stores all the amplitude values in tuples for each vertex

        if not(negative): #Turns all the values positive if negative=False
            if self.queue:
                self.queue.put(('Converting all Values to Positive', len(allAmps)))
            allAmps = [self.convertAbsolute(allAmps[i], i) for i in xrange(len(allAmps))]

        if self.queue:
            self.queue.put(('Averaging Amplitude values', len(allAmps)))
        allAmps = [self.averageAmps(allAmps[i], i) for i in xrange(len(allAmps))] #finds the average of
                                                        #each tuple value
        hRatio = float(vheight) / max(allAmps) 
        #hRatio is the value to multiply each averaged allAmp value to reflect
        #a maximum of vheight
        if self.queue:
            self.queue.put(('Scaling to Magnitude Value', len(allAmps)))
        return tuple(self.relativeScale(allAmps[i], hRatio, i) for i in xrange(len(allAmps)))
                      
    def getsamplesize(self):
        '''Returns the sample size for the song'''
        return self._samplesize
    
    def getsonglength(self):
        '''Returns the song length for the song in seconds'''
        return self._songlength
    
    def getsonglengthtime(self):
        '''Returns the song length in the form "h:mm:ss.msmsms"'''
        return str(datetime.timedelta(seconds=self._songlength))
    
    def getmaxamplitude(self):
        '''Returns the maximum amplitede for the song'''
        return self._maxamplitude

     
if __name__ == "__main__":
    songLink = 'D:\\Users\\Jon\\workspace\\Terraign Generator\\01 Heaven Never Seemed So Close.wav'
    songInfo = TerrainWaveFile(songLink)
    print songInfo.createheightvals(100, 15)
    