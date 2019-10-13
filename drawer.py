from TCMDriver import TCMConnection
from PIL import Image, ImageOps
from utils import bitsToFormatType4bytes
import requests

link = 'https://a0e41fa6.ngrok.io/aula115/'
print('downloading img')
img = requests.get(link)
# assert response is OK
if img.status_code == 200:
    print('img downloaded')
    f = open('/home/pi/Documents/eink/aula115.png', 'wb+')
    f.write(img.content)
    f.close()
    print('img saved')

conn = TCMConnection()
v1 = Image.open('/home/pi/Documents/eink/aula115.png')
v2 = ImageOps.invert(v1.convert('RGB'))
v3 = v2.convert('1')
v4 = v3.transpose(Image.ROTATE_270)
d = list(v4.getdata())
byteArray = bitsToFormatType4bytes(d)
conn.writeFullScreen(tuple(byteArray))
