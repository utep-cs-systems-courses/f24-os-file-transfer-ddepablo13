import os

# Creates tar file similar to command tar c file1 file2... > combined.tar
def outBandCreate(files):
    outMessage = "".encode()

    for file in files:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'textFiles', file.strip())
        if not os.path.exists(file_path):  # Check if path does not exist
            os.write(2, ("File %s does not exist\n" % file).encode())
            exit()

        fdReader = os.open(file_path, os.O_RDONLY)  # Get file reader

        fileByteSize = os.path.getsize(file_path)  # Get file byte size

        fileHeader = f"{file}\n{fileByteSize}\n".encode()  # Store header for file data

        contents = os.read(fdReader, fileByteSize)  # Get byte data

        outMessage += fileHeader
        outMessage += contents

        os.close(fdReader)  # Close when done

    return outMessage