import spidev
from datetime import datetime
import time
import RPi.GPIO as GPIO


# Connection table
# +------+----------+----------------------------------+-------------------------------------+----------------+
# | Pin  |   Name   |             Remarks              |               Details               |   Connect to   |
# +------+----------+----------------------------------+-------------------------------------+----------------+
# |    1 | GND      | Supply ground                    |                                     | RPI-39         |
# |    2 | /TC_EN   | TC enable                        |                                     | RPI-34         |
# |    3 | VDDIN    | Power supply for digital part    | Op: 2.7 - 3.3 V | Abs: 0 - 3.6 V    | RPI-17         |
# |    4 | VIN      | Power supply for analog part     | Op: 2.0 - 5.5 V | Abs: -0.3 - 6.0 V | RPI-02         |
# |    5 | /TC_BUSY | Host interface busy output       |                                     | RPI-22         |
# |    6 | TC_MISO  | Host interface data output       |                                     | RPI-21         |
# |    7 | TC_MOSI  | Host interface data input        |                                     | RPI-19         |
# |    8 | /TC_CS   | Host interface chip select input |                                     | RPI-24         |
# |    9 | TC_SCK   | Host interface clock input       |                                     | RPI-23         |
# |   10 | GND      | Supply ground                    |                                     | RPI-30         |
# +------+----------+----------------------------------+-------------------------------------+----------------+



GPIO.setmode(GPIO.BOARD)
BUSY_CHANNEL = 22

