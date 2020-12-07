#f = open("sampleScreen.txt", "rb")
#raw = f.read()
#acefalus = raw.split(b'\r\n\r\n',3)[-1]
#clean = b''
#for x in acefalus.split(b'+IPD'):
#    if x[-2:] == b'\r\n':
#        clean += x[x.find(b':')+1:-2]
#    else:
#        clean += x[x.find(b':')+1:]
#print(len(clean))
#
#lz = 60
#sampleLines = []
#for x in range(24000,24000+lz*50,lz):
#    sampleLines.append(clean[x:x+lz])
    
import serial
import time

f = open("sampleScreen.txt", "rb")
raw = f.read()
s = serial.Serial( "/dev/ttyS0", baudrate=115200, timeout=0.3 )    

i=0
while True:
    if not s.inWaiting():
        if not i%100:
            print( 'waiting... {}'.format(i) )
        i+=1
        time.sleep( 0.1 )
        continue
    line = s.readlines()
    print(line)
    if line[0] == b'send me the image\n':
        for x in range(0, len(raw), 5000):
            s.write( raw[x:x+5000] )
            print( 'sending... {}'.format(x) )
            time.sleep( 0.4 )
            i += 1000000000
    else:
        s.write(b'qfeargaegaegasfasdf'*2000)
