#! /usr/bin/env python3
import socket, sys, re, os, time
import threading
sys.path.append("../lib")       # for params
import params

sys.path.append("../Archiver")  # for Archiver
from extract import outBandExtract


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

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
listenSock.listen(5)              # allow only one outstanding request

print("Listening on: ", listenSock)


transferred_files = "received"

transferred_files_set = set()       # Also keep track of files names
transferred_files_lock = threading.Lock()


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

# Server code to be run by each thread
def handle_client(connSockAddr):
    sock, addr = connSockAddr

    print(f'Thread: {threading.current_thread().name} connected to client at {addr}')

    data = sock.recv(1024)

    if len(data) == 0:
        print("Zero length read, nothing to send, terminating")
        return

    extractedFilesMsg = outBandExtract(data)

    for fileInfo in extractedFilesMsg:

        with transferred_files_lock:
            if fileInfo['name'] in transferred_files_set:

                msg = f"File '{fileInfo['name']}' previously transferred by another client."
                sock.send(msg.encode())
                continue

            if not save_file(fileInfo['name'], fileInfo['contents']):
                extractedFilesMsg.remove(fileInfo)
                continue

            transferred_files_set.add(fileInfo['name'])

        data = "\nFile name: " + fileInfo['name'] + "\nFile size: " + str(fileInfo['size']) + "\nFile contents: " + fileInfo['contents']
        sock.send(data.encode())
        time.sleep(0.25)  # Delay 1/4s

    sock.shutdown(socket.SHUT_WR)
    sock.close()  # Close the connection
    print(f'Thread: {threading.current_thread().name} terminated')


os.makedirs(transferred_files, exist_ok=True)

while True:
    try:
        connSockAddr = listenSock.accept()  # accept connection from a new client
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(connSockAddr,))
        client_thread.start()
    except TimeoutError:
        connSockAddr = None
    except Exception as e:
        print(f'Error accepting connection: {e}')