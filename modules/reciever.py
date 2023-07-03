import socket
import tqdm

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))
server.listen()
client, addr = server.accept()

file_name = client.recv(1024).decode()
print(file_name)
file_size = client.recv(1024).decode()
print(file_size)

done = False

progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))

while not done:
    data = client.recv(1024)
    if data[-7:] == b"<#END#>":
        done = True
    else:
        with open(file_name, 'ab') as file:
            file.write(data)
    progress.update(1024)

client.close()
server.close()