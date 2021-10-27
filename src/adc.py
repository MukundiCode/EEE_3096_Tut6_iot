import busio
import digitalio 
import board 
import adafruit_mcp3xxx.mcp3008 as MCP 
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_debouncer import Debouncer

import threading
import time
import datetime
import RPi.GPIO as GPIO
import math

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

#setup()
print("{:<15} {:<15} {:<15} {:>2} {:<15}".format('Runtime','Temp Reading','Temp',"",'Light Reading'))
start = time.time()


def print_time_thread():
    """
    This function prints the time to the screen every five seconds
    """
    thread = threading.Timer(sampling[i], print_time_thread)
    thread.daemon = True  # Daemon threads exit when the program does
    thread.start()
    read_adc()
    print("{:<15} {:<15} {:<15.1f} {:>2} {:<15}".format(str(math.floor((time.time()-start)))+"s", chan1.value,sensor_temp(chan1.voltage), "C", chan2.value))


if __name__ == "__main__":
    global i 
    i = 0
    try:
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