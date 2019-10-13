link = 'https://a0e41fa6.ngrok.io/img-download/'
import requests
print('downloading img')
img = requests.get(link)
print('img downloaded')
f = open('myDownloadedImg.png', 'wb+')
f.write(img.content)
f.close()
print('img saved')