GET_DEVICE_INFO    = (0x30, 0x01, 0x01, 0x00)
GET_DEVICE_ID      = (0x30, 0x02, 0x01, 0x14)
RESET_DATA_POINTER = (0x20, 0x0D, 0x00)
EDP_HEADER         = (0x3A, 0x01, 0xE0, 0x03, 0x20, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
WRITE_TO_SCREEN    = (0x20, 0x01, 0x00)
WRITE_EDP_HEADER   = WRITE_TO_SCREEN + (0x10,) + EDP_HEADER
DISPLAY_UPDATE     = (0x24, 0x01, 0x00)
TERMINATOR         = 0x00

# Status Codes
OK   = (0x90, 0x00)
ERR1 = (0x67, 0x00)
ERR2 = (0x6C, 0x00)
ERR3 = (0x6A, 0x00)
ERR4 = (0x6D, 0x00)

class StatusCode():
    def __init__(self, code=None, name='', message=''):
        self.code    = code
        self.name    = name
        self.message = message
    def log(self):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(t, self.code, self.name, self.message, sep=' - ')

STATUS_CODE = {
    OK   : StatusCode(OK, 'EP_SW_NORMAL_PROCESSING', 'command successfully executed'),
    ERR1 : StatusCode(ERR1, 'EP_SW_WRONG_LENGTH', 'incorrect length (invalid Lc value or command too short or too long)'),
    ERR2 : StatusCode(ERR2, 'EP_SW_INVALID_LE', 'invalid Le field'),
    ERR3 : StatusCode(ERR3, 'EP_SW_WRONG_PARAMETERS_P1P2', 'invalid P1 or P2 field'),
    ERR4 : StatusCode(ERR4, 'EP_SW_INSTRUCTION_NOT_SUPPORTED', 'command not supported'),
}


class TCMConnection():
    DEVICE_INFO = 'MpicoSys TC-P74-230_v1.1'
    
    def __init__(self, bus=0, device=0):
        GPIO.setup(BUSY_CHANNEL, GPIO.IN)
        GPIO.add_event_detect(BUSY_CHANNEL, GPIO.RISING)
        
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        # According to TCM datasheet: Bit rate up to 3 MHz
        # DO NOT GO OVER 500kHz. The TCM is not being able to receive the commands and returns INSTRUCTION_NOT_SUPPORTED most of the time.
        self.spi.max_speed_hz = 500000
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
        self.spi.cshigh        = False
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

    def _waitForBusy(self):
        """ Wait until bussy is off. Abs minimum 28us (T_A+T_BUSY+T_NS).
            It usually takes around 1ms. From time to time it might take up to 15ms.
            Updating the screen takes around 2.5 seconds. """
        while not GPIO.event_detected(BUSY_CHANNEL):
            pass

    def write(self, bytesMessage):
        '''Writes a byte message through SPI and wawits for the busy signal to turn off'''
        self.spi.writebytes(bytesMessage)
        self._waitForBusy()

    def getDeviceInfo(self):
        self.write(GET_DEVICE_INFO)
        return self.spi.readbytes(len(self.DEVICE_INFO)+1+2)
            
    def _fetchDeviceId(self):
        self.write(GET_DEVICE_ID)
        return self.spi.readbytes(20+2)
    
    def getDeviceId(self):
        fetch = self._fetchDeviceId()
        if len(fetch) != 22:
            print("error: couldn't fetch device Id")
        id = fetch[:-2]
        statusCode = tuple(fetch[-2:])
        if statusCode in STATUS_CODE:
            STATUS_CODE.get(statusCode).log()
        return id
    
    def resetDataPointer(self):
        self.write(RESET_DATA_POINTER)
        statusCode = tuple(self.spi.readbytes(2))
        if statusCode in STATUS_CODE:
            STATUS_CODE.get(statusCode).log()
            return True
        return False

    def displayUpdate(self):
        self.write(DISPLAY_UPDATE)
        statusCode = tuple(self.spi.readbytes(2))
        if statusCode in STATUS_CODE:
            STATUS_CODE.get(statusCode).log()
            return True
        print(statusCode)
        return False
    
    def writeHeader(self):
        self.write(WRITE_EDP_HEADER)
        statusCode = tuple(self.spi.readbytes(2))
        if statusCode in STATUS_CODE:
            STATUS_CODE.get(statusCode).log()
            return True
        return False
    
    def _writeLine(self, black=True):
        color = (0xFF,) if black else (0x00,)
        self.write(WRITE_TO_SCREEN + (0x3C,) + 60 * color)
        statusCode = tuple(self.spi.readbytes(2))
        if statusCode in STATUS_CODE:
            STATUS_CODE.get(statusCode).log()
            return True
        return False
        
    def writeWhiteLine(self):
        return self._writeLine(black=False)

    def writeBlackLine(self):
        return self._writeLine()

    def verifyConnection(self):
        deviceInfoResponse = self.getDeviceInfo()
        if TERMINATOR not in deviceInfoResponse:
            print("error: terminator not found on response.")
            return False
        
        strEnd = deviceInfoResponse.index(0x00)
        if strEnd < len(deviceInfoResponse):
            deviceInfo = deviceInfoResponse[:strEnd]
            deviceInfo = ''.join(chr(x) for x in deviceInfo)
            statusCode = tuple(deviceInfoResponse[strEnd+1:strEnd+3])
            if statusCode == OK:
                STATUS_CODE.get(statusCode).log()
                print("deviceInfo: " + deviceInfo)
                return True
            else:
                STATUS_CODE.get(statusCode).log() if statusCode in STATUS_CODE else None
                return False

    def dooplerScreen(self):
        self.resetDataPointer()
        self.writeHeader()
        for _ in range(2):
            for growing in range(1,20,2):
                for witdh in range(growing):
                    self.writeBlackLine()
                for witdh in range(growing+1):
                    self.writeWhiteLine()
            for decreacing in range(19,1,-2):
                for witdh in range(decreacing):
                    self.writeBlackLine()
                for witdh in range(decreacing-1):
                    self.writeWhiteLine()
            self.writeBlackLine()
        self.displayUpdate()
                
        

conn = TCMConnection()
print("Connected:", conn.verifyConnection())
print("Devide Id:", conn.getDeviceId())
conn.dooplerScreen()
print("Done\n")
