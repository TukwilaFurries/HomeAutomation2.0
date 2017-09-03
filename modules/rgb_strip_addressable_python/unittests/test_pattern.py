#!/usr/bin/python3

import unittest
from models.pattern import Pattern
from models.pattern import PatternExceptionNotArray
from models.pattern import PatternExceptionInvalidEntry
from models.pattern import PatternExceptionFadeTimeNotInteger
from models.pattern import PatternExceptionFadeTimeBelowMinimum
from models.pattern import PatternExceptionLoopTimeNotInteger
from models.pattern import PatternExceptionLoopTimeBelowMinimum
from models.pattern import PatternExceptionBrightLevelNotInteger
from models.pattern import PatternExceptionBrightLevelBelowMinimum
from models.pattern import PatternExceptionBrightLevelAboveMaximum
from models.color import Color

class TestModelPattern(unittest.TestCase):
    def testDefaults(self):
        pattern = Pattern()
        self.assertEqual(pattern.getColors(), None)
        self.assertEqual(pattern.getNumColors(), 0)
        self.assertEqual(pattern.getLoopTime(), 0)
        self.assertEqual(pattern.getFadeTime(), 0)
        self.assertEqual(pattern.getBrightLevel(), 0)

    def testBasic(self):
        colors = [ Color(0,0,0),Color(255,255,255) ]
        loopTime = 100
        fadeTime = 100
        brightLevel = 100
        pattern = Pattern(colors, loopTime, fadeTime, brightLevel)
        self.assertEqual(pattern.getColors(), colors)
        self.assertEqual(pattern.getNumColors(), 2)
        self.assertEqual(pattern.getLoopTime(), loopTime)
        self.assertEqual(pattern.getFadeTime(), fadeTime)
        self.assertEqual(pattern.getBrightLevel(), brightLevel)

    def testColorsNotArray(self):
        with self.assertRaises(PatternExceptionNotArray):
            colors = Color(0,0,0)
            pattern = Pattern(colors,0,0,0)

    def testColorsInvalidElement(self):
        with self.assertRaises(PatternExceptionInvalidEntry):
            colors = [ Color(0,0,0),"ABC",Color(255,255,255) ]
            pattern = Pattern(colors,0,0,0)

    def testFadeTimeNotInteger(self):
        with self.assertRaises(PatternExceptionFadeTimeNotInteger):
            colors = [Color(0,0,0)]
            pattern = Pattern([Color(0,0,0)],"?",0,0)

    def testFadeTimeBelowMinimum(self):
        with self.assertRaises(PatternExceptionFadeTimeBelowMinimum):
            pattern = Pattern([Color(0,0,0)],-1,0,0)

    def testLoopTimeNotInteger(self):
        with self.assertRaises(PatternExceptionLoopTimeNotInteger):
            pattern = Pattern([Color(0,0,0)],0,"?",0)

    def testLoopTimeBelowMinimum(self):
        with self.assertRaises(PatternExceptionLoopTimeBelowMinimum):
            pattern = Pattern([Color(0,0,0)],0,-1,0)

    def testBrightLevelNotInteger(self):
        with self.assertRaises(PatternExceptionBrightLevelNotInteger):
            pattern = Pattern([Color(0,0,0)],0,0,"?")

    def testBrightLevelBelowMinimum(self):
        with self.assertRaises(PatternExceptionBrightLevelBelowMinimum):
            pattern = Pattern([Color(0,0,0)],0,0,-1)

    def testBrightLevelAboveMaximum(self):
        with self.assertRaises(PatternExceptionBrightLevelAboveMaximum):
            pattern = Pattern([Color(0,0,0)],0,0,256)

if __name__ == '__main__':
    unittest.main()
