import io
import os, stat

# Extract from .tar  file into separate files
def outBandExtract(inMessage):

    bytesObjects = io.BytesIO(inMessage)

    buffered_reader = io.BufferedReader(bytesObjects)  # For reading

    filesList = []

    while True:
        fileName = buffered_reader.readline().decode().strip() # Read file name

        if not fileName:
            break

        fileSize = int(buffered_reader.readline().decode().strip()) # Read file size

        fileContents = buffered_reader.readline(fileSize).decode().strip() # Read the contents of that file

        filesInfo = {
            'name' : fileName,
            'size' : fileSize,
            'contents' : fileContents
        }

        filesList.append(filesInfo)         # Store decoded file

    buffered_reader.close() # Close when done

    return filesList