#!/usr/bin/python
import threading
import time
import RPi.GPIO as GPIO
import pygame
from pygame import mixer

GPIO.setmode(GPIO.BCM)
aStopEvent = threading.Event()
path = "/home/pi/PianoStairs/media"

class UltraSound(threading.Thread):
    
    def __init__(self,event,name,trigger,echo):
        threading.Thread.__init__(self)
        self.name = name
        self.gpioTrigger = trigger
        self.gpioEcho = echo
        self.stopEvent = event
        #set up the mixer
        freq = 44100     # audio CD quality
        bitsize = -16    # unsigned 16 bit
        channels = 1     # 1 is mono, 2 is stereo
        buffer = 2048    # number of samples (experiment to get right sound)
        pygame.mixer.init(freq, bitsize, channels, buffer)
        pygame.mixer.init() #Initialize Mixer
        print("Load file: "+path+"/"+self.name+".wav")
        self.audio = pygame.mixer.Sound(path+"/"+self.name+".wav")
        self.channel = pygame.mixer.Channel(1)
        self.audio.set_volume(1.0)
        self.isPlaying = False
        self.enable = False

    def play(self):
        print("Play: "+self.name)
        self.isPlaying = True
        self.channel.play(self.audio)
        while self.channel.get_busy():
            pygame.time.wait(10)  #  wait in ms
        self.channel.stop()
        print ("Finish Play")
        self.isPlaying = False

    def measureDistance(self):
        GPIO.output(self.gpioTrigger, False)                 #Set TRIG as LOW
        #print ("Waitng For Sensor To Settle")
        time.sleep(0.1)                            #Delay of 2 seconds

        GPIO.output(self.gpioTrigger, True)                  #Set TRIG as HIGH
        time.sleep(0.00001)                      #Delay of 0.00001 seconds
        GPIO.output(self.gpioTrigger, False)                 #Set TRIG as LOW

        pulse_start = time.time()
        pulse_end = time.time()

        while GPIO.input(self.gpioEcho)==0:               #Check whether the ECHO is LOW
            pulse_start = time.time()                      #Saves the last known time of LOW pulse

        while GPIO.input(self.gpioEcho)==1:               #Check whether the ECHO is HIGH
            pulse_end = time.time()                #Saves the last known time of HIGH pulse 

        pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

        distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
        distance = round(distance, 2) - 0.5           #Round to two decimal points
        return distance

    def run(self):
        th=30
        pulse_start=time.time()
        pulse_end=time.time()
        GPIO.setup(self.gpioTrigger, GPIO.OUT)
        GPIO.setup(self.gpioEcho, GPIO.IN)
        time.sleep(2)
        print("UltraSound "+self.name+" ready on port "+str(self.gpioTrigger)+" "+str(self.gpioEcho))
        
        while True:
            if(self.stopEvent.wait(0)):
                print (self.name+":Asked to stop")
                break;
            distance = self.measureDistance()
            #print (self.name+" distance: "+str(distance)+" cm "+str(th))
            if (distance > 2 and distance < th):
                if (not self.enable):
                    print ("ENABLE distance: "+str(distance)+" cm "+str(th))
                    self.enable = True
                    if not self.isPlaying:
                        self.play()
            else:
                #print ("DISABLE distance: "+str(distance)+" cm "+str(th))
                self.enable = False
        print (self.name+":Stopped")

if __name__ == '__main__':
    #[[12,5],[23,24],[27,22],[4,17],[6,13],[26,16]]
    myInstances = []
    myClasses = {
        "myObj01": [aStopEvent,"c1",12,5],
        "myObj02": [aStopEvent,"d",23,24],
        "myObj03": [aStopEvent,"e",27,22],
        "myObj04": [aStopEvent,"f",4,17],
        "myObj05": [aStopEvent,"g",6,13],
        "myObj06": [aStopEvent,"a",26,16],
        }
    
    myInstances = [UltraSound(myClasses[thisClass][0],myClasses[thisClass][1],myClasses[thisClass][2],myClasses[thisClass][3]) for thisClass in myClasses.keys()]
    
    for thisObj in myInstances:
        thisObj.start()

    try:
        while True :
            time.sleep(0.1)
            # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        aStopEvent.set()
        for thisObj in myInstances:
            thisObj.join()
        GPIO.cleanup()
 
