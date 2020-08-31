import unittest
from ESP8266Driver import ESP8265
from time import sleep

class test_ESP8265(unittest.TestCase):
    def setUp(self):
        self.con = ESP8265()
        
    def assertNoResidualMessages(self):
        sleep(1)
        residual = self.con._read()
        self.assertEqual(residual, [])
    
    def test_ATCommandReturnsOK(self):
        ans = self.con.blockingWrite('AT')
        expectedAnswer = ['AT',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        
    @unittest.skip('overcovered by other tests')
    def test_canReset(self):
        ans = self.con.reset()
        self.assertEqual(ans[0], 'AT+RST')
        self.assertIn('OK', ans[2:4])
        self.assertEqual(ans[-1], 'ready')
        self.assertNoResidualMessages()
        
    @unittest.skip('overcovered by other tests')
    def test_canSetWiFiModeToClient(self):
        ans = self.con.setWifiModeToClient()
        expectedAnswer = ['AT+CWMODE_CUR=1',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        
    @unittest.skip('overcovered by other tests')
    def test_canConnectToMobileHotspot(self):
        self.con.reset()
        self.con.setWifiModeToClient()
        ans = self.con.wifiConnect( 'Nahuel Android', '66666666' )
        expectedAnswer = ['AT+CWJAP_CUR="Nahuel Android","66666666"',
                          'WIFI CONNECTED',
                          'WIFI GOT IP',
                          '',
                          'OK']
        self.assertEqual(ans, expectedAnswer)
        self.assertNoResidualMessages()
        
    def test_canRetrieveGoogleHomePage(self):
        self.con.reset()
        self.con.setWifiModeToClient()
        self.con.wifiConnect( 'Nahuel Android', '66666666' )
        self.con.establishTCPConnection( 'www.google.com' )
        ans = self.con.getRequest( '/' )
        self.assertGreater(sum(len(x) for x in ans), 2000)
        self.assertNoResidualMessages()
        

if __name__ == '__main__':
    unittest.main()