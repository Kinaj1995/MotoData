# NINA 27, 26, 25 are R, G, B
from machine import Pin
from machine import SPI
import time
from micropython import const

_START_CMD             = const(0xe0)
_END_CMD               = const(0xee)
_ERR_CMD               = const(0xef)
_REPLY_FLAG            = const(1<<7)
_CMD_FLAG              = const(0)

_SET_PIN_MODE		= 0x50
_SET_DIGITAL_WRITE	= 0x51
_SET_ANALOG_WRITE	= 0x52
_GET_DIGITAL_READ    = 0x53
_GET_ANALOG_READ     = 0x54

ESP_BUSY  = Pin(10, Pin.IN)
ESP_RESET = Pin(3, Pin.OUT, False)
ESP_CS    = Pin(9, Pin.OUT, True)
ESP_GPIO0 = Pin(2)
ESP_MISO  = Pin(8)
ESP_MOSI  = Pin(11)
ESP_SCK   = Pin(14) 

LEDR = 27
LEDG = 25
LEDB = 26

spiwifi = SPI(1, baudrate=100000, sck=ESP_SCK, mosi=ESP_MOSI, miso=ESP_MISO)

def reset():
    ESP_GPIO0.init(Pin.OUT)
    ESP_GPIO0.value(True)

    ESP_CS.high()
    ESP_RESET.low()

    time.sleep(0.01)
    ESP_RESET.high()
    time.sleep(0.75)

    ESP_GPIO0.init(Pin.IN)

    print("ESP32 reset")

def wait_ready():
    wait_status = ESP_BUSY.value()

    while wait_status:
        time.sleep(0.05)
        wait_status = ESP_BUSY.value()


def read_response():
    response = []
    response_bytes = []
    bytes_read = 0

    max_read = 32
    bytes_read = 0

    wait_ready()
    ESP_CS.low()

    while True:
        read_byte = spiwifi.read(1)
        response_bytes.append(read_byte)
        if read_byte == bytes([_END_CMD]):
            break
        if read_byte == bytes([_ERR_CMD]):
            raise RuntimeError('Error waiting on WiFi Command')

        bytes_read += 1
        if bytes_read > max_read:
            raise RuntimeError('Error waiting on WiFi command')

    ESP_CS.high()

    num_params = response_bytes[2]
    index = 3

    for _ in num_params:
        length = int.from_bytes(response_bytes[index], "little")
        newparam = response_bytes[index+1:index+1+length]
        index += 1 + length
        response.append(b''.join(newparam))

    return response

def send_command(cmd, params=[], num_params=-1):
    if num_params < 0:
        num_params = len(params)
    
    total_bytes = 3 + num_params + 1

    for p in params:
        pbytes = bytearray(p)
        total_bytes = total_bytes + len(pbytes)
    
    sendbuffer = bytearray(total_bytes)

    sendbuffer[0] = _START_CMD
    sendbuffer[1] = cmd & ~_REPLY_FLAG
    sendbuffer[2] = num_params

    index = 3

    for p in params:
        pbytes = bytearray(p)
        lenpbytes = len(pbytes)

        sendbuffer[index] = lenpbytes
        sendbuffer[index+1:index+1+lenpbytes] = pbytes
        index += 1+lenpbytes
    sendbuffer[index] = _END_CMD

    wait_ready()
    ESP_CS.low()
    spiwifi.write(sendbuffer)
    ESP_CS.high()

def set_ninapin_mode(pin, mode):
    send_command(_SET_PIN_MODE, [[pin], [mode]])
    return read_response()

def ninapin_digital_write(pin, value):
    if value == 0:
        value = 1
    else:
        value = 0

    send_command(_SET_DIGITAL_WRITE, [[pin], [value]])
    return read_response()

reset()