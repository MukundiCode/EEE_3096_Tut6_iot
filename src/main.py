from flask import Flask
import socket
import busio
import digitalio 
import board 
import adafruit_mcp3xxx.mcp3008 as MCP 
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_debouncer import Debouncer

import threading
import time
import datetime
#import mraa
import math
import RPi.GPIO as GPIO

#pins used
SCLK = 23
MISO = 21
MOSI = 19
CE0 = 24
sampling = [10, 5, 1] #different time intervals
#global i
#i = 0 #sampling index for different time intervals

#setting up button
BTN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def change_sample(x):
	if x == 2:
		x = 0
	else:
		x= x+1
	print("Sampling updated to",sampling[x],"seconds")
	return x

def read_adc():
	global spi, cs, mcp, chan2, chan1, chan3, button ,switch
	# create the spi bus
	spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
	
	button = digitalio.DigitalInOut(board.D23)
	button.direction = digitalio.Direction.INPUT
	button.pull = digitalio.Pull.UP
	switch = Debouncer(button,interval=0.1)
	# create the cs (chip select)
	cs = digitalio.DigitalInOut(board.D5)

	# create the mcp object
	mcp = MCP.MCP3008(spi, cs)

	# create an analog input channel on pin 0
	chan2 = AnalogIn(mcp, MCP.P2)

	# create analog input channel on pin 1
	chan1 = AnalogIn(mcp, MCP.P1)

def sensor_temp(adc_value):
	"""Temperature calculation"""

	voltage = (adc_value * 3.3)/1024
	temp = (adc_value-0.4)/0.01
	return temp

#setting up tcp connection
readData = True
TCP_IP = '172.20.10.12'
TCP_PORT = 5003
BUFFER_SIZE = 1024
M = "Hello, World!"
MESSAGE = str.encode(M)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
#data = s.recv(BUFFER_SIZE)
#s.close()


#setup()
print("{:<15} {:<15} {:<15} {:>2} {:<15}".format('Runtime','Temp Reading','Temp',"",'Light Reading'))
start = time.time()


def print_time_thread():
    global readData
    """
    This function prints the time to the screen every five seconds
    """
    #print(readData)
    thread = threading.Timer(sampling[i], print_time_thread)
    thread.daemon = True  # Daemon threads exit when the program does
    thread.start()
    #read_adc()

    if readData:
        #message = "{:<15} {:<15} {:<15.1f} {:>2} {:<15}".format(str(math.floor((time.time()-start)))+"s", chan1.value,sensor_temp(chan1.voltage), "C", chan2.value)
        message = ("{:<15} {:<15} {:<15.1f} {:>2} {:<15}".format(str(math.floor((time.time()-start)))+"s", 0,0, "C", 0))
        print("{:<15} {:<15} {:<15.1f} {:>2} {:<15}".format(str(math.floor((time.time()-start)))+"s", 0,0, "C", 0))
        MESSAGE = str.encode(message)
        s.send(MESSAGE)


def recieve():
    global readData,s
    while(True):
        fromServer = s.recv(1024).decode()
        if(fromServer == "sendon"):
            print(fromServer)
            readData = True
            sendAck = "sendonACK"
            s.send(str.encode(sendAck))

        elif(fromServer == "sendoff"):
            print(fromServer)
            readData = False
            sendAck = "sendoffACK"
            s.send(str.encode(sendAck))
        print("Sending data:",readData)



def sendData():
    global i 
    i = 0
    try:
        GPIO.setmode(GPIO.BCM)
        start = time.time()
        print_time_thread() # call it once to start the thread
        #setup()
        # Tell our program to run indefinitely
        while True:
            switch.update()
            #GPIO.add_event_detect(BTN, GPIO.FALLING, callback=my_callback, bouncetime=300)
            if  switch.rose:
                i = change_sample(i)
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()


app = Flask(__name__)

@app.route('/')
def hello_world():
    global i 
    i = 0
    try:
        GPIO.setmode(GPIO.BCM)
        start = time.time()
        print_time_thread() # call it once to start the thread
        #setup()
        # Tell our program to run indefinitely
        while True:
            switch.update()
            #GPIO.add_event_detect(BTN, GPIO.FALLING, callback=my_callback, bouncetime=300)
            if  switch.rose:
                i = change_sample(i)
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        
    return 'Hello Mukundi!'

if __name__ == '__main__':
    thread =  threading.Thread(target=recieve,args=())
    thread.start()
    sendData()
    app.run(host='0.0.0.0', port=80) 
