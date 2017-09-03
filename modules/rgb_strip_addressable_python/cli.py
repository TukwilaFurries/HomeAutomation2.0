#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, getopt
import pigpio
import signal 
from decimal import *
from multiprocessing.managers import BaseManager
from time import sleep

import configparser

from models.pins import *
from models.pattern import *
from models.color import *
from ipaddress import ip_address

import multiprocessing as mp
class MyPiLightsManager(BaseManager): pass

#class MyLoggingManager(BaseManager): pass

class CLIException(Exception):
    def __init__(self, error):
        ex = "CLI Error: " + error
        Exception.__init__(self, ex)

class CLIExceptionInvalidSocket(Exception):
    def __init__(self, socketInput):
        ex = "CLI Error: " + socketInput + " is not a valid socket"
        Exception.__init__(self, ex)
 
class CLIExceptionDuplicateModes(Exception):
    def __init__(self):
        ex = "Cannot specify other arguments with -s / --socket"
        Exception.__init__(self, ex)

def ArgSocketToIpPort(arg):

    socket = arg.split(":")

    if len(socket) != 2:
        raise CLIExceptionInvalidSocket(arg)

    try:
        ip_address(socket[0])
        int(socket[1])
    except Exception:
        raise CLIExceptionInvalidSocket(arg)

    return socket[0], int(socket[1])


class CommandLineArguments:
    class MODE:
        UNSET        = 0
        DAEMON       = 1
        INTERACTIVE  = 2

    def __init__(self, argv):
        self.mode           = self.MODE.UNSET
        self.ip             = ''
        self.port           = -1
        self.colors         = ''
        self.fadeTime       = 0
        self.loopTime       = 0
        self.brightLevel    = 0
        self.parseArgs(argv)

    def display(self):
        print ("IP: " + str(self.ip))
        print ("Port: " + str(self.port))
        print ("Fade: " + str(self.fadeTime))
        print ("Loop: " + str(self.loopTime))
        print ("Brightness: " + str(self.brightLevel))
        print ("Colors: " + self.colors)
    
        if (self.mode is self.MODE.DAEMON):
            print("Running as a daemon")
        elif (self.mode is self.MODE.INTERACTIVE):
            print("Running interactive")
        else:
            print("WTF")

    def parseArgs(self, argv):
        helpText="controller.py -s <ip:port> | -f <fade time> -l <loop time> -b <bright level> -c [R,G,B,R,G,B...]"

        try:
            opts, args = getopt.getopt(argv, "hs:f:l:b:c:", ["socket=", "fade=", "loop=", "bright=", "colors="])
        except getopt.GetoptError:
            raise CLIException(helpText)
        
        for opt, arg in opts:
            if opt == '-h':
                raise CLIException(helpText)

            elif opt in ("-s", "--socket"):
                if (self.mode == self.MODE.UNSET):
                    self.ip, self.port = ArgSocketToIpPort(arg)
                    self.mode = self.MODE.DAEMON
                elif (self.mode == self.MODE.DAEMON):
                    raise CLIException("Cannot specify multiple sockets")
                elif (self.mode == self.MODE.INTERACTIVE):
                    raise CLIExceptionDuplicateModes

            elif opt in ("-f", "--fade"):
                if (self.mode == self.MODE.DAEMON):
                    raise CLIExceptionDuplicateModes
                self.fadeTime = int(arg)
                self.mode = self.MODE.INTERACTIVE
        
            elif opt in ("-l", "--loop"):
                if (self.mode == self.MODE.DAEMON):
                    raise CLIExceptionDuplicateModes
                self.loopTime = int(arg)
                self.mode = self.MODE.INTERACTIVE
        
            elif opt in ("-b", "--bright"):
                if (self.mode == self.MODE.DAEMON):
                    raise CLIExceptionDuplicateModes
                self.brightLevel = int(arg)
                self.mode = self.MODE.INTERACTIVE
        
            elif opt in ("-c", "--color"):
                if (self.mode == self.MODE.DAEMON):
                    raise CLIExceptionDuplicateModes
                self.colors = arg
                self.mode = self.MODE.INTERACTIVE
        
            else:
                raise CLIException("Unknown argument: " + arg)
