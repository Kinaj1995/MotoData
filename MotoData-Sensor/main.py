## ================================================= ##
##		MotoData
##		Authors: Pascal Rusca, Janik Schilter
##
## ================================================= ##


## ==================== Imports ==================== ##
## Add libaries to import here
##
## 	!! Make shure you created a "lib and log" folder on
##	the device and add the lib files to it !!
## ================================================= ##
import machine, uos, os
from machine import UART, I2C, Pin, SPI
import time


# - Multicore
import utime
import _thread

# - WLAN
import network, socket, sys, time, gc
from sites import web_page

# - IMU
from lsm6dsox import LSM6DSOX
import math

# - SD Card
import sdcard
from storage import STORAGE_lib

# - GPS
from gps_lib import GPS_lib, GPSNoCompDataType, GPSMessageError


import neopixel




## =================== USER VARS =================== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##

# - W-LAN AP Config
SSID ='MotoData-Sensor'   # Network SSID
KEY  ='12345678'  # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 80         # Arbitrary non-privileged port



## ================== GLOBAL VARS ================== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##

# - Storage
DATAHEADER = "LOOPCOUNT;INTERVAL(ms);ROLL;PITCH;TIME;DATE;LAT;LONG;SPEED;ALT\n"
FILENAME = ""
FILE = None
MAXLINECOUNT = 1000


# - States
SensorState = "INIT" # States INIT, READY, INIT_RECORD, RECORD, STOP_RECORD, CALIBRATION, RENEW_FILE
Core0State = "INIT"
StateChange = False


# - GPS
GPSData = bytearray(255)
timeCount = time.ticks_ms()
loopCount = 0


# - Semaphores
sLock = _thread.allocate_lock()


# - SerialPort for GPS
GPSSerial = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


# - IMU 
IMU = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))		# Init I2C Connection


# units m/s/s i.e. accelZ if often 9.8 (gravity)
accelX = 0.0
accelY = 0.0
accelZ = 0.0

# units dps (degrees per second)
gyroX = 0.0 
gyroY = 0.0 
gyroZ = 0.0

# units dps
gyroDriftX = 0.0
gyroDriftY = 0.0
gyroDriftZ = 0.0

# units degrees (excellent roll, pitch, yaw minor drift)
complementaryRoll = 0.0
complementaryPitch = 0.0
complementaryYaw = 0.0    


# - Pindefinitions
led = Pin(6, Pin.OUT) # Internal Pin

p = Pin(21, Pin.OUT)
n = neopixel.NeoPixel(p, 2)

for i in range(2):
    n[i] = (0,0,0)

n.write()



## ================ GLOBAL Functions =============== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##
def GPS_send_command(command, add_checksum):
    GPSSerial.write(b"$")
    GPSSerial.write(command)
    if add_checksum:
        checksum = 0
        for char in command:
            checksum ^= char
        GPSSerial.write(b"*")
        GPSSerial.write(bytes("{:02x}".format(checksum).upper(), "ascii"))
    GPSSerial.write(b"\r\n")
    time.sleep(1)



def changeState(endState):
    global SensorState
    global StateChange
    
    
    sLock.acquire()
       
    SensorState = endState
    StateChange = True
        
    sLock.release()
    
def errorLog(time, date, message):
    errorlogFile = open("/log/error.log", "a")
    errorlogFile.write(str(date) + "--" + str(time) + "-- " + str(message) + "\n")
    errorlogFile.close()


## ====================  INIT   ==================== ##
## Initialize all Sensors an Objects
##
## ================================================= ##
# - Init W-Lan
wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(essid=SSID, key=KEY, security=wlan.WEP, channel=2)
print("AP mode started. SSID: {} IP: {}".format(SSID, wlan.ifconfig()[0]))


# - Init Webserver
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

# - SD-Card
CS = machine.Pin(5, machine.Pin.OUT)
spi = machine.SPI(0,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=Pin(6),mosi=machine.Pin(7),miso=machine.Pin(4))
sd = sdcard.SDCard(spi,CS)

vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")
time.sleep(5)

# - GPS
GPS = GPS_lib()

# - Storage
STR = STORAGE_lib()

# Set GPS output
GPS_send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', True) 		# only GPRMC
#GPS_send_command(b'PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', True) 	# only GPGGA
#GPS_send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', True) 	# GPRMC and GPGGA
#GPS_send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', True)		* Turn off all messages

