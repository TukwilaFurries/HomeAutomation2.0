#!/usr/bin/python
import random, time
import RPi.GPIO as GPIO
import pigpio
import math
import thread
import pi_config
import threading
def setup(pi,freq):
    global R_PIN
    R_PIN = pi_config.RGB.getPinR()
    global G_PIN
    G_PIN = pi_config.RGB.getPinG()
    global B_PIN
    B_PIN = pi_config.RGB.getPinB()

    pi.set_mode(R_PIN, pigpio.OUTPUT)
    pi.set_mode(G_PIN, pigpio.OUTPUT)
    pi.set_mode(B_PIN, pigpio.OUTPUT)

    pi.set_PWM_frequency(R_PIN, freq)
    pi.set_PWM_frequency(G_PIN, freq)
    pi.set_PWM_frequency(B_PIN, freq)

    global frequency
    frequency = freq
    global redprev
    redprev = 0
    global greenprev
    greenprev = 0
    global blueprev
    blueprev = 0

def changeto(redv,greenv,bluev,speed):
    print("changeto() {")
    global redprev
    global greenprev
    global blueprev
    r = int(round(redv/2.55))
    g = int(round(greenv/2.55))
    b = int(round(bluev/2.55))
    r_thread = threading.Thread(target=changered, args=(r, speed))
    g_thread = threading.Thread(target=changegreen, args=(g, speed))
    b_thread = threading.Thread(target=changeblue, args=(b, speed))
    r_thread.start()
    g_thread.start()
    b_thread.start()
    r_thread.join()
    g_thread.join()
    b_thread.join()
    #thread.start_new_thread(changered,(r,speed))
    #thread.start_new_thread(changegreen,(g,speed))
    #thread.start_new_thread(changeblue,(b,speed))
    #time.sleep(speed + 2)
    print("} changeto()")

def changered(red,speed):
    print ("changered() {")
    global redprev
    if(red > redprev):
        for x in range (redprev,red):
            pi.set_PWM_dutycycle(R_PIN, x)
            time.sleep(speed)
    else:
        down = redprev - red
        for x in range (0,down):
            pi.set_PWM_dutycycle(R_PIN, redprev-x)
            time.sleep(speed)
    redprev = red
    print("} changered()")

def changegreen(green,speed):
    print ("changegreen() {")
    global greenprev
    if(green > greenprev):
        for x in range (greenprev,green):
            pi.set_PWM_dutycycle(G_PIN, x)
            time.sleep(speed)
    else:
        down = greenprev - green
        for x in range (0,down):
            pi.set_PWM_dutycycle(G_PIN, greenprev-x)
            time.sleep(speed)
    greenprev = green
    print ("} changegreen()")

def changeblue(blue,speed):
    print ("changeblue() {")
    global blueprev
    if(blue > blueprev):
        for x in range (blueprev,blue):
            pi.set_PWM_dutycycle(B_PIN, x)
            time.sleep(speed)
    else:
        down = blueprev - blue
        for x in range (0,down):
            pi.set_PWM_dutycycle(B_PIN, blueprev-x)
            time.sleep(speed)
    blueprev = blue
    print ("} changeblue()")
def on(r,g,b):
    pass    
def off(speed):
    for x in range (0,blueprev):
        pi.set_PWM_dutycycle(B_PIN, blueprev-x)
        time.sleep(speed)
    for x in range (0,greenprev):
        pi.set_PWM_dutycycle(G_PIN, greenprev-x)
        time.sleep(speed)
    for x in range (0,redprev):
        pi.set_PWM_dutycycle(R_PIN, redprev-x)
        time.sleep(speed)

if __name__ == "__main__":  
    pi = pigpio.pi()
    setup(pi,100)
    while True:
        print("Red")
        changeto(255,0,0,.1)
        time.sleep(5)
        print("Green")
        changeto(0,255,0,.1)
        time.sleep(5)
        print("Blue")
        changeto(0,0,255,.1)
        time.sleep(5)
    off(.2)
    time.sleep(2)
