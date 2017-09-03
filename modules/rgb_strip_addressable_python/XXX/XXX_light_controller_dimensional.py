#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import termios
import tty
import pigpio
import time
import signal 
from decimal import *
import threading

#from Framework import logging as log
from Modules.RGB.light_model import *
import config

# TODO:
#   Exception Handling
#   Logging (NoLog, Status Messages, Debugging Messages, Full Trace)
MIN_RGB_VALUE =0  # No smaller than 0
MAX_RGB_VALUE =255 # No bigger than 255.
TRANSITION_DELAY = 10  # In milliseconds, between individual light changes
WAIT_DELAY = 500         # In milliseconds, at the end of each traversal, wait for this long    
    
class coord():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vertex = []

class PiLights:
    RED_PIN   = 17
    GREEN_PIN = 22
    BLUE_PIN  = 24

    def dicks(self):
        print "PiLights.dicks()"

    def lockMainLoop(self):
        #log.rgb_log(log.LEVEL.VERBOSE, "lockMainLoop()")
        self.mainLoopLock = True

    def unlockMainLoop(self):
        #log.rgb_log(log.LEVEL.VERBOSE, "unlockMainLoop()")
        self.mainLoopLock = False

    def setFadeTime(self, ft):
        #log.rgb_log(log.LEVEL.STATUS, "Fade Time Changed to " + str(ft))
        self.mainLoopLock = True      
        self.fadeTime = ft
        self.mainLoopLock = False
        self.configChagned = True

    def setLoopTime(self, lt):
        #log.rgb_log(log.LEVEL.STATUS, "Loop Time Changed to " + str(lt))
        self.mainLoopLock = True
        self.loopTime = lt
        self.mainLoopLock = False
        self.configChanged = True

    def setBrightLevel(self, bl):
        #log.rgb_log(log.LEVEL.STATUS, "Brightness Chanes to " + str(bl))
        self.mainLoopLock = True       
        self.brightLevel = bl
        self.mainLoopLock = False
        self.configChanged = True

    def setColorPattern(self, cp):
        #log.rgb_log(log.LEVEL.STATUS, "colorPattern: " + self.cp)
        self.mainLoopLock = True
        self.colorPattern = cp
        self.mainLoopLock = False
        self.configChanged = True

    def setPattern(self, p):
        #log.rgb_log(log.LEVEL.VERBOSE, "setPattern()") 
        self.mainLoopLock = True
        self.fadeTime = p.getFadeTime()
        self.loopTime = p.getLoopTime()
        self.brightLevel = p.getBrightLevel()
        self.colorPattern = p.getColors()

        #log.rgb_log(log.LEVEL.STATUS, "Fade Time Changed to " + str(self.fadeTime))
        #log.rgb_log(log.LEVEL.STATUS, "Loop Time Changed to " + str(self.loopTime))
        #log.rgb_log(log.LEVEL.STATUS, "Brightnes Changed to " + str(self.brightLevel))
        #log.rgb_log(log.LEVEL.STATUS, "Pattern changed to " + str(self.colorPattern))
        self.mainLoopLock = False
        self.configChanged = True

    def killProgram(self):
        #log.rgb_log(log.LEVEL.STATUS, "killProgram()")
        self.kill = True
        self.configChanged = True
        self.mainLoopThread.join()
        self.pi.stop()

    def updateColor(self, color, step):
        color += step
        if color > 255:
            return 255
        if color < 0:
            return 0
        return color

    def setLights(self, pin, brightness, bright):
        #log.rgb_log(log.LEVEL.DEBUG, "Setting Pin " + str(pin) + " = " + str(brightness))
        brightness = self.updateColor(brightness, 0)
        realBrightness = int(int(brightness) * (float(bright) / 255.0))
        self.pi.set_PWM_dutycycle(pin, realBrightness)

    # fadeTime
    # loopTime
    # brightLevel
    # pattern
    
    # Total Traversal time is ((MAX_RGB_VALUE - MIN_RGB_VALUE) GB LED - Automatic Smooth Color Cycling
    
    # Marco Colli
    # April 2012
    #
    # Uses the properties of the RGB Colour Cube
    # The RGB colour space can be viewed as a cube of colour. If we assume a cube of dimension 1, then the 
    # coordinates of the vertices for the cubve will range from (0,0,0) to (1,1,1) (all black to all white).
    # The transitions between each vertex will be a smooth colour flow and we can exploit this by using the 
    # path coordinates as the LED transition effect. 
    #
    #
    # Vertices of a cube     
    #    C+----------+G
    #    /|        / |
    #  B+---------+F |
    #   | |       |  |    y   
    #   |D+-------|--+H   ^  7 z
    #   |/        | /     | /
    #  A+---------+E      +--->x

       
    def smartLoop(self):
        #log.rgb_log(log.LEVEL.DEBUG, "smartLoop()")
        self.v = coord(0,0,0); 

        vertex = []
        vertex.append(coord(0,0,0)) # A or 0 or 0000
        vertex.append(coord(0,1,0)) # B or 1 or 0001
        vertex.append(coord(0,1,1)) # C or 2 or 0010
        vertex.append(coord(0,0,1)) # D or 3 or 0011
        vertex.append(coord(1,0,0)) # E or 4 or 0100
        vertex.append(coord(1,1,0)) # F or 5 or 0101
        vertex.append(coord(1,1,1)) # G or 6 or 0110
        vertex.append(coord(1,0,1)) # H or 7 or 0111

        # A list of vertex numbers encoded 2 per byte.
        # Hex digits are used as vertices 0-7 fit nicely (3 bits 000-111) and have the same visual
        # representation as decimal, so bytes 0x12, 0x34 ... should be interpreted as vertex 1 to 
        # v2 to v3 to v4 (ie, one continuous path B to C to D to E).
        # 0000 0001 A->B 0 1
        # 0010 0011 C->D 2 3
        # 0111 0110 H->G 7 6
        # 0101 0100 F->E 5 4
        # 0000 0011 A->D 0 4
        # 0010 0001 C->B 2 1
        # 0101 0110 F->G 5 6 
        # 0111 0100 H->E 7 4
        # 0001 0011 B->D 1 3
        # 0110 0100 G->E 6 4
        # 0001 0110 B->G 1 6
        # 0000 0010 A->C 0 2
        # 0111 0101 H->F 7 5
        # 0010 0100 C->E 2 4
        # 0011 0101 D->G 3 6 
        # 0001 0111 B->H 1 7 
        # 0010 0101 C->F 2 5
        # 0111 0000 H->A 7 0

        path = [0, 1, 2, 3, 7, 6, 5, 4,
                0, 4, 2, 1, 5, 6, 7, 4,
                1, 3, 6, 4, 1, 6, 0, 2,
                7, 5, 2, 4, 3, 6, 1, 7,
                2, 5, 7, 0]
        v1 = 0
        v2 = 0 # the new vertex and the previous one

        # initialize the place we start from as the first vector in the array
        if vertex[v2].x == 1:
            self.v.x = MAX_RGB_VALUE
        else:
            self.v.x = MIN_RGB_VALUE        
        
        if vertex[v2].y == 1:
            self.v.y = MAX_RGB_VALUE
        else:
            self.v.y = MIN_RGB_VALUE

        if vertex[v2].z == 1:
            self.v.z = MAX_RGB_VALUE
        else:
            self.v.z = MIN_RGB_VALUE

        # Now just loop through the path, traversing from one point to the next
        for i in range(0, len(path)):       
            v1 = v2
            if i % 2 == 1: # Odd number is the second element and...
                v2 = path[i>>1] & 0xf; # ... the bottom nybble (index /2) or...
            else:
                v2 = path[i>>1] >> 4 # .. the top nybble
            #print "v1 = " +str(v1)
            #print "v2 = " + str(v2)
            self.traverse(vertex[v2].x - vertex[v1].x,
                          vertex[v2].y - vertex[v1].y,
                          vertex[v2].z - vertex[v1].z)

    # Move along the color line from where wqe are to the next vertex of the cube.
    # The transition is achieved by applying the 'delta' value to the coordinate.
    # By definition, all coordinates will complete the transition at the same time as we only have one loop index.
    def traverse(self, dx, dy, dz):
