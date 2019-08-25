import time

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{} function took {:0.3f} ms'.format(f, (time2-time1)*1000.0))
        return ret
    return wrap

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def bits2bytes(array):
    return [ sum(v<<i for i, v in enumerate((chunk[::-1])))
             for chunk in chunker(array, 8)]

def bitsToFormatType4bytes(bitsArray):
    newArray = [0 for _ in range(len(bitsArray)//8)]
    row = 30
    s = 1
    for i in range(0,len(bitsArray),16):
        newArray[row-s] = ( ( ( bitsArray[i+6 ] & 0x01 ) << 7 ) |
                            ( ( bitsArray[i+14] & 0x01 ) << 6 ) |
                            ( ( bitsArray[i+4 ] & 0x01 ) << 5 ) |
                            ( ( bitsArray[i+12] & 0x01 ) << 4 ) |
                            ( ( bitsArray[i+2 ] & 0x01 ) << 3 ) |
                            ( ( bitsArray[i+10] & 0x01 ) << 2 ) |
                            ( ( bitsArray[i+0 ] & 0x01 ) << 1 ) |
                            ( ( bitsArray[i+8 ] & 0x01 ) ) )

        newArray[row+30-s] = ( ( ( bitsArray[i+1 ] & 0x01 ) << 7 ) |
                               ( ( bitsArray[i+9 ] & 0x01 ) << 6 ) |
                               ( ( bitsArray[i+3 ] & 0x01 ) << 5 ) |
                               ( ( bitsArray[i+11] & 0x01 ) << 4 ) |
                               ( ( bitsArray[i+5 ] & 0x01 ) << 3 ) |
                               ( ( bitsArray[i+13] & 0x01 ) << 2 ) |
                               ( ( bitsArray[i+7 ] & 0x01 ) << 1 ) |
                               ( ( bitsArray[i+15] & 0x01 ) ) )
        s+=1
        if s==31:
            s=1
            row+=60
    return newArray
        