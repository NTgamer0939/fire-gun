import time

from module import control_servo

servo = control_servo.ControlServo()

# while True:
#     servo.send_angle(40, 40, 1)
#     time.sleep(1)
#     servo.send_angle(40, 40, 0)
#     time.sleep(1)

# servo.send_angle(40, 40, 0)


servo.send_angle(40, 40, 1)
time.sleep(1)
servo.send_angle(40, 40, 0)