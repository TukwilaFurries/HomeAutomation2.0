#!/usr/bin/python3

from models.color import Color

# Macro Defines
FADETIME_MIN = 0
LOOPTIME_MIN = 0
BRIGHT_MIN = 0
BRIGHT_MAX = 255

# Custom Exceptions
class PatternExceptionNotArray(Exception):
    def __init__(self):
        Exception.__init__(self, "Pattern class recieved something other than array of Color objects")

class PatternExceptionInvalidEntry(Exception):
    def __init__(self):
        Exception.__init__(self, "Pattern recieved array of something other than Color objects")

class PatternExceptionFadeTimeNotInteger(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured fade time (" + str(value) + ") is not integer")

class PatternExceptionFadeTimeBelowMinimum(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured fade time (" + str(value) + ") is below minimum value of " + str(LOOPTIME_MIN))

class PatternExceptionLoopTimeNotInteger(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured loop time (" + str(value) + ") is not an integer")

class PatternExceptionLoopTimeBelowMinimum(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured loop time (" + str(value) + ") is below minimum value of " + str(FADETIME_MIN))
    
class PatternExceptionBrightLevelNotInteger(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured brightness level (" + str(value) + ") is not an integer")

class PatternExceptionBrightLevelBelowMinimum(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured brightness level (" + str(value) + ") is below minimum value of " + str(BRIGHT_MIN))

class PatternExceptionBrightLevelAboveMaximum(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Configured brightness level (" + str(value) + ") is above maximum value of " + str(BRIGHT_MAX))

#Private Methods
def validateColors(colors):
    # None is okay
    if colors is None:
        return colors

    # Ensure array of Color objects
    if type(colors) is not list:
        raise PatternExceptionNotArray()
    
    # Everything is a Color object
    for color in colors:
        if type(color) is not Color:
            raise PatternExceptionInvalidEntry()

    return colors

def validateFadeTime(fadeTime):
    if type(fadeTime) is not int:
        raise PatternExceptionFadeTimeNotInteger(fadeTime)
    if fadeTime < FADETIME_MIN:
        raise PatternExceptionFadeTimeBelowMinimum(fadeTime)
    return fadeTime

def validateLoopTime(loopTime):
    if type(loopTime) is not int:
        raise PatternExceptionLoopTimeNotInteger(loopTime)
    if loopTime < LOOPTIME_MIN:
        raise PatternExceptionLoopTimeBelowMinimum(loopTime)
    return loopTime

def validateBrightLevel(brightLevel):
    if type(brightLevel) is not int:
        raise PatternExceptionBrightLevelNotInteger(brightLevel)
    if brightLevel < BRIGHT_MIN:
        raise PatternExceptionBrightLevelBelowMinimum(brightLevel)
    if brightLevel > BRIGHT_MAX:
        raise PatternExceptionBrightLevelAboveMaximum(brightLevel)
    return brightLevel

# A Pattern contains an array of Colors
class Pattern:
       
    # colorsIn = array of Color objects
    def __init__(self, colors=None, fadeTime=0, loopTime=0, brightLevel=0):
        self.colors     = validateColors(colors)
        self.fadeTime   = validateFadeTime(fadeTime)
        self.loopTime   = validateLoopTime(loopTime) 
        self.brightLevel = validateBrightLevel(brightLevel)

    ##### Public Getters
    def getColors(self):
        return self.colors
    def getNumColors(self):
        if self.colors is None:
            return 0
        return len(self.colors)

    def getLoopTime(self):
        return self.loopTime
    def getFadeTime(self):
        return self.fadeTime
    def getBrightLevel(self):
        return self.brightLevel
    def getColor(self, patternIndex):
        return self.colors[patternIndex]


    ##### Public Setters
    def setColors(self, colors):
        self.colors = validateColors(colors)

    def setFadeTime(self, fadeTime):
        self.fadeTime = validateFadeTime(fadeTime)
        
    def setLoopTime(self, loopTime):
        self.loopTime = validateLoopTime(loopTime)
    
    def setBrightLevel(self, brightLevel):
        self.brightLevel = validateBrightLevel(brightLevel)
