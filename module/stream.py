import cv2
import socketio

class SocketClient:
    def __init__ (self):
        self.sio = socketio.Client()
        self.sio.connect('http://127.0.0.1:3000',
                    auth = {
                        'token': "010818064018thilamthidang"
                    })
        self.is_stream = True

        @self.sio.on('start')
        def startStream ():
            print('statr')
            self.is_stream = True

        @self.sio.on('stop')
        def stopStream ():
            print('stop')
            self.is_stream = False

    def send_frame_to_server (self, frame):
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            self.sio.emit('frame_from_camera', buffer.tobytes())
        except Exception as e:
            print(f'Error: {e}')