import serial
ser= serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
ser.write([0xAA])