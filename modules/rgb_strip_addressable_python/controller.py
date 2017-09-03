#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, getopt
import pigpio
import signal 
from decimal import *
from multiprocessing.managers import BaseManager
from time import sleep
import socket 
from socket import error as socket_error
import errno
import struct
import time
import configparser

import _thread
from models.pins import *
from models.pattern import *
from models.color import *

import multiprocessing as mp
class MyPiLightsManager(BaseManager): pass

#class MyLoggingManager(BaseManager): pass

class MainLoopStatus:
    START   = 0 # Loop Start Requested
    STARTED = 1 # Loop Has Started
    KILL    = 2 # Please kill the loop / thread
    STOP    = 3 # Loop Stop Requested but thread remains active
    STOPPED = 4 # Loop Has Stopped, thread is exiting

class PiLights:

    def setFadeTime(self, ft):
        #self.getLog().info("Fade Time Changed to " + str(ft))
        self.fadeTime = ft
        self.configChagned = True
    def getFadeTime(self):
        return self.fadeTime

    def setLoopTime(self, lt):
        #self.getLog().info("Loop Time Changed to " + str(lt))
        self.loopTime = lt
        self.configChanged = True
    def getLoopTime(self):
        return self.loopTime

    def setBrightLevel(self, bl):
        #self.getLog().info("Brightness Chanes to " + str(bl))
        self.brightLevel = bl
        self.configChanged = True
    def getBrightLevel(self):
        return self.brightLevel

    def setColorPattern(self, cp):
        #self.getLog().debug("setColorPattern() {")
        self.colorPattern = cp
        self.numColors = len(cp)
        self.configChanged = True
        #self.getLog().debug("} setColorPattern()")

    def getColorPattern(self):
        return self.colorPattern
    
    def getNumColors(self):
        return self.numColors

    def setNumColors(self, num):
        #self.getLog().info("Number of Colors Changed to: " + str(num))
        self.numColors = num
    
    def setConfigChanged(self, changed):
        self.configChanged = changed
    def getConfigChanged(self):
        return self.configChanged

    def setPattern(self, p):
        #self.getLog().info("New Pattern Recieved:" + str(p))
        self.setFadeTime(p.getFadeTime())
        self.setLoopTime(p.getLoopTime())
        self.setBrightLevel(p.getBrightLevel())
        self.setColorPattern(p.getColors())
        self.setNumColors(p.getNumColors())
        self.setConfigChanged(True)
        #if self.logging_enabled: self.getLog().debug("} setPattern()")

    
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

    #def getLog(self):
    #    return self.log
    

    def getPins(self):
        return self.pins
    def getMainLoopStatus(self):
        return self.mainLoopStatus
    def setMainLoopStatus(self, mainLoopStatus):
        self.mainLoopStatus = mainLoopStatus

    def killProgram(self):
        #self.getLog().info("Kill Program Recieved")
        self.mainLoopStatus = MainLoopStatus.KILL
        self.configChanged = True
        
        # Wait for main loop to exit on its own
        while self.mainLoopStatus is not MainLoopStatus.STOPPED:
            sleep(0.1)
            pass
        else:
            self.pi.stop()

    def stopProgram(self):
        self.setLights(self.pins.getR(), 0, 0)
        self.setLights(self.pins.getG(), 0, 0)
        self.setLights(self.pins.getB(), 0, 0)



    def __init__(self):
        #    self.logging_enabled = True
        #print("I SHOULD BE FIRST")
        self.mainLoopStatus = MainLoopStatus.START

        self.fadeTime = 1
        self.loopTime = 1
        self.brightLevel = 1
        self.colorPattern = [] 
        self.numColors = 0
        self.pi = pigpio.pi()
        self.configChanged = False

        config = configparser.RawConfigParser()
        config.read('../../config.ini')
        rPin = config.getint('RGBLightControllerStatic', 'PinR')
        gPin = config.getint('RGBLightControllerStatic', 'PinG')
        bPin = config.getint('RGBLightControllerStatic', 'PinB')
        self.pins = Pins(rPin, gPin, bPin)
        print("Red Pin: " + str(self.pins.getR()))
        print("Green Pin: " + str(self.pins.getG()))
        print("Blue Pin: " + str(self.pins.getB()))


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
    #print("Status: " + s)
        
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

    rPin = pi_lights.getPins().getR()
    gPin = pi_lights.getPins().getG()
    bPin = pi_lights.getPins().getB()

    setproctitle.setproctitle("LightController")
    pi_lights.setMainLoopStatus(MainLoopStatus.STARTED)
    # Only exit if killing the thread
    while (pi_lights.getMainLoopStatus() is not MainLoopStatus.KILL):
        # We should be here every LOOP time
        # If STOP, program not dead, just lights are turned off
        if (pi_lights.getMainLoopStatus() is MainLoopStatus.STOP):
            sleep(0.5)
            continue

        #printStatus(pi_lights)
        pi_lights.setConfigChanged(False)

        for x in range (0, pi_lights.getNumColors()):
            print ("Number of sexy colors: " + str(pi_lights.getNumColors()))
            # Only STARTED, do work. Otherwise leave immediately
            if (pi_lights.getMainLoopStatus() is not MainLoopStatus.STARTED):
                break
            currentR = pi_lights.getColorPattern()[x].getR()
            currentG = pi_lights.getColorPattern()[x].getG()
            currentB = pi_lights.getColorPattern()[x].getB()
            pi_lights.setLights(rPin, currentR, pi_lights.getBrightLevel())           
            pi_lights.setLights(gPin, currentG, pi_lights.getBrightLevel())
            pi_lights.setLights(bPin, currentB, pi_lights.getBrightLevel())            
            if (x == pi_lights.getNumColors()-1):
                futureR = pi_lights.getColorPattern()[0].getR()
                futureG = pi_lights.getColorPattern()[0].getG()
                futureB = pi_lights.getColorPattern()[0].getB()
            else:
                futureR = pi_lights.getColorPattern()[x+1].getR()
                futureG = pi_lights.getColorPattern()[x+1].getG()
                futureB = pi_lights.getColorPattern()[x+1].getB()
               
            tSteps = 50
            hopsR = (futureR - currentR) / tSteps
            hopsG = (futureG - currentG) / tSteps
            hopsB = (futureB - currentB) / tSteps

            rDone = gDone = bDone = False

            # This is the "Fade"
            while not pi_lights.getConfigChanged():
                # If STARTED, do work. Otherwise leave immediately
                if (pi_lights.getMainLoopStatus() is not MainLoopStatus.STARTED):
                    #printStatus(pi_lights)
                    break

                # current (positive direction) future                  
                if (((pi_lights.getColorPattern()[x].getR() <= futureR) and (currentR >= futureR)) or 
                    ((pi_lights.getColorPattern()[x].getR() >= futureR) and (currentR <= futureR))):
                        rDone = True
                    
                if (((pi_lights.getColorPattern()[x].getG() <= futureG) and (currentG >= futureG)) or 
                    ((pi_lights.getColorPattern()[x].getG() >= futureG) and (currentG <= futureG))):
                        gDone = True
                    
                if (((pi_lights.getColorPattern()[x].getB() <= futureB) and (currentB >= futureB)) or 
                    ((pi_lights.getColorPattern()[x].getB() >= futureB) and (currentB <= futureB))):
                        bDone = True

                if (rDone and bDone and gDone):
                    # Show this color for this long (Hold time)
                    # XXX: change to getHoldTime() and such
                    sleep(pi_lights.getLoopTime())
                    break
                # vector / fadeTime = NumberOfHops
                if (not rDone):
                    currentR = pi_lights.updateColor(currentR, hopsR) 
                if (not gDone):
                    currentG = pi_lights.updateColor(currentG, hopsG) 
                if (not bDone):
                    currentB = pi_lights.updateColor(currentB, hopsB)

                pi_lights.setLights(rPin, currentR, pi_lights.getBrightLevel())           
                pi_lights.setLights(gPin, currentG, pi_lights.getBrightLevel())
                pi_lights.setLights(bPin, currentB, pi_lights.getBrightLevel()) 

                #intervalUnitOfTime = 1/255
                sleep(pi_lights.getFadeTime() / tSteps)
            print("Bitches")
    pi_lights.stopProgram()
    pi_lights.setMainLoopStatus(MainLoopStatus.STOPPED)

