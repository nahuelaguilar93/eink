import serial
import io
import time
import logging
logging.basicConfig( format = '%(asctime)s [%(levelname)s] %(message)s',
                     level  = logging.DEBUG )

class ESP8265():
    def __init__( self ):
        self.serial = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=5.0 )
        self._link = None

    def _read( self, decodeLecture = True ):
        i = 0
        while True:
            if self.serial.inWaiting() > 0:
                break;
            time.sleep( 0.001 )
            logging.debug( 'waiting... {}'.format( i ) )
            i += 1
        lines = self.serial.readlines( )
        if not decodeLecture:
            logging.info('retrieving {} non decoded lines'.format(len(lines)))
            return lines

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

    def _blockingWrite( self, string, terminator = "\r\n", decodeLecture = True ):
        self.serial.write( bytes( string + terminator, 'utf-8' ) )
        lecture = self._read( decodeLecture = decodeLecture )
        return lecture
    
    def _verifyNotBussy( self ):
        return True

    def __del__( self ):
        self.serial.close()
        
    def reset( self ):
        logging.info( 'Reseting Board' )
        return self._blockingWrite( 'AT+RST' )

    def factoryReset( self ):
        logging.info( 'Applying Factory Reset to Board' )
        return self._blockingWrite( 'AT+RESTORE' )

    def setWifiModeToClient( self ):
        logging.info( 'Setting WiFi Mode to client' )
        return self._blockingWrite( 'AT+CWMODE_CUR=1' )

    def wifiConnect( self, ssid, pwd ):
        logging.info( 'Connecting to Access Point: {}'.format( ssid ) )
        return self._blockingWrite( 'AT+CWJAP_CUR="{}","{}"'.format( ssid, pwd ) )
        
    def establishTCPConnection( self, link, port=80 ):
        link       = link.rstrip( '/' )
        self._link = link
        logging.info( 'Establishing TCP Connection: {}'.format( link ) )
        return self._blockingWrite( 'AT+CIPSTART="TCP","{}",{}'.format( link, port ) )

    def getRequest( self, request ):
        message = 'GET {}{} HTTP/1.0\r\n\r\n\r\n'.format( self._link, request )
        logging.info( 'Sending request: {} | len {}'.format( message, len( message ) ) )
        self._blockingWrite( 'AT+CIPSEND={}'.format( len( message ) ) )
        return self._blockingWrite( message, terminator = '', decodeLecture = False )
        
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
    esp.wifiConnect( 'PochiNet 0.5', 'prohibidofumar247' )
    #esp.wifiConnect( 'Nahuel Android', '66666666' )
    return esp

def getTimeToSleep(esp):
    esp.establishTCPConnection( 'http://750ba94f.ngrok.io' )
    response = esp.getRequest( '/aula115/time_till_wake_up' )
    return int(response[-1].decode('utf-8').strip('\r\n').strip('CLOSED'))

def getImageData(esp):
    esp.establishTCPConnection( 'http://750ba94f.ngrok.io' )
    b = esp.getRequest( '/aula115/digested_image' )
    toStrip = ['\r\n','CLOSED','+IPD,1460:','+IPD,1437:']
    for stripIt in toStrip:
        b = [stripBytes(x, stripIt) for x in b]
    q = bytes('','utf-8')    
    for t in range(11, len(b)):
        q += b[t]
    return q

def demo():
    esp = getConnection()
    q = getImageData(esp)
    from TCMDriver import TCMConnection
    TCMConnection().writeFullScreen(q[:48000])
