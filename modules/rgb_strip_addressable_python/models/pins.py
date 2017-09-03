#!/usr/bin/python3

class Pins:
    def __init__(self, rPin, gPin, bPin):
        self.rPin = rPin
        self.gPin = gPin
        self.bPin = bPin

    def getR(self):
        return self.rPin
    def getG(self):
        return self.gPin
    def getB(self):
        return self.bPin
