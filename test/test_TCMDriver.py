import unittest
from TCMDriver import TCMConnection, InputMessage

class Test_TCMDriver( unittest.TestCase ):
    """ All this tests are expected to be runned with
        the TCM connected as inticated in the TCMDriver.py header."""
    def setUp(self):
        self.conn = TCMConnection()
    
    def test_deviceInfo(self):
        expectedDeviceInfo = self.conn.DEVICE_INFO
        deviceInfo = self.conn.deviceInfo()
        self.assertEqual(deviceInfo, expectedDeviceInfo)
        
    def test_deviceId(self):
        expectedDeviceId = (176, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 43, 16, 50, 37)
        deviceId = self.conn.deviceId()
        self.assertEqual(len(deviceId), 20)
        self.assertEqual(deviceId, expectedDeviceId)
        
        
class Test_InputMessage( unittest.TestCase ):
    def test_stringMessageParsedCorrectly(self):
        testMessage = b'TestMessage'
        fullBytesMessage = list(testMessage) + [0x90, 0x00]
        message = InputMessage(fullBytesMessage)
        self.assertTrue(message.statusOk())
        self.assertEqual(message.bytesMessage(), tuple(testMessage))
        self.assertEqual(message.stringMessage(), testMessage.decode())
        self.assertEqual(message.statusCode(), (0x90, 0x00))

    def test_errorMessageParsedCorrectly(self):
        message = InputMessage([0x67, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.assertFalse(message.statusOk())
        self.assertEqual(len(message.bytesMessage()), 0)
        self.assertEqual(message.statusCode(), (0x67, 0x00))
        
