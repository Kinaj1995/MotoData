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

# - SD Card
import sdcard
import storage


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
FILENAME = ""

# - States
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

# units degrees (roll and pitch noisy, yaw not possible)
accRoll  = 0.0
accPitch  = 0.0
accYaw = 0.0

# units degrees (excellent roll, pitch, yaw minor drift)
complementaryRoll = 0.0
complementaryPitch = 0.0
complementaryYaw = 0.0    


# - Pindefinitions
led = Pin(6, Pin.OUT) # Internal Pin




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







"""
# Create a file and write something to it
with open("/sd/00004.csv", "w") as file:
    print("Writing to data.txt...")
    file.write("Welcome to microcontrollerslab!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/00004.csv", "r") as file:
    print("Reading data.txt...")
    data = file.read()
    print(data)
"""
time.sleep(5)







SensorState = "READY"
StateChange = True


## ==================== Core 1  ==================== ##
## Core1 runs just the Web Server
##
## ================================================= ##

def WebServer():
    while True:
        
        global SensorState
        global StateChange
        
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
                
                sLock.acquire()
                SensorState = "RECORD"
                StateChange = True
                sLock.release()
                
                led.on()
            if btn_record_stop == 6:
                
                sLock.acquire()
                SensorState = "READY"
                StateChange = True
                sLock.release()
                
                led.off()
            if btn_calibrate == 6:
                
                sLock.acquire()
                SensorState = "CALIBRATE"
                StateChange = True
                sLock.release()
                
                led.off()                
           
            
            
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
    
    
    accd = IMU.read_accel()
    gyd = IMU.read_gyro()
    
    accelX = accd[0]
    accelY = accd[1]
    accelZ = accd[2]
    gyroX = gyd[0]
    gyroY = gyd[1]
    gyroZ = gyd[2]
        
    
def calibrateIMU(delayMillis, calibrationMillis):
    
    calibrationCount = 0
        
    sumX = 0.0000000000
    sumY = 0.0
    sumZ = 0.0
        
    starttime = time.ticks_ms()
        
    while(time.ticks_ms() < starttime + calibrationMillis):
        
        readIMU()
        
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
    
    
    
    if(Core0State == "READY"):
        print("READY")
        
        # Generate new Filename for next Record
        dir_list =  os.listdir("/sd")
        FILENAME = storage.getNewFileName(dir_list)
        
        
        
        time.sleep(5)
        
    if(Core0State == "RECORD"):
        print("RECORD")
        
        readIMU()
        
        """
        GPSData = GPSSerial.readline()
        print(GPSData) # prints data
        
        try:
            f = open("/sd/" + FILENAME, "a")
            f.write(GPSData)
            f.close()
            print("Written to File ", FILENAME)
            
        except TypeError as e:
            print(e)
            f.close()
            
        
        
        
        print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel()))
        print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_gyro()))
        print("")
        """
        
        time.sleep(0.1)
        
        
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
        
        if(sLock.locked() == False and StateChange == False):        
        
            # We acquire the semaphore lock
            sLock.acquire()
            
            SensorState = "READY"
            StateChange = True
            
            # We release the semaphore lock
            sLock.release()
                        

        
        
    
    
    """
    val = uart.read(120)  # reads up to 5 bytes
       
        
    print(val) # prints data
    
    print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel()))
    print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_gyro()))
    print("")
    
        
    time.sleep(0.1)
    """
    

    



