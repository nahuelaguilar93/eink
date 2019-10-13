import spidev
import time
import RPi.GPIO as GPIO
import logging
from utils import bitsToFormatType4bytes

logging.basicConfig( format = '%(asctime)s [%(levelname)s] %(message)s',
                     level  = logging.INFO )



# Connection table
# +------+----------+----------------------------------+-------------------------------------+----------------+
# | Pin  |   Name   |             Remarks              |               Details               |   Connect to   |
# +------+----------+----------------------------------+-------------------------------------+----------------+
# |    1 | GND      | Supply ground                    |                                     | RPI-06         |
# |    2 | /TC_EN   | TC enable                        |                                     | RPI-20         |
# |    3 | VDDIN    | Power supply for digital part    | Op: 2.7 - 3.3 V | Abs: 0 - 3.6 V    | RPI-17         |
# |    4 | VIN      | Power supply for analog part     | Op: 2.0 - 5.5 V | Abs: -0.3 - 6.0 V | RPI-02         |
# |    5 | /TC_BUSY | Host interface busy output       |                                     | RPI-22         |
# |    6 | TC_MISO  | Host interface data output       |                                     | RPI-21         |
# |    7 | TC_MOSI  | Host interface data input        |                                     | RPI-19         |
# |    8 | /TC_CS   | Host interface chip select input |                                     | RPI-24         |
# |    9 | TC_SCK   | Host interface clock input       |                                     | RPI-23         |
# |   10 | GND      | Supply ground                    |                                     | RPI-25         |
# +------+----------+----------------------------------+-------------------------------------+----------------+



GPIO.setmode(GPIO.BOARD)
BUSY_CHANNEL = 22

