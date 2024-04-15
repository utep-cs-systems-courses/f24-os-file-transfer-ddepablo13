#! /usr/bin/env python3
import socket, sys, re, os, time

sys.path.append("../lib")  # for params
import params

sys.path.append("../Archiver")  # for Archiver
from extract import outBandExtract

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)

paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''  # Symbolic name meaning all available interfaces

pidAddr = {}  # for active connections: maps pid->client addr

if paramMap['usage']:
    params.usage()

listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# listener socket will unbind immediately on close
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# accept will block for no more than 5s
listenSock.settimeout(5)
# bind listener socket to port
listenSock.bind((listenAddr, listenPort))
# set state to listen
listenSock.listen(1)  # allow only one outstanding request

transferred_files = "received"


#  Save files that were transferred
def save_file(fileName, contents):
    filePath = os.path.join(transferred_files, fileName)

    if os.path.exists(filePath):
        with open(filePath, "rb") as file:
            existing_contents = file.read()

        if existing_contents.decode() != contents:
            print("File exists already and contents are different, removing old file")
            os.remove(filePath)
        else:
            print("Duplicate file")
            return False

    with open(filePath, "wb") as file:
        file.write(contents.encode())

    return True


# Serer code to be run by child
def echoBackToClient(connAddr):
    sock, addr = connAddr
    print(f'Child: pid={os.getpid()} connected to client at {addr}')

    data = sock.recv(1024)

    if len(data) == 0:
        print("Zero length read, nothing to send, terminating")
        return

    extractedFilesMsg = outBandExtract(data)

    for fileInfo in extractedFilesMsg:
        if not save_file(fileInfo['name'], fileInfo['contents']):
            extractedFilesMsg.remove(fileInfo)
            continue
        data = "\nFile name: " + fileInfo['name'] + "\nFile size: " + str(fileInfo['size']) + "\nFile contents: " + \
               fileInfo['contents']
        sock.send(data.encode())
        time.sleep(0.25)  # Delay 1/4s

    sock.shutdown(socket.SHUT_WR)
    sys.exit(0)  # terminate child


os.makedirs(transferred_files, exist_ok=True)
while True:
    # Reap zombie children (if any)
    try:
        while True:
            # Check for exited children (zombies).  If none, don't block (hang)
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:  # No zombie to reap, break the loop
                break
            else:
                print(f"zombie reaped: pid={pid}, status={status}")
                del pidAddr[pid]  # Remove the pid from the active connections
    except ChildProcessError:
        # No child processes
        pass

    print(f"Currently {len(pidAddr.keys())} clients")

    try:
        connSockAddr = listenSock.accept()  # accept connection from a new client
    except TimeoutError:
        connSockAddr = None

    if connSockAddr is not None:  # Check if a client connection was accepted
        forkResult = os.fork()  # fork child for this client

        if forkResult == 0:  # Am child
            listenSock.close()  # child does not need listen socket
            echoBackToClient(connSockAddr)
        # Parent
        sock, addr = connSockAddr
        sock.close()  # parent closes its connection to client
        pidAddr[forkResult] = addr
        print(f"spawned off child with pid = {forkResult} at addr {addr}")
