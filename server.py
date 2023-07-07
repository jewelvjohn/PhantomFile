import socket

def receive_file(save_path, server_host, server_port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Bind the socket to a specific address and port
        server_socket.bind((server_host, server_port))
        print(f"Server started on {server_host}:{server_port}")
        
        # Listen for incoming connections
        server_socket.listen(1)
        
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Connected to client at {client_address[0]}:{client_address[1]}")
        
        # Open a file to write the received data
        with open(save_path, 'wb') as file:
            # Receive the file data in chunks
            chunk = client_socket.recv(1024)
            
            # Write the received data to the file
            while chunk:
                file.write(chunk)
                chunk = client_socket.recv(1024)
        
        print("File received successfully.")
    
    finally:
        # Close the client socket
        client_socket.close()
        
        # Close the server socket
        server_socket.close()

# Usage example
save_path = 'path/to/save/file.txt'
server_host = '127.0.0.1'  # Replace with the server's IP address
server_port = 12345  # Replace with the server's port

receive_file(save_path, server_host, server_port)