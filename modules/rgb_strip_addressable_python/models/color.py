#!/usr/bin/python3fddf

# Macro Defines
MIN_VALUE = 0
MAX_VALUE = 255

# Custom Exceptions
class ColorExceptionBelowMinimum(Exception):
    def __init__(self, value, minimum):
        ex = ("Value " + str(value) + " is below minimum value of " + str(minimum))
        Exception.__init__(self, ex)

class ColorExceptionAboveMaximum(Exception):
    def __init__(self, value, maximum):
        ex = ("Value " + str(value) + " is above maximum value of " + str(maximum))
        Exception.__init__(self, ex)

class ColorExceptionNotInteger(Exception):
    def __init__(self, value):
        ex = ("Value " + str(value) + " is not an integer")
        Exception.__init__(self, ex)

# Private Methods
def validateValue(value):
    if (type(value) != int):
        raise ColorExceptionNotInteger(value)
    if (value < MIN_VALUE):
        raise ColorExceptionBelowMinimum(value, MIN_VALUE)
    if (value > MAX_VALUE):
        raise ColorExceptionAboveMaximum(value, MAX_VALUE)
    return value

# A Color contains a single R value, G value, and B value
class Color:
    
    def __init__(self, colorR=0, colorG=0, colorB=0):
        self.r = validateValue(colorR)
        self.g = validateValue(colorG)
        self.b = validateValue(colorB)

    def __str__(self):
        return "(" + self.r + "," + self.g + "," + self.b +")"

    def getR(self):
        return self.r
    def getG(self):
        return self.g
    def getB(self):
        return self.b

    def setR(self, value):
        self.r = validateValue(value)
    def setG(self, value):
        self.g = validateValue(value)
    def setB(self, value):
        self.b = validateValue(value)
