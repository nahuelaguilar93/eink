import serial
terminator = "\r\n"
s = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=5.0 )
s.write( bytes((0xAA,)*30+(0xBB,)*30) )

from ESP8266Driver import ESP8265, getImageData, getTimeToSleep, getConnection
