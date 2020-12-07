import unittest
from ESP8266Driver import ESP8265
from config import NGROK_LINK
from time import sleep
import logging
from pprint import pprint

class test_ESP8265_Basics(unittest.TestCase):
    def setUp(self):
        logging.info("[TEST] Running Test {}".format(self._testMethodName))
        self.con = ESP8265()
        
    def assertNoResidualMessages(self):
        logging.warning('[TEST] Timeout Warning Log Expected in next line.')
        residual = self.con._read(timeout = 3)
        self.assertEqual(residual, [])
    
    def test_ATCommandReturnsOK(self):
        ans = self.con.blockingWrite('AT')
        expectedAnswer = ['AT',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        
    def test_badCommandReturnsError(self):
        ans = self.con.blockingWrite('AT+QWERTY')
        expectedAnswer = ['AT+QWERTY',
                          '',
                          'ERROR']
        self.assertEqual(ans, expectedAnswer)
        
    def test_canReset(self):
        ans = self.con.reset()
        self.assertEqual(ans[0], 'AT+RST')
        self.assertIn('OK', ans[2:4])
        self.assertEqual(ans[-1], 'ready')
        self.assertNoResidualMessages()
        
    def test_canSetWiFiModeToClient(self):
        ans = self.con.setWifiModeToClient()
        expectedAnswer = ['AT+CWMODE_CUR=1',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        
class test_ESP8265_Connection(test_ESP8265_Basics):

    def resetAndConnectHotspot(self):
        self.con.reset()
        self.con.setWifiModeToClient()
        return self.con.wifiConnect( 'Nahuel Android', '66666666' )

    def assertNoBadRequest(self, ans):
        self.assertFalse(any(b'400 Bad Request' in x for x in ans))

    def test_canConnectToMobileHotspot(self):
        ans = self.resetAndConnectHotspot()
        expectedAnswer = ['AT+CWJAP_CUR="Nahuel Android","66666666"',
                          'WIFI CONNECTED',
                          'WIFI GOT IP',
                          '',
                          'OK']
        for expectedLine in expectedAnswer:
            self.assertIn(expectedLine, ans)
        self.assertNoResidualMessages()
        
    def test_canConnectToGoogle(self):
        self.resetAndConnectHotspot()
        ans = self.con.establishTCPConnection( 'www.google.com' )
        expectedAnswer = ['AT+CIPSTART="TCP","www.google.com",80',
                          'CONNECT',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        self.assertNoResidualMessages()
        
    def test_canRetrieveGoogleHomePage(self):
        self.resetAndConnectHotspot()
        self.con.establishTCPConnection('www.google.com')
        ans = self.con.getRequest( '/' )
        self.assertNoBadRequest(ans)
        self.assertGreater(sum(len(x) for x in ans), 2000)
        self.assertNoResidualMessages()
        
    def test_canRetrieveFromMyNgrokServer(self):
        self.resetAndConnectHotspot()
        self.con.establishTCPConnection(NGROK_LINK.split('://')[-1])
        ans = self.con.getRequest('/')
        pprint(ans)
        self.assertNoBadRequest(ans)
        self.assertTrue(any(b'Hello Woooooorld!' in x for x in ans))
        self.assertNoResidualMessages()
    
    def test_canRetrieveSleepTimeFromServer(self):
        self.resetAndConnectHotspot()
        self.con.establishTCPConnection(NGROK_LINK.split('://')[-1])
        ans = self.con.getRequest('/aula115/time_till_wake_up')
        pprint(ans)
        self.assertNoBadRequest(ans)
        self.assertTrue(any(b'10' in x for x in ans))
        self.assertNoResidualMessages()
        
    def test_canRetrieveImageFromServer(self):
        self.resetAndConnectHotspot()
        self.con.establishTCPConnection(NGROK_LINK.split('://')[-1])
        ans = self.con.getRequest('/aula115/digested_image')
#        pprint(ans)
        self.assertNoBadRequest(ans)
        self.assertGreater(sum(len(x) for x in ans), 2000)
        self.assertNoResidualMessages()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
#    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(test_ESP8265_Connection("test_badCommandReturnsError"))
#    suite.addTest(test_ESP8265_Connection("test_canRetrieveImageFromServer"))
    runner = unittest.TextTestRunner()
    runner.run(suite)