from module.control_servo import ControlServo
from module.getCamera import FromCamera
# from module.stream import SocketClient
# from module import warning_process
from module import processor
import time
import threading
import cv2

# State have 3 form: scanning - checking - shooting
state = 'scanning'

check_time = time.time()
wait_check_time = 0.5

delay_time = time.time()

last_x = 70
last_y = 58

real_x = 70
real_y = 50

angle_x = 0
angle_y = 0

pump = 0

cam_width = 640
cam_height = 480
camera = FromCamera(width=cam_width, height=cam_height)

servo_control = ControlServo()

def autoMode():
    global last_x, last_y, check_time, state
    x, y = last_x, last_y
    direction = 1
    while True:
        if state == "scanning":
            check_time = time.time()
            
            x += (10 * direction)
            servo_control.send_angle(x, y, 0)
            if x <= 30 or x >= 110: direction *= -1
            
            last_x = x
            last_y = y
            
            time.sleep(0.5)
        else: 
            time.sleep(2)
auto = threading.Thread(target=autoMode)
auto.start()

print("Starting main...")

while True:
    frame = camera.get_image()

    boxes, info = camera.detect_fire(frame)

    if boxes != []:
        center_targets = processor.get_center_target(boxes)
        
        angle_x, angle_y, pump = processor.cal_degree(center_targets, cam_width, cam_height, angle_x, angle_y)
        
        for target in center_targets:
            cv2.circle(frame, ( target[0], target[1]), 5, (255, 0, 0), -1)

        if state != "checking" and state != "shooting":
            state = "checking"
        
        if state == "checking":
            if time.time() - check_time >= wait_check_time:
                state = "shooting"
                real_x = last_x
                real_y = last_y
            
        elif state == "shooting":
            check_time = time.time()
            
            if time.time() - delay_time >= 0.5:
                delay_time = time.time()
                
                # if int(angle_x) <= 1 and int(angle_x) >= -1:
                #     real_x += angle_x
                #     real_y += angle_y
                # else:
                #     real_x += angle_x
                #     real_y = last_y
                
                real_x += angle_x
                real_y += angle_y
                
                if pump == 1: real_y += 2
                servo_control.send_angle(real_x, real_y, pump)
                print(angle_x, angle_y)
    elif (state != "scanning") and (time.time() - check_time >= wait_check_time):
            state = "scanning"


    camera.draw_bounding_boxes(frame, info)
    
    camera.draw_centers_points(frame)
    
    camera.show_image(frame)
    
    print("state: ", state)