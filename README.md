# MTG :: Music Terrain Generator

![MTG](http://jfdesigner.co.uk/wp-content/uploads/2015/10/MTG-banner.png "MTG")


Music Terrain Generator (MTG) for Maya is a script that produces terrain from WAV audio files. It is not only limited to plane geometry and can be used on any Polygon based object to manipulate based on the amplitude of a song file. It also has the ability to procedurally texture the terrain as well. It does this in the following steps:

  - You select some Polygon geometry in your Maya scene
  - Load in a .wav file into the program
  - Set the settings and generate the terrain
  - Follow this up with texturing the selected object as well

### Version
1.1.0

### Tech

Tested on Maya 2014 and briefly on 2015. Not 100% sure how compatible it is for future versions of Maya.

MTG only needs the Maya Python environment to work.

### Installation

1. Install Autodesk Maya
2. Clone the directory and move all the files within "scripts" into a Maya scripts folder
	- An example folder you can place it in is "<user>\Documents\maya\2014-x64\scripts"
3. To then run the script, in the Script Editor window, click 'Source Script...' button and find the 'mtg.py' file to run.

After that, you should be good to go!

### How to Use

To use the program, simply run the script, select a mesh in the scene and click "Select" in the top right, followed by loading a song in the "Music Location" section by browsing for a song and clicking "Load". Adjust the settings how you like and click "Generate".

For more detailed instructions, see https://github.com/JFDesigner/MTG/blob/master/docs/UserManual.pdf

### To-Do

I most likely won't make any changes to the program from now as it's an old assignment I completed for my course (Computer Visualisation & Animation) at the NCCA. The final version was published on 19/06/2015.

I tried implementing a progress window with some Threading but Maya only uses one main thread for its commands and this means that I would have to re-work the entire code to get that working. Bare in mind that if you start the script to generate Terrain that you have the time to finish it since there is no way of exiting out of the currently running script.

## Contact

If you have problems or questions then please contact me by emailing me at jonflynn@jfdesigner.co.uk.

## Website

Visit my portfolio to see more of my work and interesting programs at http://jfdesigner.co.uk/

License
----

GPL V2