GET_DEVICE_INFO    = (0x30, 0x01, 0x01, 0x00)
GET_DEVICE_ID      = (0x30, 0x02, 0x01, 0x14)
RESET_DATA_POINTER = (0x20, 0x0D, 0x00)
EDP_HEADER         = (0x3A, 0x01, 0xE0, 0x03, 0x20, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
WRITE_TO_SCREEN    = (0x20, 0x01, 0x00)
DISPLAY_UPDATE     = (0x24, 0x01, 0x00)
TERMINATOR         = 0x00

# Status Codes
OK   = (0x90, 0x00)
ERR1 = (0x67, 0x00)
ERR2 = (0x6C, 0x00)
ERR3 = (0x6A, 0x00)
ERR4 = (0x6D, 0x00)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

class StatusCode():
    def __init__(self, code=None, name='', message=''):
        self.code    = code
        self.name    = name
        self.message = message
        
    def logMessage(self):
        return ' - '.join((str(self.code), self.name, self.message))
        
class SuccessCode(StatusCode):
    def log(self):
        logging.debug(self.logMessage())

class ErrorCode(StatusCode):
    def log(self):
        logging.error(self.logMessage())

STATUS_CODE = {
    OK   : SuccessCode(OK, 'EP_SW_NORMAL_PROCESSING', 'command successfully executed'),
    ERR1 : ErrorCode(ERR1, 'EP_SW_WRONG_LENGTH', 'incorrect length (invalid Lc value or command too short or too long)'),
    ERR2 : ErrorCode(ERR2, 'EP_SW_INVALID_LE', 'invalid Le field'),
    ERR3 : ErrorCode(ERR3, 'EP_SW_WRONG_PARAMETERS_P1P2', 'invalid P1 or P2 field'),
    ERR4 : ErrorCode(ERR4, 'EP_SW_INSTRUCTION_NOT_SUPPORTED', 'command not supported'),
}


class InputMessage():
    def __init__(self, bytesArray):
        self._rawInput = bytesArray
        if tuple(bytesArray[-2:]) in STATUS_CODE:
            self._statusCode   = tuple(bytesArray[-2:])
            self._bytesMessage = tuple(bytesArray[:-2])
        else:
            self._statusCode   = tuple(bytesArray[:2])
            self._bytesMessage = tuple()
        self.log()

    def stringMessage(self):
        return ''.join(chr(c) for c in self._bytesMessage if c!= 0x00)
    
    def bytesMessage(self):
        return self._bytesMessage
    
    def statusCode(self):
        return self._statusCode
    
    def statusOk(self):
        return self._statusCode == OK
    
    def log(self):
        if self._statusCode in STATUS_CODE:
            STATUS_CODE.get(self._statusCode).log()
        else:
            logging.error('Unrecognized status code {}  raw input: {}'.format(self._statusCode, self._rawInput))

class TCMConnection():
    DEVICE_INFO = 'MpicoSys TC-P74-230_v1.1'
    
    def __init__(self, bus=0, device=0, freq=500000):
        logging.info('Initializing TCM Connection. Bus: {}  Device: {}  Freq: {}Hz'.format(bus, device, freq))
        GPIO.setup(BUSY_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUSY_CHANNEL, GPIO.RISING)
        
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        # According to TCM datasheet: Bit rate up to 3 MHz
        # DO NOT GO OVER 500kHz. The TCM is not being able to receive the commands and returns INSTRUCTION_NOT_SUPPORTED most of the time.
        self.spi.max_speed_hz = freq
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
        time.sleep(0.05)  # This little nap avoids communication issues on the firsts messages after setup.
        
        
    def reverseBits(byte):
        """ According to library documentation, spi.lsbfirst might be hardware fixed,
            This method might be of help when changing to another master device. """
        byte = ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)
        byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
        byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
        return byte

    def __del__(self):
        GPIO.remove_event_detect(BUSY_CHANNEL)
        self.spi.close()

    def _waitForBusy(self):
        """ Wait until bussy is off. Abs minimum 28us (T_A+T_BUSY+T_NS).
            It usually takes around 1ms. From time to time it might take up to 15ms.
            Updating the screen takes around 2.5 seconds. """
        timeout = time.time() + 4
        while not GPIO.event_detected(BUSY_CHANNEL):
            if time.time() > timeout:
                logging.warning('Timeout. Busy signal event not detected')
                break

    def _write(self, bytesMessage):
        ''' Writes a byte message through SPI and awaits for
            the busy signal to turn off '''
        self.spi.writebytes(bytesMessage)
        self._waitForBusy()
        
    def _readMessage(self,length):
        bytesArray = self.spi.readbytes(length)
        return InputMessage(bytesArray)
        
    def _askDeviceInfo(self):
        logging.info('Getting device info')
        self._write(GET_DEVICE_INFO)
        message = self._readMessage(len(self.DEVICE_INFO)+1+2)
        return message
    
    def deviceInfo(self):
        return self._askDeviceInfo().stringMessage()
            
    def _askDeviceId(self):
        logging.info('Getting device ID')
        self._write(GET_DEVICE_ID)
        message = self._readMessage(20+2)
        return message
    
    def deviceId(self):
        return self._askDeviceId().bytesMessage()
    
    def resetDataPointer(self):
        logging.info('Reseting Data Pointer')
        self._write(RESET_DATA_POINTER)
        message = self._readMessage(2)
        return message.statusOk()

    def displayUpdate(self):
        logging.info('Updating Display')
        self._write(DISPLAY_UPDATE)
        message = self._readMessage(2)
        return message.statusOk()

    def _writeImageData(self, byteArray, attempts=10):
        '''The command uploads image data (in EPD file format)
           to TCon image memory. The data needs to be divided
           into packets and transferred with multiple calls to
           this command.
           
           byteArray: EPD formated image packet. Max Size: 250
           
           '''
        for attempt in range(attempts):
            self._write(WRITE_TO_SCREEN + (len(byteArray),) + tuple(byteArray))
            message = self._readMessage(2)
            if message.statusOk():
                break
            logging.warning('Writing attempt {}/{} failed'.format(attempt+1, attempts) )
        return message.statusOk()
    
    def writeHeader(self):
        return self._writeImageData(EDP_HEADER)

    def verifyConnection(self):
        logging.info('Verifying TCM connection')
        message = self._askDeviceInfo()
        return message.statusOk()

    def writeFullScreen(self, byteArray ):
        self.resetDataPointer()
        self.writeHeader()
        for ix in range(0, len(byteArray), 250):
            self._writeImageData(byteArray[ix:ix+250])
        self.displayUpdate()        

    def whiteScreen(self):
        self.writeFullScreen((0x00,)*(SCREEN_WIDTH*SCREEN_HEIGHT//8))

    def dopplerScreen(self):
        byteArray = []
        WHITE_LINE = (0x00,)*60
        BLACK_LINE = (0xFF,)*60
        for _ in range(2):
            for growing in range(1,20,2):
                for witdh in range(growing):
                    byteArray.extend(BLACK_LINE)
                for witdh in range(growing+1):
                    byteArray.extend(WHITE_LINE)
            for decreacing in range(19,1,-2):
                for witdh in range(decreacing):
                    byteArray.extend(BLACK_LINE)
                for witdh in range(decreacing-1):
                    byteArray.extend(WHITE_LINE)
            byteArray.extend(BLACK_LINE)
        self.writeFullScreen(tuple(byteArray))
        
    def polarPatternScreen(self, coorCallback, centered=True):
        dx, dy = (0, 0)
        if centered:
            dx, dy = ( -SCREEN_WIDTH//2, -SCREEN_HEIGHT//2 )
        bitArray = []
        for x in range(dx, SCREEN_WIDTH + dx):
            for y in range(dy, SCREEN_HEIGHT + dy):
                if coorCallback(x, y):
                    bitArray.append(1)
                else:
                    bitArray.append(0)
        byteArray = bitsToFormatType4bytes(bitArray)
        self.writeFullScreen(tuple(byteArray))
    
    def coolCirclePatternScreen(self):
        self.polarPatternScreen(lambda x, y: (x**3+y**3) % 500000 > 120000)
        
    def bibrationPatternScreen(self):
        from math import sin, pi
        self.polarPatternScreen(lambda x, y: 100*(sin(7*pi*x/SCREEN_WIDTH) + sin(4*pi*y/SCREEN_HEIGHT)) %20 > 15, centered=False)
        
if __name__ == "__main__":
    conn = TCMConnection()
    print("Connected:", conn.verifyConnection())
    print("Device Id:", conn.deviceId())
    conn.bibrationPatternScreen()
    print("Done\n")
