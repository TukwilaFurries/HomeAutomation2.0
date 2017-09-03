#!/usr/bin/python3

import unittest
from cli import *


class testCli(unittest.TestCase):
    def testSocketSocket(self):
        argv = "-s 1.1.1.1:1"
        cla = CommandLineArguments(argv.split())

        self.assertEqual(cla.ip, "1.1.1.1")
        self.assertEqual(cla.port, 1)

    def testSocketBadIp(self):
        argv = "-s 1.1.1.1.1:1"
        with self.assertRaises(CLIExceptionInvalidSocket):
            cla = CommandLineArguments(argv.split())

    def testSocketBadPort(self):
        argv = "-s 1.1.1.1:NOPE"
        with self.assertRaises(CLIExceptionInvalidSocket):
            cla = CommandLineArguments(argv.split())
    
    def testBasicInput(self):
        argv = "-c ABCABC -f 25 -l 30 -b 35"
        cla = CommandLineArguments(argv.split())

        self.assertEqual(cla.fadeTime, 25)
        self.assertEqual(cla.loopTime, 30)
        self.assertEqual(cla.brightLevel, 35)
        self.assertEqual(cla.colors, "ABCABC")

    def testDuplicateModesSocket(self):
        argv = "-f 1 -l 1 -b 1 -c ABC -s 1.1.1.1:1"
        with self.assertRaises(CLIExceptionDuplicateModes):
            cla = CommandLineArguments(argv.split())

    def testDuplicateModesFade(self):
        argv = "-s 1.1.1.1:1 -f 1"
        with self.assertRaises(CLIExceptionDuplicateModes):
            cla = CommandLineArguments(argv.split())

    def testDuplicateModesLoop(self):
        argv = "-s 1.1.1.1:1 -l 1"
        with self.assertRaises(CLIExceptionDuplicateModes):
            cla = CommandLineArguments(argv.split())
   
    def testDuplicateModesBrightness(self):
        argv = "-s 1.1.1.1:1 -b 1"
        with self.assertRaises(CLIExceptionDuplicateModes):
            cla = CommandLineArguments(argv.split())
  
    def testDuplicateModesColors(self):
        argv = "-s 1.1.1.1:1 -c ABC"
        with self.assertRaises(CLIExceptionDuplicateModes):
            cla = CommandLineArguments(argv.split())


if __name__ == '__main__':
    unittest.main()
