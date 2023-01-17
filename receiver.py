import time
import serial

ser = serial.Serial(
        port='/dev/ttyAMA2',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )


while True:
    if ser.readable():
        res = ser.readline().decode('utf-8')
        if res:
            print(res)

