#! /usr/bin/env python3
import socket, sys, re

sys.path.append("../lib")  # for params
import params
import io

sys.path.append("../Archiver")  # for Archiver
from extract import outBandExtract

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''  # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)  # allow only one outstanding request

conn, addr = s.accept()  # wait until incoming connection request (and accept it)
print('Connected by', addr)

while True:
    data = conn.recv(1024)

    if len(data) == 0:
        print("Zero length read, nothing to send, terminating")
        break

    extractedFilesMsg = outBandExtract(data)

    for fileInfo in extractedFilesMsg:
        sendMsg = b"\nEchoing "
        sendMsg += b"\nFile name: " + fileInfo['name'].encode()
        sendMsg += b"\nFile size: " + str(fileInfo['size']).encode()
        sendMsg += b"\nFile contents: " + fileInfo['contents'].encode()

        data = "\nFile name: " + fileInfo['name'] + "\nFile size: " + str(fileInfo['size']) + "\nFile contents: " + \
               fileInfo['contents']
        print("Received \n'%s', \nsending \n'%s'" % (data, sendMsg))

        while len(sendMsg):
            bytesSent = conn.send(sendMsg)
            sendMsg = sendMsg[bytesSent:0]

        data = ""
conn.shutdown(socket.SHUT_WR)
conn.close()