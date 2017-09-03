#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pigpio
import signal 
from decimal import *
from multiprocessing.managers import BaseManager
from Modules.RGB.light_model import *
import pi_config
from time import sleep
from Framework.home_automation_logging import HomeAutomationLogging


class MyLoggingManager(BaseManager): pass

class MainLoopStatus:
    START   = 0 # Loop Start Requested
    STARTED = 1 # Loop Has Started
    KILL    = 2 # Please kill the loop / thread
    STOP    = 3 # Loop Stop Requested but thread remains active
    STOPPED = 4 # Loop Has Stopped, thread is exiting

class PiLights:

    def setFadeTime(self, ft):
        self.getLog().info("Fade Time Changed to " + str(ft))
        self.fadeTime = ft
        self.configChagned = True
    def getFadeTime(self):
        return self.fadeTime

    def setLoopTime(self, lt):
        self.getLog().info("Loop Time Changed to " + str(lt))
        self.loopTime = lt
        self.configChanged = True
    def getLoopTime(self):
        return self.loopTime

    def setBrightLevel(self, bl):
        self.getLog().info("Brightness Chanes to " + str(bl))
        self.brightLevel = bl
        self.configChanged = True
    def getBrightLevel(self):
        return self.brightLevel

    def setColorPattern(self, cp):
        self.getLog().debug("setColorPattern() {")
        self.colorPattern = cp
        self.numColors = len(cp)
        self.configChanged = True
        self.getLog().debug("} setColorPattern()")

    def getColorPattern(self):
        return self.colorPattern
    
    def getNumColors(self):
        return self.numColors

    def setNumColors(self, num):
        self.getLog().info("Number of Colors Changed to: " + str(num))
        self.numColors = num
    
    def setConfigChanged(self, changed):
        self.configChanged = changed
    def getConfigChanged(self):
        return self.configChanged

    def setPattern(self, p):
        self.getLog().info("New Pattern Recieved:" + str(p))
        self.setFadeTime(p.getFadeTime())
        self.setLoopTime(p.getLoopTime())
        self.setBrightLevel(p.getBrightLevel())
        self.setColorPattern(p.getColors())
        self.setNumColors(p.getNumColors())
        self.setConfigChanged(True)
        if self.logging_enabled: self.getLog().debug("} setPattern()")

    
    def updateColor(self, color, step):
        color += step
        if color > 255:
            return 255
        if color < 0:
            return 0
        return color

    def setLights(self, pin, brightness, bright):
        brightness = self.updateColor(brightness, 0)
        realBrightness = int(int(brightness) * (float(bright) / 255.0))
        self.pi.set_PWM_dutycycle(pin, realBrightness)

    def getLog(self):
        return self.log
    

    def getMainLoopStatus(self):
        return self.mainLoopStatus
    def setMainLoopStatus(self, mainLoopStatus):
        self.mainLoopStatus = mainLoopStatus

    def killProgram(self):
        self.getLog().info("Kill Program Recieved")
        self.mainLoopStatus = MainLoopStatus.KILL
        self.configChanged = True
        
        # Wait for main loop to exit on its own
        while self.mainLoopStatus is not MainLoopStatus.STOPPED:
            sleep(0.1)
            pass
        else:
            self.pi.stop()

    def stopProgram(self):
        self.setLights(pi_config.RGB.getPinR(), 0, 0)
        self.setLights(pi_config.RGB.getPinG(), 0, 0)
        self.setLights(pi_config.RGB.getPinB(), 0, 0)



    def __init__(self):
        self.logging_enabled = True
        print("I SHOULD BE FIRST")
        self.mainLoopStatus = MainLoopStatus.START

        self.fadeTime = 1
        self.loopTime = 1
        self.brightLevel = 1
        self.colorPattern = [] 
        self.numColors = 0
        self.pi = pigpio.pi()
        self.configChanged = False
        if self.logging_enabled:
            MyLoggingManager.register('HomeAutomationLogging', HomeAutomationLogging)
            self.logging_manager = MyLoggingManager()
            self.logging_manager.daemon = True
            self.logging_manager.start()
            self.log = self.logging_manager.HomeAutomationLogging("RGB", pi_config.RGB.getLogLocation())
        #self.process = mp.Process(target=mainLoop, args=(self,), name="PiLights")
        #self.process.start()
        # TODO: Join log 

def printStatus(pi_lights):
    s = "NULL"
    if (pi_lights.getMainLoopStatus() is MainLoopStatus.START):
        s = "`START"
    elif (pi_lights.getMainLoopStatus() is MainLoopStatus.STARTED):
        s = "STARTED"
    elif (pi_lights.getMainLoopStatus() is MainLoopStatus.STOP):
        s = "STOP"
    elif (pi_lights.getMainLoopStatus() is MainLoopStatus.STOPPED):
        s = "STOPPED"
    elif (pi_lights.getMainLoopStatus() is MainLoopStatus.KILL):
        s = "KILL"
    print("Status: " + s)
        
def getDiff(numA, numB):
    if (numA <= numB):
        return numB - numA
    else:
        return numA - numB
