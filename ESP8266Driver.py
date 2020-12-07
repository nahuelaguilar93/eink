import serial
import io
import time
import logging
from pprint import pprint
from config import NGROK_LINK
logging.basicConfig( format = '%(asctime)s [%(levelname)s] %(message)s',
                     level  = logging.DEBUG )

class ESP8265():
    
    DEFAULT_READ_TIMEOUT = 5
    
    def __init__( self ):
        self.serial = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.3 )
        self._link = None

    def _read( self, decodeLecture = True, timeout = None, enders = None, quickExit = True ):
        lines = []
        timeout = timeout or self.DEFAULT_READ_TIMEOUT
        enders = enders or []
        t = time.time()
        while time.time()-t < timeout:
            if ((enders and any(x in lines for x in enders)) or (not enders and lines and quickExit)):
                return lines
            if not self.serial.inWaiting():
                logging.debug( 'waiting...' )
                time.sleep( 0.1 )
                continue
            time.sleep( 0.1 )
            t = time.time()
            undecodedLines = self.serial.readlines()
            if not decodeLecture:
                logging.info('retrieving {} non decoded lines'.format(len(undecodedLines)))
                lines += undecodedLines
            else:
                lines += self.decodeLines(undecodedLines)
        else:
            logging.warning('Read operation timeout! Waiting for too long.')
            return lines

    @staticmethod
    def decodeLines(lines):
        decodedLines = []
        for line in lines:
            try:
                decodedLine = line.decode( 'utf-8' ).rstrip('\n').rstrip('\r')
                logging.info( '[REC] ' + line.decode('utf-8').encode('unicode_escape').decode('utf-8') )
                decodedLines.append( decodedLine )
            except:
                logging.warning( 'fail to decode line: {}'.format( line ) )
#                decodedLines.append( line )
        return decodedLines 

    def blockingWrite( self, string, terminator = "\r\n", decodeLecture = True, timeout = None, enders = None, quickExit = True ):
        logging.info( '[SEND] ' + (string + terminator).encode('unicode_escape').decode('utf-8') )
        self.serial.write( bytes( string + terminator, 'utf-8' ) )
        lecture = self._read( decodeLecture = decodeLecture, timeout = timeout, enders = enders, quickExit = quickExit )
        return lecture
    
    def _verifyNotBussy( self ):
        return True

    def __del__( self ):
        self.serial.close()
        
    def reset( self ):
        logging.info( 'Reseting Board' )
        response = self.blockingWrite( 'AT+RST',
                                       timeout = 5,
                                       enders = ['ready'] )
        return response

    def factoryReset( self ):
        logging.info( 'Applying Factory Reset to Board' )
        return self.blockingWrite( 'AT+RESTORE' )

    def setWifiModeToClient( self ):
        logging.info( 'Setting WiFi Mode to client' )
        return self.blockingWrite( 'AT+CWMODE_CUR=1',
                                   timeout = 5,
                                   enders = ['OK'] )

    def wifiConnect( self, ssid, pwd ):
        logging.info( 'Connecting to Access Point: {}'.format( ssid ) )
        return self.blockingWrite( 'AT+CWJAP_CUR="{}","{}"'.format( ssid, pwd ),
                                   timeout = 30,
                                   enders = ['OK'] )
        
    def establishTCPConnection( self, link, port=80 ):
        link       = link.rstrip( '/' )
        self._link = link
        logging.info( 'Establishing TCP Connection: {}'.format( link ) )
        return self.blockingWrite( 'AT+CIPSTART="TCP","{}",{}'.format( link, port ),
                                   timeout = 30,
                                   enders = ['OK', 'FAIL'] )

    def getRequest( self, request ):
        message = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format( request, self._link )
        logging.info( 'Sending request: {} | len {}'.format( message, len( message ) ) )
        self.blockingWrite( 'AT+CIPSEND={}'.format( len( message ) ) )
        return self.blockingWrite( message, terminator = '', decodeLecture = False, timeout = 5, quickExit = False )
        
def stripBytes(byteIn, stripStr):
    encodedStrip = bytes(stripStr,'utf-8')
    l = len(encodedStrip)
    if byteIn[:l] == encodedStrip:
        byteIn = byteIn[l:]
    if byteIn[-l:] == encodedStrip:
        byteIn = byteIn[:-l]
    return byteIn

def getConnection():
    esp = ESP8265()
    esp.reset()
    #esp.factoryReset()
    esp.setWifiModeToClient()
    #esp.wifiConnect( 'PochiNet 0.5', 'prohibidofumar247' )
    esp.wifiConnect( 'Nahuel Android', '66666666' )
    return esp


def getTimeToSleep(esp):
    esp.establishTCPConnection(NGROK_LINK.split('://')[-1])
    response = esp.getRequest( '/aula115/time_till_wake_up' )
    pprint(response)
    return int(response[-1].decode('utf-8').strip('\r\n').strip('CLOSED'))

def getImageData(esp, raw = False):
    esp.establishTCPConnection(NGROK_LINK.split('://')[-1])
    b = esp.getRequest( '/aula115/digested_image' )
    if raw:
        return b
    toStrip = ['\r\n','CLOSED','+IPD,1460:','+IPD,1437:']
    for stripIt in toStrip:
        b = [stripBytes(x, stripIt) for x in b]
    q = bytes('','utf-8')    
    for t in range(11, len(b)):
        q += b[t]
    return q

# from ESP8266Driver import *

def demo():
    esp = getConnection()
    r = getTimeToSleep(esp)
    print('Time to sleep: ', r)
    q = getImageData(esp, True)
    return q
#    from TCMDriver import TCMConnection
#    TCMConnection().writeFullScreen(q[:48000])
