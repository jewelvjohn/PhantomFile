import socket

def send_file(file_path, server_host, server_port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((server_host, server_port))
        print(f"Connected to server at {server_host}:{server_port}")
        
        # Open the file to send
        with open(file_path, 'rb') as file:
            # Read the file in chunks
            chunk = file.read(1024)
            
            # Send the file data in chunks
            while chunk:
                client_socket.send(chunk)
                chunk = file.read(1024)
        
        print("File sent successfully.")
    
    except ConnectionRefusedError:
        print("Could not connect to the server.")
    
    finally:
        # Close the socket
        client_socket.close()

# Usage example
file_path = 'path/to/your/file.txt'
server_host = '127.0.0.1'  # Replace with the server's IP address
server_port = 12345  # Replace with the server's port

send_file(file_path, server_host, server_port)