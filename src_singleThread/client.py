#! /usr/bin/env python3
import socket, sys, re, os
from io import BufferedReader, FileIO
sys.path.append("../lib")       # for params
import params

sys.path.append("../Archiver")  # for Archiver
from create import outBandCreate


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),    # default 127.0.0.1:50001  -s --sever give a server
    (('-?', '--usage'), "usage", False), # boolean (set if present)    -? and --usage prints out how to use this program
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]  # maps param name to value

if usage:
    params.usage()       # Prints out message

try:
    serverHost, serverPort = re.split(":", server)  # split server on colon, get IP address, get name of server
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)


s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM): # Tell is the host, server,socket.AF_UNSPE -> tell me if it is IPv4 or IPv6
    af, socktype, proto, canonname, sa = res   # address family, server address a tuple of address and port number
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto) # proto -> TCP as protocol for strings
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))  # repr representation
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break


if s is None:
    print('could not open socket')
    sys.exit(1)

filesIN = []  # Store files

for i in range(0, len(sys.argv)):
    filesIN.append(sys.argv[i])

print("Framing message...")
outMessage = outBandCreate(filesIN)

print("Sending files...")
while len(outMessage):

    print("Sending '%s'" % outMessage)
    byteSent = os.write(s.fileno(), outMessage)
    outMessage = outMessage[byteSent:]

s.shutdown(socket.SHUT_WR)

while True:
    data = os.read(s.fileno(), 1024).decode()

    if len(data) == 0:
        print("Zero length read. Closing")
        break
    print("Received '%s'" % data)


s.close()