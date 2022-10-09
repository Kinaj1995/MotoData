## ================================================= ##
##		MotoData
##		Authors: Pascal Rusca, Janik Schilter
##
## ================================================= ##


## ==================== Imports ==================== ##
## Add libaries to import here
##
## 		!! Make shure you created a "lib" folder on
##		the device and add the "sdcard.py" file to it !!
## ================================================= ##
import machine, uos
from machine import UART, I2C, Pin, SPI
import time

# - Multicore
import utime
import _thread

# - WLAN
import network, socket, sys, time, gc

# - IMU
from lsm6dsox import LSM6DSOX

# - SD Card
import sdcard

def web_page():
    html = """<html>

    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
         integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
        <style>
            html {
                font-family: Arial;
                display: inline-block;
                margin: 0px auto;
                text-align: center;
            }

            .button {
                background-color: #ce1b0e;
                border: none;
                color: white;
                padding: 16px 40px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
            }

            .button1 {
                background-color: #000000;
            }
        </style>
    </head>

    <body>
        <h2>ESP MicroPython Web Server</h2>
        <p>LED state: <strong>""" + SensorState + """</strong></p>
        <p>
            <i class="fas fa-lightbulb fa-3x" style="color:#c81919;"></i>
            <a href=\"?RECORD\"><button class="button">RECORD</button></a>
        </p>
        <p>
            <i class="far fa-lightbulb fa-3x" style="color:#000000;"></i>
            <a href=\"?RECORD_STOP\"><button class="button button1">RECORD STOP</button></a>
        </p>
        <p>
            <i class="far fa-lightbulb fa-3x" style="color:#000000;"></i>
            <a href=\"?CALIBRATE\"><button class="button button1">Calibrate</button></a>
        </p>
    </body>

    </html>"""
    return html


## =============== GLOBAL FUCTIONS ================= ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##
SensorState = "INIT" # States INIT, READY, RECORD, CALIBRATION 
Core0State = "INIT"

StateChange = False





## ================== GLOBAL VARS ================== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##

# - Semaphores
sLock = _thread.allocate_lock()

# - SerialPort for GPS
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# - IMU 
lsm = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))

# - Pindefinitions
led = Pin(6, Pin.OUT)




## ====================  INIT   ==================== ##
## Initialize all Sensors an Objects
##
## ================================================= ##

## ----- SD-Card ----- ##
CS = machine.Pin(5, machine.Pin.OUT)
spi = machine.SPI(0,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=Pin(6),mosi=machine.Pin(7),miso=machine.Pin(4))

sd = sdcard.SDCard(spi,CS)

vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# Create a file and write something to it
with open("/sd/data.txt", "w") as file:
    print("Writing to data.txt...")
    file.write("Welcome to microcontrollerslab!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/data.txt", "r") as file:
    print("Reading data.txt...")
    data = file.read()
    print(data)

time.sleep(5)

## ----- W-LAN AP ----- ##
SSID ='MotoData-Sensor'   # Network SSID
KEY  ='12345678'  # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 80         # Arbitrary non-privileged port


# Init W-Lan
wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(essid=SSID, key=KEY, security=wlan.WEP, channel=2)
print("AP mode started. SSID: {} IP: {}".format(SSID, wlan.ifconfig()[0]))

html = """<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <p>Hello World 13</p>
        </body>
    </html>
"""

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
 
s = socket.socket()
s.bind(addr)
s.listen(1)





SensorState = "READY"
StateChange = True


## ==================== Core 1  ==================== ##
## Core1 runs just the Web Server
##
## ================================================= ##

def WebServer():
    while True:
        try:
            cl, addr = s.accept()
            print('client connected from', addr)

            request = cl.recv(1024)
            #print(request)

            request = str(request)
            #response = html
            response = web_page()
            
            
            #print('GET Rquest Content = %s' % request)
            btn_record = request.find('/?RECORD')
            btn_record_stop = request.find('/?RECORD_STOP')
            btn_calibrate = request.find('/?CALIBRATE')
            
            
            
            if btn_record == 6:
                print('RECORD')
                
                sLock.acquire()
                global SensorState
                SensorState = "RECORD"
                global StateChange
                StateChange = True
                sLock.release()
                
                led.on()
            if btn_record_stop == 6:
                print('RECORD_STOP')
                
                sLock.acquire()
                global SensorState
                SensorState = "READY"
                global StateChange
                StateChange = True
                sLock.release()
                
                led.off()
            if btn_calibrate == 6:
                print('CALIBRATE')
                
                sLock.acquire()
                global SensorState
                SensorState = "CALIBRATE"
                global StateChange
                StateChange = True
                sLock.release()
                
                led.off()                
            response = web_page()
            
            
            
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            
            
     
        except OSError as e:
            cl.close()
            print('connection closed')


_thread.start_new_thread(WebServer, ()) # Starts the WebServer on Core1


## ==================== Core 0  ==================== ##
## 
##
## ================================================= ##

while True:
    
    
    if(sLock.locked() == False and StateChange):        
        
        # We acquire the semaphore lock
        sLock.acquire()
        
        Core0State = SensorState
        StateChange = False
        
        # We release the semaphore lock
        sLock.release()
    
    
    
    if(Core0State == "READY"):
        print("READY")
    if(Core0State == "RECORD"):
        print("RECORD")
    if(Core0State == "CALIBRATE"):
        print("CALIBRATE")
                        

        
        
    
    
    """
    val = uart.read(120)  # reads up to 5 bytes
       
        
    print(val) # prints data
    
    print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel()))
    print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_gyro()))
    print("")
    
        
    time.sleep(0.1)
    """
    

    time.sleep(5)