def listenerInit(ip, port):
    retries = 3
    inboundSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inboundSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while (retries > 0):
        try:
            inboundSocket.bind((ip, port))
            print ("Socket binded to " + ip + ":" + str(port))
            inboundSocket.listen(10)
            print ("Socket now listening")
            return inboundSocket
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # If a different error than "connection refused", raise error
                raise serr
            else:
                retries = retries-1
                print ("Network Communication: unable to connect to network controller")
                print ("waiting and trying again")
                time.sleep(3)
    raise Exception("Unable to connect")

#takes in a string (RRRGGGBBB) and parses the colors into an array of ints
def parseColors(msgIn, numColors):
    toReturn = []
    msgOffset = 0
    for x in range (0, numColors):
        rInt = struct.unpack_from('I', msgIn, msgOffset)[0]
        msgOffset += 4
        gInt = struct.unpack_from('I', msgIn, msgOffset)[0]
        msgOffset += 4
        bInt = struct.unpack_from('I', msgIn, msgOffset)[0]
        msgOffset += 4
        toReturn.append(Color(rInt, gInt, bInt))
        print(toReturn)
    return toReturn


def runAsDaemon(cla, piClass):
        print ("Running as a daemon")
        # Ising IP+Port, open socket to listen for Server on
        listener = listenerInit(cla.ip, cla.port)
        try:
            while (True):
                conn, addr = listener.accept()
                print ("Connected with " + addr[0] + ":" + str(addr[1]))
                # There is a specific amount of shit to read!
                # loopTime(32) + fadeTime(32) + brightLevel(32) + numColors(32) = 128 bits = 16 bytes
                # Recieve 8bit fadeTime
                # Recieve 8bit loopTime
                # Receive 8bit brightness
                # Receive 8bit numColors
                # Loop through numColors * 3 * 8bits
                data = conn.recv(16)

                fadeTime = struct.unpack_from('I', data, offset=0)[0]
                loopTime = struct.unpack_from('I', data, offset=4)[0]
                brightLevel = struct.unpack_from('I', data, offset=8)[0]
                numColors = struct.unpack_from('I', data, offset=12)[0]
                #print("fadeTime: " + str(fadeTime))
                #print("loopTime: " + str(loopTime))
                #print("brightness: " + str(brightLevel))
                #print("numColors: " + str(numColors))
                patternParameters = []
                colors = [999,999,999]
                data = conn.recv(numColors*3*4)
                if (len(data) != (numColors*3*4)):
                    print ("WTF This data doesn't make any sense")
                    continue
                colors = parseColors(data, numColors)
                pattern = Pattern(colors, fadeTime, loopTime, brightLevel)
                piClass.setPattern(pattern)
        except Exception as e:    
            print("Exception Caught")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            listener.close()
            piClass.killProgram()
            process.join()
            raise e;

def main(argv):

    # Get command line arguments to do what is needed intelligently
    import cli
    cla = cli.CommandLineArguments(argv)

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

    if (cla.mode == cla.MODE.DAEMON):
        runAsDaemon(cla, piClass)
    else:
        fadeTime = 2
        loopTime = 5
        brightLevel = 128 
        A=85
        B=170
        C=255
        colors = [Color(A,B,C), Color(B,C,A), Color(C,A,B)]
        pattern = Pattern(colors, fadeTime, loopTime, brightLevel)
        piClass.setPattern(pattern)
    
    
        try:
            while(True):
                sleep(.01)
        except KeyboardInterrupt:
            piClass.killProgram()
            process.join()


if __name__ == '__main__':
    main(sys.argv[1:])
# 
