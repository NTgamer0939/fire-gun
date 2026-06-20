import socket
import time

class ControlServo:
    # def __init__(self, host='10.42.140.189', port=12345):
    def __init__(self, host='192.168.137.1', port=12345):
    # def __init__(self, host='169.254.51.48', port=12345):
    # def __init__(self, host='10.15.111.189', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on port {self.port}...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected by {self.addr}")
        self.wait_time = time.time()
        
    def send_command(self, command):
        if ('!' in command) and (time.time() - self.wait_time < 0.3): return
        if not command.endswith('\n'):
            command += '\n'
        print(f"Sending command: {command.strip()}")
        try:
            self.conn.sendall(command.encode())
        except Exception as e:
            print(f"Error sending command: {e}")
            self.server_socket.listen(1)
            self.conn, self.addr = self.server_socket.accept()
    
    def send_angle(self, angle_x, angle_y, pump):
        command = f"{angle_x}!{angle_y}!{pump}!\n"
        self.send_command(command)