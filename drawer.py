from TCMDriver import TCMConnection
from ESP8266Driver import ESP8265, getImageData, getTimeToSleep, getConnection
from time import sleep
import logging
logging.basicConfig( format = '%(asctime)s [%(levelname)s] %(message)s',
                     level  = logging.DEBUG )

NGROK_CODE = "750ba94f"

def retrieveData( link ):
    import requests
    response = requests.get(link)
    if response.status_code != 200:
        raise Exception('Error retrieving data.')
    return response.content

def retrieveImgData2():
    DIMG_LINK = 'https://{}.ngrok.io/aula115/digested_image'.format(NGROK_CODE)
    return list(retrieveData(DIMG_LINK))

def retrieveSleepTime():
    esp = ESP8265()
    esp.reset()
    #esp.factoryReset()
    esp.setWifiModeToClient()
    #esp.wifiConnect( 'PochiNet 0.5', 'prohibidofumar247' )
    esp.wifiConnect( 'Nahuel Android', '66666666' )
    esp.establishTCPConnection( 'http://750ba94f.ngrok.io' )
    wawa = esp.getRequest( '/aula115/time_till_wake_up' )
    return int(wawa[-1].strip('CLOSED'))

for iteration in range(3):
    esp = getConnection()
    
    logging.info('retrieving img...')
#    imgData = retrieveImgData()
    imgData = getImageData(esp)
    logging.info('img downloaded.')    

    TCMConnection().writeFullScreen(imgData)
    
    sleepTime = getTimeToSleep(esp)
    logging.info('sleeping for {} seconds...'.format(sleepTime))
    sleep(sleepTime)