from config import NGROK_LINK
link = NGROK_LINK+'/img-download/'
import requests
print('downloading img')
img = requests.get(link)
print('img downloaded')
f = open('myDownloadedImg.png', 'wb+')
f.write(img.content)
f.close()
print('img saved')
