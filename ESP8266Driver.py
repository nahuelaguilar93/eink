import serial
import io
import time
import logging
from config import NGROK_LINK
logging.basicConfig( format = '%(asctime)s [%(levelname)s] %(message)s',
                     level  = logging.DEBUG )

class ESP8265():
    def __init__( self ):
        self.serial = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.3 )
        self._link = None

    def _read( self, decodeLecture = True, terminator = None ):
        i = 0
        while i < 300:
            if self.serial.inWaiting() > 0:
                break;
            time.sleep( 0.01 )
            logging.debug( 'waiting... {}'.format( i ) )
            i += 1
        else:
            return []
        lines = self.serial.readlines( )
        #lines = []
        #def safeDecode(x):
        #    try:
        #        return x.decode( 'utf-8' )
        #    except:
        #        logging.info('Failed to decode line')
        #        return x
        #while not lines or lines[-1] not in ['ready', 'OK', 'ERROR']:
        #    lines.append(safeDecode(self.serial.readline( )).strip('\r\n'))
        #    logging.debug('incoming line: {}'.format(lines[-1]))
        if not decodeLecture:
            logging.info('retrieving {} non decoded lines'.format(len(lines)))
        
        decodedLines = []        
        for line in lines:
            try:
                decodedLine = line.decode( 'utf-8' ).rstrip('\n').rstrip('\r')
                logging.info( decodedLine )
                decodedLines.append( decodedLine )
            except:
                logging.warning( 'fail to decode line: {}'.format( line ) )
#                decodedLines.append( line )
        return decodedLines 

    def blockingWrite( self, string, terminator = "\r\n", decodeLecture = True ):
        self.serial.write( bytes( string + terminator, 'utf-8' ) )
        lecture = self._read( decodeLecture = decodeLecture )
        return lecture
    
    def _verifyNotBussy( self ):
        return True

    def __del__( self ):
        self.serial.close()
        
    def reset( self ):
        logging.info( 'Reseting Board' )
        ans = self.blockingWrite( 'AT+RST' )
        while ans[-1] != 'ready':
            ans += self._read()
        return ans

    def factoryReset( self ):
        logging.info( 'Applying Factory Reset to Board' )
        return self.blockingWrite( 'AT+RESTORE' )

    def setWifiModeToClient( self ):
        logging.info( 'Setting WiFi Mode to client' )
        return self.blockingWrite( 'AT+CWMODE_CUR=1' )

    def wifiConnect( self, ssid, pwd ):
        logging.info( 'Connecting to Access Point: {}'.format( ssid ) )
        response = self.blockingWrite( 'AT+CWJAP_CUR="{}","{}"'.format( ssid, pwd ) )
        while response[-1] != 'OK':
            response += self._read( decodeLecture = True )
        return response
        
    def establishTCPConnection( self, link, port=80 ):
        link       = link.rstrip( '/' )
        self._link = link
        logging.info( 'Establishing TCP Connection: {}'.format( link ) )
        return self.blockingWrite( 'AT+CIPSTART="TCP","{}",{}'.format( link, port ) )

    def getRequest( self, request ):
        message = 'GET {}{} HTTP/1.1\r\n\r\n\r\n'.format( self._link, request )
        #logging.info( 'Sending request: {} | len {}'.format( message, len( message ) ) )
        self.blockingWrite( 'AT+CIPSEND={}'.format( len( message ) ) )
        return self.blockingWrite( message, terminator = '', decodeLecture = False )
        
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
    esp.establishTCPConnection( 'eink.pagekite.me' )
    response = esp.getRequest( '/aula115/time_till_wake_up' )
    return int(response[-1].decode('utf-8').strip('\r\n').strip('CLOSED'))

def getImageData(esp, raw = False):
    esp.establishTCPConnection( 'eink.pagekite.me' )
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
