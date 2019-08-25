import unittest
from utils import bits2bytes

class Test_bits2bytes( unittest.TestCase ):
    def test_bits2bytes( self ):
        bits = [1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1]
        expectedBytes = [0x9A, 0x0D]
        byteArray = bits2bytes(bits)
        self.assertEqual(byteArray, expectedBytes)
        
