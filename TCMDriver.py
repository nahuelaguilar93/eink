import spidev
from datetime import datetime
import time
from enum import Enum

# Connection table
# +------+----------+----------------------------------+-------------------------------------+----------------+
# | Pin  |   Name   |             Remarks              |               Details               |   Connect to   |
# +------+----------+----------------------------------+-------------------------------------+----------------+
# |    1 | GND      | Supply ground                    |                                     | RPI-39         |
# |    2 | /TC_EN   | TC enable                        |                                     | RPI-34         |
# |    3 | VDDIN    | Power supply for digital part    | Op: 2.7 - 3.3 V | Abs: 0 - 3.6 V    | RPI-17         |
# |    4 | VIN      | Power supply for analog part     | Op: 2.0 - 5.5 V | Abs: -0.3 - 6.0 V | RPI-02         |
# |    5 | /TC_BUSY | Host interface busy output       |                                     | (disconnected) |
# |    6 | TC_MISO  | Host interface data output       |                                     | RPI-21         |
# |    7 | TC_MOSI  | Host interface data input        |                                     | RPI-19         |
# |    8 | /TC_CS   | Host interface chip select input |                                     | RPI-24         |
# |    9 | TC_SCK   | Host interface clock input       |                                     | RPI-23         |
# |   10 | GND      | Supply ground                    |                                     | RPI-30         |
# +------+----------+----------------------------------+-------------------------------------+----------------+

GET_DEVICE_INFO = (0x30, 0x01, 0x01, 0x00)
POLL_RESPONSE = [0x00, 0x00]

# Status Codes
OK = (0x90, 0x00)
ERR1 = (0x67, 0x00)
ERR2 = (0x6C, 0x00)
ERR3 = (0x6A, 0x00)
ERR4 = (0x6D, 0x00)

class StatusCode():
    def __init__(self, code=None, name='', message=''):
        self.code = code
        self.name = name
        self.message = message
    def log(self):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(t, self.code, self.name, self.message, sep=' - ')

STATUS_CODE = {
    OK : StatusCode(OK, 'EP_SW_NORMAL_PROCESSING', 'command successfully executed'),
    ERR1 : StatusCode(ERR1, 'EP_SW_WRONG_LENGTH', 'incorrect length (invalid Lc value or command too short or too long)'),
    ERR2 : StatusCode(ERR2, 'EP_SW_INVALID_LE', 'invalid Le field'),
    ERR3 : StatusCode(ERR3, 'EP_SW_WRONG_PARAMETERS_P1P2', 'invalid P1 or P2 field'),
    ERR4 : StatusCode(ERR4, 'EP_SW_INSTRUCTION_NOT_SUPPORTED', 'command not supported'),
}


class TCMConnection():
    DEVICE_INFO = 'MpicoSys TC-P74-230_v1.1'
    
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
        # According to library documentation, spi.lsbfirst might be read only,
        # so just make sure it is false or we might need to invert data locally.
        assert self.spi.lsbfirst == False
        self.spi.cshigh = False
        self.spi.bits_per_word = 8
        
        
    def reverseBits(byte):
        """ According to library documentation, spi.lsbfirst might be hardware fixed,
            This method might be of help when changing to another master device. """
        byte = ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)
        byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
        byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
        return byte

    def __del__(self):
        self.spi.close()
        
    def getDeviceInfo(self):
        self.spi.writebytes(GET_DEVICE_INFO)
        # Wait until bussy is off. This should be replaced by a busy byte read. Abs minimum 28us (T_A+T_BUSY+T_NS)
        time.sleep(0.001)
        return self.spi.readbytes(len(self.DEVICE_INFO)+1+2)
    
    def verifyConnection(self):
        deviceInfoResponse = self.getDeviceInfo()
        if 0x00 not in deviceInfoResponse:
            print("Zero terminator not found on response.")
            return False
        
        strEnd = deviceInfoResponse.index(0x00)
        if strEnd < len(deviceInfoResponse):
            deviceInfo = deviceInfoResponse[:strEnd]
            deviceInfo = ''.join(chr(x) for x in deviceInfo)
            statusCode = tuple(deviceInfoResponse[strEnd+1:strEnd+3])
            if statusCode == OK:
                STATUS_CODE.get(statusCode).log()
                print("deviceInfo: " + deviceInfo)
                print("Connection Success!")
                return True
            else:
                STATUS_CODE.get(statusCode).log() if statusCode in STATUS_CODE else None
                return False

conn = TCMConnection()
while True:
    print("Connected: ", conn.verifyConnection())
    print()
    time.sleep(2)
