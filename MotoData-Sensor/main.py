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
import storage

# - GPS
from gps_lib import GPS_lib




## =============== GLOBAL FUCTIONS ================= ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##

# - W-LAN AP Config
SSID ='MotoData-Sensor'   # Network SSID
KEY  ='12345678'  # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 80         # Arbitrary non-privileged port


# - Storage
DATAHEADER = "ROLL;PITCH;DATE;TIME;LAT;LONG;SPEED;ALT\n"
FILENAME = ""
FILE = None

# - File Write
FWI = 500	# FileWriteInteval
FWT = 0 	# FileWriteTimer

# - States
SensorState = "INIT" # States INIT, READY, INIT_RECORD, RECORD, STOP_RECORD, CALIBRATION 
Core0State = "INIT"
StateChange = False

# - GPS
GPSData = bytearray(255)
timeCount = time.ticks_ms()
loopCount = 0





## ================== GLOBAL VARS ================== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##

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


## ================ GLOBAL Functions =============== ##
## Initialize all global variables, pins and interfaces
##
## ================================================= ##
def GPS_send_command(command):
    """Send a command string to the GPS.  If add_checksum is True (the
    default) a NMEA checksum will automatically be computed and added.
    Note you should NOT add the leading $ and trailing * to the command
    as they will automatically be added!
    """
    add_checksum = True
    GPSSerial.write(b"$")
    GPSSerial.write(command)
    if add_checksum:
        checksum = 0
        for char in command:
            checksum ^= char
        GPSSerial.write(b"*")
        GPSSerial.write(bytes("{:02x}".format(checksum).upper(), "ascii"))
    GPSSerial.write(b"\r\n")



def changeState(endState):
    global SensorState
    global StateChange
    
    
    sLock.acquire()
    SensorState = endState
    StateChange = True
    sLock.release()
    



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

# Set GPS output
GPS_send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0') 		# only GPRMC
#GPS_send_command(b'PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0') 	# only GPGGA
#GPS_send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0') 	# GPRMC and GPGGA
#GPS_send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')		* Turn off all messages

# Set GPS update freq (Just data Sending)
#GPS_send_command(b'PMTK220,1000') 					# 1HZ
GPS_send_command(b'PMTK220,500') 					# 2HZ
#GPS_send_command(b'PMTK220,200') 					# 5Hz

# Set GPS Pos Update
#GPS_send_command(b'PMTK300,1000,0,0,0,0')			# 1HZ
GPS_send_command(b'PMTK300,200,0,0,0,0')			# 5HZ





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
            response = web_page(SensorState)
            
            
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
        

               
        
        time.sleep(5)
        

# ----- State Init Record
        
    if(Core0State == "INIT_RECORD"):
        
        
        
        
        print("INIT_RECORD")
        
        # Generate new Filename for the Record
        dir_list =  os.listdir("/sd")
        FILENAME = storage.getNewFileName(dir_list)
        
        # Generates new file with csv Header
        f = open("/sd/" + FILENAME, "w")
        f.write("ROLL;PITCH;DATE;TIME;LAT;LONG;SPEED;ALT\n")
        f.close
        
        
        time.sleep(5)
        
        FILE = open("/sd/" + FILENAME, "a")
        loopCount = 0
        
        changeState("RECORD")
             
        lastTime = time.ticks_us()

# ----- State Record
        
    if(Core0State == "RECORD"):
        #print("RECORD")
        FULLMSG = False
        GPSData = ""
        
        
        
        if(readIMU()):
            currentTime = time.ticks_us()
            lastInterval = currentTime - lastTime  # expecting this to be ~104Hz +- 4%
            lastTime = currentTime
 
            doCalculations()
            
            
        while GPSSerial.any():    
            GPSData += str(GPSSerial.read())     
        
        
        
        if(len(GPSData) > 100):
            GPSData = None
            
        time.ticks_ms()
                
        
        if(GPSData):
            print(GPSData)
            nowtime = time.ticks_ms()
            interval = nowtime - timeCount
            timeCount = nowtime
            
            loopCount += 1
            
            FWT = time.ticks_ms()
            GPS.read(GPSData)
            
            print(str(loopCount) + ";" + str(interval) + ";" + str(complementaryRoll) + ";" + str(complementaryPitch) + ";" + str(GPS.time) + ";" + str(GPS.date) + ";" + str(GPS.fix))

        
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
                FILE.close()
                changeState("READY")
            
        
        
        
        time.sleep_ms(50)

# ----- State STOP_RECORD

    if(Core0State == "STOP_RECORD"):
        print(" --- STOP_RECORD ---")
        FILE.close()
        
        time.sleep(2)
        
        changeState("READY")

# ----- State Calibration

    if(Core0State == "CALIBRATE"):
        print(" --- CALIBRATE ---")
        
        calibrateIMU(1000, 5000)
        
        print("--------------------")
        print("Gyro Drift")
        print("x", gyroDriftX)
        print("y", gyroDriftY)
        print("z", gyroDriftZ)
        print("--------------------")
        
        time.sleep(2)
        
        changeState("READY")
        

                        

        
        
    
    
    """
    val = uart.read(120)  # reads up to 5 bytes
       
        
    print(val) # prints data
    
    print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel()))
    print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_gyro()))
    print("")
    
        
    time.sleep(0.1)
    """
    

    



