#!/usr/bin/python
import socket
import time
import struct

# RGB message structure
# 32uint, control char - 0 is command to gracefully shutdown
# 32uint, numColors - number of colors
# 32uint, fadeTime - fade time
# 32uint, loopTime - total loop time
# 32uint, brightLevel - intensity/brightness
# colors

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 20

print "Sending to " + TCP_IP + ":" + str(TCP_PORT)

A=85
B=170
C=255


fadeTime = 3
loopTime = 2
brightness = 255
numColors= 3

toSend = struct.pack('IIIIIIIIIIIII', fadeTime, loopTime, brightness, numColors, A, B, C, B, C, A, C, A, B)

print "fadeTime: " + str(fadeTime)
print "loopTime: " + str(loopTime)
print "brightness: " + str(brightness)
print "numColor: " + str(numColors)

print "(" + str(A) + "," + str(B) + "," + str(C) + ")"
print "(" + str(B) + "," + str(C) + "," + str(A) + ")"
print "(" + str(C) + "," + str(A) + "," + str(B) + ")"

lightControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lightControlSocket.connect((TCP_IP,TCP_PORT))
print lightControlSocket.send(toSend)
time.sleep(5)
lightControlSocket.close()
