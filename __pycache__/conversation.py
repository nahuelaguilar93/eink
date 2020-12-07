conversationLog = r'''2020-12-05 00:09:39,926 [INFO] [TEST] Running Test test_canRetrieveImageFromServer
2020-12-05 00:09:39,928 [INFO] Reseting Board
2020-12-05 00:09:39,931 [INFO] [SEND] AT+RST\r\n
2020-12-05 00:09:40,454 [INFO] [REC] AT+RST\r\r\n
2020-12-05 00:09:40,455 [INFO] [REC] \r\n
2020-12-05 00:09:40,456 [INFO] [REC] OK\r\n
2020-12-05 00:09:40,457 [INFO] [REC] CLOSED\r\n
2020-12-05 00:09:40,458 [INFO] [REC] WIFI DISCONNECT\r\n
2020-12-05 00:09:40,459 [INFO] [REC] \r\n
2020-12-05 00:09:40,460 [INFO] [REC]  ets Jan  8 2013,rst cause:1, boot mode:(3,6)\r\n
2020-12-05 00:09:40,461 [INFO] [REC] \r\n
2020-12-05 00:09:40,462 [INFO] [REC] load 0x40100000, len 27728, room 16 \r\n
2020-12-05 00:09:40,463 [INFO] [REC] tail 0\r\n
2020-12-05 00:09:40,464 [INFO] [REC] chksum 0x2a\r\n
2020-12-05 00:09:40,465 [INFO] [REC] load 0x3ffe8000, len 2124, room 8 \r\n
2020-12-05 00:09:40,466 [INFO] [REC] tail 4\r\n
2020-12-05 00:09:40,467 [INFO] [REC] chksum 0x07\r\n
2020-12-05 00:09:40,468 [INFO] [REC] load 0x3ffe8850, len 9276, room 4 \r\n
2020-12-05 00:09:40,469 [INFO] [REC] tail 8\r\n
2020-12-05 00:09:40,470 [INFO] [REC] chksum 0xba\r\n
2020-12-05 00:09:40,471 [INFO] [REC] csum 0xba\r\n
2020-12-05 00:09:40,472 [WARNING] fail to decode line: b'\x8c\xe3\xdcw\x13\xc7\xc1\x8c\x1c\xf3\x1b0\xec\x0c\x18\x80\xec\x1c\r\r\n'
2020-12-05 00:09:40,473 [INFO] [REC] ready\r\n
2020-12-05 00:09:40,474 [INFO] Setting WiFi Mode to client
2020-12-05 00:09:40,475 [INFO] [SEND] AT+CWMODE_CUR=1\r\n
2020-12-05 00:09:40,979 [INFO] [REC] AT+CWMODE_CUR=1\r\r\n
2020-12-05 00:09:40,981 [INFO] [REC] \r\n
2020-12-05 00:09:40,983 [INFO] [REC] OK\r\n
2020-12-05 00:09:40,985 [INFO] Connecting to Access Point: Nahuel Android
2020-12-05 00:09:40,986 [INFO] [SEND] AT+CWJAP_CUR="Nahuel Android","66666666"\r\n
2020-12-05 00:09:41,492 [INFO] [REC] AT+CWJAP_CUR="Nahuel Android","66666666"\r\r\n
2020-12-05 00:09:44,506 [INFO] [REC] WIFI CONNECTED\r\n
2020-12-05 00:09:45,112 [INFO] [REC] WIFI GOT IP\r\n
2020-12-05 00:09:46,419 [INFO] [REC] \r\n
2020-12-05 00:09:46,421 [INFO] [REC] OK\r\n
2020-12-05 00:09:46,423 [INFO] Establishing TCP Connection: b6807f8fcb7c.ngrok.io
2020-12-05 00:09:46,424 [INFO] [SEND] AT+CIPSTART="TCP","b6807f8fcb7c.ngrok.io",80\r\n
2020-12-05 00:09:47,032 [INFO] [REC] AT+CIPSTART="TCP","b6807f8fcb7c.ngrok.io",80\r\r\n
2020-12-05 00:09:47,034 [INFO] [REC] CONNECT\r\n
2020-12-05 00:09:47,035 [INFO] [REC] \r\n
2020-12-05 00:09:47,037 [INFO] [REC] OK\r\n
2020-12-05 00:09:47,039 [INFO] Sending request: GET /aula115/digested_image HTTP/1.1
Host: b6807f8fcb7c.ngrok.io

 | len 69
2020-12-05 00:09:47,040 [INFO] [SEND] AT+CIPSEND=69\r\n
2020-12-05 00:09:47,846 [INFO] [REC] AT+CIPSEND=69\r\r\n
2020-12-05 00:09:47,847 [INFO] [REC] \r\n
2020-12-05 00:09:47,849 [INFO] [REC] OK\r\n
2020-12-05 00:09:47,851 [INFO] [REC] > 
2020-12-05 00:09:47,852 [INFO] [SEND] GET /aula115/digested_image HTTP/1.1\r\nHost: b6807f8fcb7c.ngrok.io\r\n\r\n
2020-12-05 00:09:48,361 [INFO] retrieving 4 non decoded lines
2020-12-05 00:09:54,158 [INFO] retrieving 242 non decoded lines
2020-12-05 00:09:54,561 [WARNING] Read operation timeout! Waiting for too long.
2020-12-05 00:09:54,566 [WARNING] [TEST] Timeout Warning Log Expected in next line.
2020-12-05 00:09:57,578 [WARNING] Read operation timeout! Waiting for too long.'''

for line in conversationLog.split('\n'):
    if '[REC]' in line:
        print('\t' + line.split('[REC] ')[-1])
    if '[SEND]' in line:
        print(line.split('[SEND] ')[-1])
