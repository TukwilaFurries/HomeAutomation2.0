#!/usr/bin/python3

import unittest
from models.color import Color
from models.color import ColorExceptionNotInteger, ColorExceptionAboveMaximum, ColorExceptionBelowMinimum

class TestModelColor(unittest.TestCase):
    def testNoColor(self):
        color = Color(0,0,0)
        self.assertEqual(color.getR(), 0)
        self.assertEqual(color.getG(), 0)
        self.assertEqual(color.getB(), 0)

    def testMaxColor(self):
        color = Color(255,255,255)
        self.assertEqual(color.getR(), 255)
        self.assertEqual(color.getG(), 255)
        self.assertEqual(color.getB(), 255)

    def testRedInvalid(self):
        with self.assertRaises(ColorExceptionNotInteger):
            color = Color("?", 255, 255)
    def testGreenInvalid(self):
        with self.assertRaises(ColorExceptionNotInteger):
            color = Color(255, "?", 255)
    def testBlueInvalid(self):
        with self.assertRaises(ColorExceptionNotInteger):
            color = Color(255,255,"?")

    def testRedAboveMaximum(self):
        with self.assertRaises(ColorExceptionAboveMaximum):
            color = Color(256,255,255)
    def testGreenAboveMaximum(self):
        with self.assertRaises(ColorExceptionAboveMaximum):
            color = Color(255,256,255)
    def testBlueAboveMaximum(self):
        with self.assertRaises(ColorExceptionAboveMaximum):
            color = Color(255,255,256)

    def testRedBelowMinimum(self):
        with self.assertRaises(ColorExceptionBelowMinimum):
            color = Color(-1,0,0)
    def testGreenBelowMinimum(self):
        with self.assertRaises(ColorExceptionBelowMinimum):
            color = Color(0,-1,0)
    def testBlueBelowMinimum(self):
        with self.assertRaises(ColorExceptionBelowMinimum):
            color = Color(0,0,-1)


if __name__ == '__main__':
    unittest.main()
