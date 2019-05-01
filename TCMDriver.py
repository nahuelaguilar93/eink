import spidev
import time

GET_DEVICE_INFO = [0x30, 0x01, 0x01, 0x00]
POLL_RESPONSE = [0x00, 0x00]

class TCMConnection():
    deviceInfo = 'MpicoSys TC-P74-230_v1.0'
    
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 5000

    def __del__(self):
        self.spi.close()
        
    def getDeviceInfo(self):
        self.spi.writebytes(GET_DEVICE_INFO)
        time.sleep(0.001) # Wait until bussy is off.
        return self.spi.readbytes(len(self.deviceInfo)+1+2)
    
    def verifyConnection(self):
        deviceInfoResponse = self.getDeviceInfo()
        if 0x00 not in deviceInfoResponse:
            print("Zero terminator not found on response.")
            return False
        
        strEnd = deviceInfoResponse.index(0x00)
        if strEnd == 1:
            print("statusCode: " + str(deviceInfoResponse[:2]))
            return False
        elif strEnd < len(deviceInfoResponse):
            deviceInfo = deviceInfoResponse[:strEnd]
            deviceInfo = ''.join(chr(x) for x in deviceInfo)
            print("deviceInfo: " + deviceInfo)
            statusCode = deviceInfoResponse[strEnd+1:strEnd+3]
            print("statusCode: " + str(statusCode))
            if (deviceInfo == self.deviceInfo and
                statusCode == [0x90, 0x00]):
                print("DeviceInfo is the expected.")
                print("Status code is the expected.")
                print("Connection Success!")
                return True
            return False

conn = TCMConnection()
while True:
    print("Connected: ", conn.verifyConnection())
    print()
    time.sleep(5)