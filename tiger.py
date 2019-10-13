from TCMDriver import TCMConnection
from PIL import Image, ImageOps
from utils import bitsToFormatType4bytes

conn = TCMConnection()
v1 = Image.open('/home/pi/Documents/eink/tiger.bmp')
v2 = ImageOps.invert(v1.convert('RGB'))
v3 = v2.convert('1')
v4 = v3.transpose(Image.ROTATE_270)
d = list(v4.getdata())
byteArray = bitsToFormatType4bytes(d)
conn.writeFullScreen(tuple(byteArray))