#        print "traverse(" + str(dx) + "," + str(dy) + ","+str(dz) + ") { "
        if (dx == 0) and (dy == 0) and (dz == 0):
            return;

        for i in range(0, MAX_RGB_VALUE-MIN_RGB_VALUE):
            self.setLights(self.RED_PIN, self.v.x, self.brightLevel)
            self.setLights(self.GREEN_PIN, self.v.y, self.brightLevel)
            self.setLights(self.BLUE_PIN, self.v.z, self.brightLevel)

            time.sleep(float(TRANSITION_DELAY/1000.0))
            MULT=1
            self.v.x += (MULT * dx)
            self.v.y += (MULT * dy)
            self.v.z += (MULT * dz)

        time.sleep(float(WAIT_DELAY/1000.0))

    def __init__(self):
        self.kill = False
        self.fadeTime = 1
        self.loopTime = 1
        self.brightLevel = 1
        self.colorPattern = [] 

        self.pi = pigpio.pi()
        self.mainLoopThread = threading.Thread(target=self.smartLoop)
        self.mainLoopThread.daemon = True
        self.mainLoopLock = False      
        self.mainLoopThread.start()
if __name__ == '__main__':
   print "GO" 
   piLights = PiLights()
   numColors = 3
   fadeTime = 3
   loopTime = 1
   brightLevel = 255 
   A=85
   B=170
   C=255
   colors = [ [A,B,C], [B,C,A], [C,A,B]]
   #colors = [ [0, 128, 255], [128, 255, 0], [255, 0, 128]]
   pattern = Pattern(numColors, fadeTime, loopTime, brightLevel, colors)

   #config.GLOBAL.LOG.LEVEL = log.LEVEL.VERBOSE
   #config.GLOBAL.LOG.OUTPUT = log.OUTPUT.BOTH

   print "Beginning Program Now"
   piLights.setPattern(pattern)

   while True:
       try:
          pass
       except KeyboardInterrupt:
            print "Quitting"
            piLights.killProgram()
            break
