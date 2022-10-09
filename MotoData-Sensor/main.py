import machine, uos
import utime
import _thread

import sdcard

from lsm6dsox import LSM6DSOX



from machine import UART, I2C, Pin
import time

lsm = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))




## --- WLAN
import network, socket, sys, time, gc


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

time.sleep(20)

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
            <p>Hello World</p>
        </body>
    </html>
"""

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
 
s = socket.socket()
s.bind(addr)
s.listen(1)


## Semaphore
sLock = _thread.allocate_lock()


uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


led1 = Pin(6, Pin.OUT)


def CoreTask():
    while True:
        try:
            cl, addr = s.accept()
            print('client connected from', addr)

            request = cl.recv(1024)
            print(request)

            request = str(request)
            response = html
            
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
     
        except OSError as e:
            cl.close()
            print('connection closed')


_thread.start_new_thread(CoreTask, ())



while True:
    # We acquire the semaphore lock
    sLock.acquire()

    # We release the semaphore lock
    sLock.release()
    
    val = uart.read(120)  # reads up to 5 bytes
       
        
    print(val) # prints data
    
    print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel()))
    print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_gyro()))
    print("")
    
        
    time.sleep(0.1)