# Set GPS Pos Update
#GPS_send_command(b'PMTK220,1000', True) 					# 1HZ
#GPS_send_command(b'PMTK220,500', True) 					# 2HZ
GPS_send_command(b'PMTK220,200', True) 					# 5Hz

# Set GPS update freq (Just data Sending)
#GPS_send_command(b'PMTK300,1000,0,0,0,0', True)			# 1HZ
#GPS_send_command(b'PMTK300,500,0,0,0,0', True)			# 2HZ
GPS_send_command(b'PMTK300,200,0,0,0,0', True)			# 5HZ





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
            
            
            
            #print('GET Rquest Content = %s' % request)
            btn_record = request.find('/?RECORD')
            btn_record_stop = request.find('/?RECORD_STOP')
            btn_calibrate = request.find('/?CALIBRATE')
            
            
            
            if btn_record == 6:
                changeState("INIT_RECORD")

            if btn_record_stop == 6:
                changeState("STOP_RECORD")
                
            if btn_calibrate == 6:
                changeState("CALIBRATE")
               
            response = web_page(SensorState)   
            
            
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            
            
     
        except OSError as e:
            cl.close()
            print('connection closed')
            
        


_thread.start_new_thread(WebServer, ()) # Starts the WebServer on Core1



## ==================== IMU Calc =================== ##
## Calculates the angles with the IMU
##
## ================================================= ##

def readIMU():
    
    global gyroX, gyroY, gyroZ, accelX, accelY, accelZ
    
    try:
        accd = IMU.read_accel()
        gyd = IMU.read_gyro()
        
        accelX = accd[0]
        accelY = accd[1]
        accelZ = accd[2]
        gyroX = gyd[0]
        gyroY = gyd[1]
        gyroZ = gyd[2]
        
        return True
        
    except:
        return False
        
    
def calibrateIMU(delayMillis, calibrationMillis):
    
    calibrationCount = 0
        
    sumX = 0.0000000000
    sumY = 0.0
    sumZ = 0.0
        
    starttime = time.ticks_ms()
        
    while(time.ticks_ms() < starttime + calibrationMillis):
        
        if(readIMU()):
        
            sumX += gyroX
            sumY += gyroY
            sumZ += gyroZ        
            
            calibrationCount += 1
        
    if(calibrationCount == 0):
        print("Calibration faild!")
    
    global gyroDriftX, gyroDriftY, gyroDriftZ
    
    gyroDriftX = sumX / calibrationCount
    gyroDriftY = sumY / calibrationCount
    gyroDriftZ = sumZ / calibrationCount


def doCalculations():
    
    global complementaryRoll, complementaryPitch, complementaryYaw
    
    accRoll = math.atan2(accelY, accelZ) * 180 / math.pi
    accPitch = math.atan2(-accelX, math.sqrt(accelY * accelY + accelZ * accelZ)) * 180 / math.pi
    
    lastFrequency = float(1000000.0) / lastInterval;
    
    complementaryRoll = complementaryRoll + ((gyroX - gyroDriftX) / lastFrequency)
    complementaryPitch = complementaryPitch + ((gyroY - gyroDriftY) / lastFrequency)
    complementaryYaw = complementaryYaw + ((gyroZ - gyroDriftZ) / lastFrequency)
    
    complementaryRoll = 0.98 * complementaryRoll + 0.02 * accRoll
    complementaryPitch = 0.98 * complementaryPitch + 0.02 * accPitch
    
def printCalculations():
    
    print("ROLL: {}".format(complementaryRoll))
    print("PITCH: {}".format(complementaryPitch))


## ==================== Core 0  ==================== ##
## 
##
## ================================================= ##

while True:
    
    
    
# ----- Checks for StateChanges    
    if(sLock.locked() == False and StateChange):        
        
        # We acquire the semaphore lock
        sLock.acquire()
        
        Core0State = SensorState
        StateChange = False
        
        # We release the semaphore lock
        sLock.release()
        
        print("State changed.")
    
    

        
        
    
# ----- State READY  
    
    if(Core0State == "READY"):
        print("READY")
        

               
        n[0] = (100,0,0)
        n[1] = (100,0,0)
        n.write()
        time.sleep(5)
        

# ----- State Init Record
        
    if(Core0State == "INIT_RECORD"):
        print("INIT_RECORD")
        
        n[0] = (0,254,0)
        n[1] = (0,254,0)
        n.write()
        
        # Generate new Filename for the Record
        dir_list =  os.listdir("/sd")
        FILENAME = STR.getNewFileName(dir_list)
        
        # Generates new file with csv Header
        try:
            f = open("/sd/" + STR.getFilename(), "w")
            f.write(DATAHEADER)
            f.close()
        except OSError as e:
            print(e)
        
        
        FILE = open("/sd/" + STR.getFilename(), "a")
                
        changeState("RECORD")
        
        loopCount = 0
        lastTime = time.ticks_us()
        
