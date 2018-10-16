#!/usr/bin/python
import threading
import time
import RPi.GPIO as GPIO
import pygame
from pygame import mixer

GPIO.setmode(GPIO.BCM)
lock = threading.Lock()
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
    
    def play(self):
        self.channel.play(self.audio)
        while self.channel.get_busy():
            pygame.time.wait(100)  #  wait in ms
        self.channel.stop()

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
            pulse_start = time.time()              #Saves the last known time of LOW pulse

        while GPIO.input(self.gpioEcho)==1:               #Check whether the ECHO is HIGH
            pulse_end = time.time()                #Saves the last known time of HIGH pulse 

        pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

        distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
        distance = round(distance, 2) - 0.5           #Round to two decimal points
        return distance

    def run(self):
        global lastPlayed
        lastPlayed = ""
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
                lock.acquire()
                if lastPlayed != self.name:
                    print("Play: "+self.name)
                    self.play()
                    lastPlayed = self.name
                lock.release()
        print (self.name+":Stopped")

if __name__ == '__main__':
    
    myInstances = []
    myClasses = {
        "myObj01": [aStopEvent,"c1",23,24],
        #"myObj02": [aStopEvent,"d",25,26],
        #"myObj03": [aStopEvent,"e",23,24],
        #"myObj04": [aStopEvent,"f",23,24],
        #"myObj05": [aStopEvent,"g",23,24],
        #"myObj06": [aStopEvent,"a",23,24],
        #"myObj07": [aStopEvent,"b",23,24],
        #"myObj08": [aStopEvent,"c",23,24],
        }
    
    myInstances = [UltraSound(myClasses[thisClass][0],myClasses[thisClass][1],myClasses[thisClass][2],myClasses[thisClass][3]) for thisClass in myClasses.keys()]
    
    for thisObj in myInstances:
        thisObj.start()

    #letters = ["c1", "d", "e", "f", "g", "a", "b", "c"]
    #self.piano_notes = ["samples/"+letter+".wav" for letter in letters]
    #ultraSound1 = UltraSound(aStopEvent,"a",23,24)
    #ultraSound1 = UltraSound("b",23,24)
    #ultraSound1 = UltraSound("c",23,24)
    #ultraSound1 = UltraSound("d",23,24)
    #ultraSound1 = UltraSound("e",23,24)
    #ultraSound1 = UltraSound("f",23,24)
    #ultraSound1 = UltraSound("g",23,24)
    
    #ultraSound1.start()

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
 