# fadeTime = The total time to move from one color to the next
# loopTime = The total time to move through the entire pattern list
# brightLevel = The total brightness to use
# pattern = The array of patterns to transition between
def mainLoop(pi_lights):
    import setproctitle

    setproctitle.setproctitle("LightController")
    pi_lights.setMainLoopStatus(MainLoopStatus.STARTED)
    # Only exit if killing the thread
    while (pi_lights.getMainLoopStatus() is not MainLoopStatus.KILL):
        # We should be here every LOOP time
        # If STOP, program not dead, just lights are turned off
        if (pi_lights.getMainLoopStatus() is MainLoopStatus.STOP):
            sleep(0.5)
            continue
        printStatus(pi_lights)
        pi_lights.setConfigChanged(False)

        for x in range (0, pi_lights.getNumColors()):
            print ("Number of sexy colors: " + str(pi_lights.getNumColors()))
            # Only STARTED, do work. Otherwise leave immediately
            if (pi_lights.getMainLoopStatus() is not MainLoopStatus.STARTED):
                break
            currentR = pi_lights.getColorPattern()[x][RGB.SPECTRUM.R]
            currentG = pi_lights.getColorPattern()[x][RGB.SPECTRUM.G]
            currentB = pi_lights.getColorPattern()[x][RGB.SPECTRUM.B]
            pi_lights.setLights(pi_config.RGB.getPinR(), currentR, pi_lights.getBrightLevel())           
            pi_lights.setLights(pi_config.RGB.getPinG(), currentG, pi_lights.getBrightLevel())
            pi_lights.setLights(pi_config.RGB.getPinB(), currentB, pi_lights.getBrightLevel())            
            if (x == pi_lights.getNumColors()-1):
                futureR = pi_lights.getColorPattern()[0][RGB.SPECTRUM.R]
                futureG = pi_lights.getColorPattern()[0][RGB.SPECTRUM.G]
                futureB = pi_lights.getColorPattern()[0][RGB.SPECTRUM.B]
            else:
                futureR = pi_lights.getColorPattern()[x+1][RGB.SPECTRUM.R]
                futureG = pi_lights.getColorPattern()[x+1][RGB.SPECTRUM.G]
                futureB = pi_lights.getColorPattern()[x+1][RGB.SPECTRUM.B]
               
            tSteps = 50
            hopsR = (futureR - currentR) / tSteps
            hopsG = (futureG - currentG) / tSteps
            hopsB = (futureB - currentB) / tSteps

            rDone = gDone = bDone = False

            # This is the "Fade"
            while not pi_lights.getConfigChanged():
                # If STARTED, do work. Otherwise leave immediately
                if (pi_lights.getMainLoopStatus() is not MainLoopStatus.STARTED):
                    printStatus(pi_lights)
                    break

                # current (positive direction) future                  
                if (((pi_lights.getColorPattern()[x][RGB.SPECTRUM.R] <= futureR) and (currentR >= futureR)) or 
                    ((pi_lights.getColorPattern()[x][RGB.SPECTRUM.R] >= futureR) and (currentR <= futureR))):
                        rDone = True
                    
                if (((pi_lights.getColorPattern()[x][RGB.SPECTRUM.G] <= futureG) and (currentG >= futureG)) or 
                    ((pi_lights.getColorPattern()[x][RGB.SPECTRUM.G] >= futureG) and (currentG <= futureG))):
                        gDone = True
                    
                if (((pi_lights.getColorPattern()[x][RGB.SPECTRUM.B] <= futureB) and (currentB >= futureB)) or 
                    ((pi_lights.getColorPattern()[x][RGB.SPECTRUM.B] >= futureB) and (currentB <= futureB))):
                        bDone = True

                if (rDone and bDone and gDone):
                    # Show this color for this long (Hold time)
                    # XXX: change to getHoldTime() and such
                    sleep(pi_lights.getLoopTime())
                    break
                # vector / fadeTime = NumberOfHops
                if (not rDone):
                    currentR = pi_lights.updateColor(currentR, hopsR) # / pi_lights.getFadeTime()) #((futureR - pi_lights.getColorPattern()[x][0]) / pi_lights.getFadeTime()))
                if (not gDone):
                    currentG = pi_lights.updateColor(currentG, hopsG) # / pi_lights.getFadeTime()) #((futureG - pi_lights.getColorPattern()[x][1]) / pi_lights.getFadeTime()))
                if (not bDone):
                    currentB = pi_lights.updateColor(currentB, hopsB)

                pi_lights.setLights(pi_config.RGB.getPinR(), currentR, pi_lights.getBrightLevel())           
                pi_lights.setLights(pi_config.RGB.getPinG(), currentG, pi_lights.getBrightLevel())
                pi_lights.setLights(pi_config.RGB.getPinB(), currentB, pi_lights.getBrightLevel()) 

                #intervalUnitOfTime = 1/255
                sleep(pi_lights.getFadeTime() / tSteps)
            print("Bitches")
    pi_lights.stopProgram()
    pi_lights.setMainLoopStatus(MainLoopStatus.STOPPED)

if __name__ == '__main__':
    import multiprocessing as mp


    class MyPiLightsManager(BaseManager): pass

    if True:

        print("Go")
        #mp.set_start_method('spawn')
        MyPiLightsManager.register('PiLights', PiLights)
        manager = MyPiLightsManager()

        # child processes should ignore /ALL/ signals
        default_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        # Start everything up

        manager.start()
        piClass = manager.PiLights()
        process = mp.Process(target=mainLoop, args=(piClass,), name="PiLights")
        process.start()
        signal.signal(signal.SIGINT, default_handler)
        sleep(5)
        
        numColors = 3
        fadeTime = 2
        loopTime = 5
        brightLevel = 128 
        A=85
        B=170
        C=255
        colors = [ [A,B,C], [B,C,A], [C,A,B]]
        #colors = [ [0, 255,0]]
        
        pattern = Pattern(numColors, fadeTime, loopTime, brightLevel, colors)
        piClass.setPattern(pattern)
        try:
            while(True):
                sleep(.01)
        except KeyboardInterrupt:
            piClass.killProgram()
            process.join()