# ----- State Renew File
        
    if(Core0State == "RENEW_FILE"):
        print("RENEW_FILE")
        
        # Generate new Filename for the Record
        dir_list =  os.listdir("/sd")
        FILENAME = STR.increaseFileName(FILENAME)
                
        FILE = open("/sd/" + STR.getFilename(), "a")
               
        changeState("RECORD")
        
        loopCount = 0
        lastTime = time.ticks_us()

# ----- State Record
        
    if(Core0State == "RECORD"):
        #print("RECORD")
        GPSData = ""
        
        
        
        if(readIMU()):
            currentTime = time.ticks_us()
            lastInterval = currentTime - lastTime  # expecting this to be ~104Hz +- 4%
            lastTime = currentTime
     
            doCalculations()
                

        
      
        #-- Read Data from Serial if avaiable
        nowtime = time.ticks_ms()
        while GPSSerial.any():    
            GPSData += str(GPSSerial.read())
            
            if(time.ticks_ms() - nowtime > 500):
                break
        

        
        # -- If revieved Date is over 100 Chars discard
        if(len(GPSData) > 100):
            GPSData = None
            

                
        # -- When GPS Data is recived it will get processed
        if(GPSData):
            
            # -- Timing between each GPS Date recieved
            nowtime = time.ticks_ms()
            interval = nowtime - timeCount
            timeCount = nowtime
            
            loopCount += 1		# Loopcount von Record Loop

            # -- Parsing GPS Data            
            try:
                
                GPS.read(GPSData)
                        
            except GPSMessageError:
                print("GPS Message Error")
                errorLog(GPS.time, GPS.date, "GPS Message Error")
            
            except GPSNoCompDataType:
                print("GPS Message Error")
                errorLog(GPS.time, GPS.date, "no complete GPS Message")
            
            except MemoryError as e:
                print(e)
                errorLog(GPS.time, GPS.date, "MemoryError: " + e)
                time.sleep(5)
                
            
            # -- File writing
            try:
                

                FILE.write(str(loopCount) + ";" + str(interval) + ";" )
                FILE.write(str(complementaryRoll) + ";" + str(complementaryPitch) + ";")
                FILE.write(str(GPS.time) + ";" + str(GPS.date) + ";" + str(GPS.fix))
                
                if(GPS.fix):
                    FILE.write(";" + str(GPS.lat) + ";" + str(GPS.long) + ";" + str(GPS.speed) + "\n")
                else:
                    FILE.write("\n")
                



            except TypeError as e:
                print(e)
                errorLog(GPS.time, GPS.date, "TypeError: File Write")
                FILE.close()
                changeState("READY")
            
            except OSError as e:
                print("OSError:" + str(e))
                errorLog(GPS.time, GPS.date, "OSError: File Write" + str(e))
                changeState("READY")
                
                
            if(loopCount >= MAXLINECOUNT):
                FILE.close()
                changeState("RENEW_FILE")
            
            
            # -- Debug Print
            print(GPSData)
            print(str(loopCount) + ";" + str(interval) + ";" + str(complementaryRoll) + ";" + str(complementaryPitch) + ";" + str(GPS.time) + ";" + str(GPS.date) + ";" + str(GPS.fix))

          
                
            
        
        
        
        time.sleep_ms(50)

# ----- State STOP_RECORD

    if(Core0State == "STOP_RECORD"):
        print(" --- STOP_RECORD ---")
        
        n.write()
        
        try:
            FILE.close()
        
        except AttributeError as e:
            print(e)
            errorLog(GPS.time, GPS.date, "AttributeError: STOP_RECORD")
        
        time.sleep(2)
        
        changeState("READY")

# ----- State Calibration

    if(Core0State == "CALIBRATE"):
        print(" --- CALIBRATE ---")
        n[0] = (0,0,254)
        n[1] = (0,0,254)
        n.write()
        
        calibrateIMU(1000, 5000)
        
        print("--------------------")
        print("Gyro Drift")
        print("x", gyroDriftX)
        print("y", gyroDriftY)
        print("z", gyroDriftZ)
        print("--------------------")
        
        time.sleep(2)
        
        changeState("READY")
        

                        

        
        

    

    



