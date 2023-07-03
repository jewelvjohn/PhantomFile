import os
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9999))

file_name = "file.mp4"

file = open(file_name, "rb")
file_size = os.path.getsize(file_name)

reciever_file = "PhantomFile_" + file_name

client.send(reciever_file.encode())
client.send(str(file_size).encode())

data = file.read()
client.sendall(data)
client.send(b"<#END#>")

file.close()
client.close()