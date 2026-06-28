import serial
import time

class ControlServo:
    def __init__(self, COM_PORT='COM3', BAUD_RATE='115200'):
        self.COM_PORT = COM_PORT
        self.BAUD_RATE = BAUD_RATE
        self.wait_time = time.time()
        self.connect_serial()
        
    def connect_serial(self):
        self.ser = serial.Serial(self.COM_PORT, self.BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"[SYSTEM] Opened serial port in {self.COM_PORT} with BAUD_RATE: {self.BAUD_RATE}")
        
    def send_command(self, command):
        if ('!' in command) and (time.time() - self.wait_time < 0.3): return
        if not command.endswith('\n'):
            command += '\n'
        print(f"Sending command: {command.strip()}")
        try:
            self.ser.write(command.encode("utf-8"))
        except Exception as e:
            print(f"Error sending command: {e}")
            self.connect_serial()
    
    def send_angle(self, angle_x, angle_y, pump):
        command = f"{angle_x}!{angle_y}!{pump}!\n"
        self.send_command(command)