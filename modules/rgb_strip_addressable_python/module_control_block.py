#!/usr/bin/python3

import threading
from Modules.RGB.light_model import Pattern
import time
from Modules.RGB.light_controller import *
import struct
#import logging as log

import multiprocessing as mp
from multiprocessing.managers import BaseManager

# 32uint, control char - 0 is command to gracefully shutdown
# 32uint, numColors - number of colors
# 32uint, fadeTime - fade time
# 32uint, loopTime - total loop time
# 32uint, brightLevel - intensity/brightness


class MyPiLightsManager(BaseManager): pass


class moduleControlBlock:

    #takes in a string representing the parameters for a pattern, and creates and returns a pattern object with those parameters
    def parseParameters(self, msgIn):
#        log.rgb_log(log.LEVEL.VERBOSE, "Light Module parsing message into parameters")
        control = struct.unpack_from('I', msgIn, offset=0)
        print('control was: ', control[0])
        if(int(control[0]) == 1):
#            log.rgb_log(log.LEVEL.DEBUG, "Light Module received graceful shutdown command")

            self.shutDown = True
            return 1

        numColors = struct.unpack_from('I', msgIn, offset=4)[0]
        fadeTime = struct.unpack_from('I', msgIn, offset=8)[0]
        loopTime = struct.unpack_from('I', msgIn, offset=12)[0]
        brightLevel = struct.unpack_from('I', msgIn, offset=16)[0]

        print('fade, loop, bright, numcolors: ', fadeTime, loopTime, brightLevel, numColors)
        patternParameters = []
#        log.rgb_log(log.LEVEL.VERBOSE, "params are "+ str(control) + " " + str(numColors) + " " + str(fadeTime) + " " + str(loopTime) + " " + str(brightLevel))
        colors = [999,999,999]
        colors = self.parseColors(msgIn, numColors)

        return Pattern(numColors, fadeTime, loopTime, brightLevel, colors)

    #takes in a string (RRRGGGBBB) and parses the colors into an array of ints
    def parseColors(self, msgIn, numColors):
#        log.rgb_log(log.LEVEL.VERBOSE, "Light Module parsing colors into pattern")
        toReturn = []
        msgOffset = 20
        for x in range (0, numColors):
            rInt = struct.unpack_from('I', msgIn, msgOffset)[0]
            msgOffset += 4
            gInt = struct.unpack_from('I', msgIn, msgOffset)[0]
            msgOffset += 4
            bInt = struct.unpack_from('I', msgIn, msgOffset)[0]
            msgOffset += 4
            toReturn.append([rInt, gInt, bInt])
            print ('colors to add is: ', toReturn)
        return toReturn

    
    def runController(self):

        from Modules.RGB.light_controller import PiLights

        print("runController")
        #mp.set_start_method('spawn')
        MyPiLightsManager.register('PiLights', PiLights)
        self.manager = MyPiLightsManager()

        # child processes should ignore /ALL/ signals
        #default_handler = signal.getsignal(signal.SIGINT)
        #signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        print("RGb MCB about to start lights ********************************")
        # Start everything up
        self.manager.start()
        self.piClass = self.manager.PiLights()
        self.process = mp.Process(target=mainLoop, args=(self.piClass,), name="PiLights")
        self.process.start()

#        log.rgb_log(log.LEVEL.VERBOSE, "pilights established")

    def __init__(self, mailBoxIn):
        self.shutDown = 0;
#        log.rgb_log(log.LEVEL.DEBUG, "Light Module initializing, starting controller and listening for messages")

        del mailBoxIn[:]

        self.shutDown = False
        self.runController()        

        while(not self.shutDown):
            time.sleep(3)
            if(len(mailBoxIn)>0):
                print("GOT A MESSAGE")
#                log.rgb_log(log.LEVEL.VERBOSE, "Light module has found a new message in its mailbox")
                toParse = mailBoxIn.pop()
                response = self.parseParameters(toParse)

                if (response == 1):
                    #log.rgb_log(log.LEVEL.DEBUG, "Light Module ShutDown flag is true, control block sending shutdown command to pilights")
                    self.piClass.killProgram()
                    self.process.join()
                    self.shutDown = True
                    return

                else:
#                    print ('skipping setting pattern because it is commented out')
                    self.piClass.setPattern(response)
            else:
                print("rgb mcb awaiting message")



if __name__ == "__main__":
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

    numColors = 3
    fadeTime = 3 
    loopTime = 1 
    brightLevel = 128 
    A=85
    B=170
    C=255
    colors = [ [A,B,C], [B,C,A], [C,A,B]]
    pattern = Pattern(numColors, fadeTime, loopTime, brightLevel, colors)

    print("Setting Pattern")

    while True:
        time.sleep(2)
        print ("module control block looping")
