import spidev
import time

GET_DEVICE_INFO = [0x30, 0x01, 0x01, 0x0F]
POLL_RESPONSE = [0x00, 0x00]

class TCMConnection():
    deviceInfo = 'MpicoSys TC-P74-230_v1.0'
    
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        # According to TCM datasheet: Bit rate up to 3 MHz
        self.spi.max_speed_hz = 5000
        # SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], min: 0b00 = 0, max: 0b11 = 3
        # According to TCM datasheet:
        #         Polarity – CPOL = 1; clock transition high-to-low on the leading edge and low-to-high on the trailing edge
        #         Phase – CPHA = 1; setup on the leading edge and sample on the trailing edge
        # This was verified as correct by testing the output signal using Analog Discorvery.
        self.spi.mode = 0b11
        # According to TCM datasheet: Bit order – MSB first
        spi.lsbfirst = False

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
    time.sleep(2)