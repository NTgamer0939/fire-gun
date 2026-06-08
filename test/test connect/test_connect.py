# server.py
import socket

HOST = ''
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server lắng nghe tại cổng {PORT}...")

conn, addr = server_socket.accept()
print(f"ESP32 kết nối từ {addr}")   
first_command = "90!45!0!\n"
conn.sendall(first_command.encode())
    
while True:
    # Gửi lệnh điều khiển liên tục (có thể lấy từ input, file hoặc UI)
    command = input("Nhập lệnh (vd: 0!90!): ") + "\n"
    conn.sendall(command.encode())