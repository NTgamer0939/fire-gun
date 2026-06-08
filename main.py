from module.get_image import get_image_from_camera
from module.calc_position import PositionCalculator
from module.control_servo import ControlServo
from module import warning_process
import time
import threading

def start():
    print("Starting main...")
    # Initialize parameters
    P = 0.006
    I = 0.00
    D = 0.00
    conf = 0.6

    OFFSET_CENTER_Y = -300
    OFFSET_CENTER_X = 0

    RANGE_ANGLE_X = [30, 110]
    RANGE_ANGLE_Y = [40, 90]

    real_x, real_y = 70, 70
    last_real_x, last_real_y = real_x, real_y
    last_range_x, last_range_y = 0, 0

    state_up_down = 0 
    last_up_down_y = 0

    last_time = time.time()
    wait_time = 0.3 # thời gian check đám lửa trước khi xác nhận phun
    log_time = time.time() # thời gian log cảnh báo một lần để tránh spam log khi có nhiều khung hình liên tiếp phát hiện lửa

    STATE = 0 # 0: checking, 2: wating, 3: shooting
    dir_x = 1 # 1: left, -1: right
    dir_y = 1 # 1: down, -1: up

    camera = get_image_from_camera(model_path = "last_3.pt",
                                    offset_center_x=OFFSET_CENTER_X, offset_center_y=OFFSET_CENTER_Y,
                                    conf=conf
                                    )
    position_calculator = PositionCalculator(camera.width, 
                                                camera.height, 
                                                P=P, I=I, D=D, 
                                                range_angle_x=RANGE_ANGLE_X, range_angle_y=RANGE_ANGLE_Y, 
                                                dir_x=dir_x, dir_y=dir_y
                                                )
    servo = ControlServo()
    servo.send_angle(real_x, real_y, 0)

    while True:
        # Capture an image from the camera
        frame = camera.get_image()
        
        # Detect objects in the image
        bboxs = camera.detect_objects(frame)
        
        target_positions = position_calculator.convert_center_coordinates(bboxs)
        x_range, y_range = position_calculator.calculate_position(target_positions)
        
        # move gun to check if there is any object
        if STATE == 0:
            real_x, real_y, dir_x, dir_y = position_calculator.dir_changer(real_x, real_y, dir_x, dir_y)
            
            servo.send_angle(real_x, real_y, 0)
            
            if target_positions:
                last_time = time.time()
                last_range_x, last_range_y = x_range, y_range            
                STATE = 1
        
        # If objects are detected, switch to waiting state
        if STATE == 1:
            print("cccccccccccccccccccccccccccccc")
            if x_range is None or y_range is None:
                STATE = 0
            else:
                error_range_x = x_range - last_range_x
                error_range_y = y_range - last_range_y
                
                error_range_x = abs(error_range_x)
                error_range_y = abs(error_range_y)
                
                if time.time() - last_time > wait_time:
                    last_time = time.time()
                    if error_range_x < 25 and error_range_y < 25:
                        last_real_x, last_real_y = real_x, real_y
                        if time.time() - log_time > 30:
                            log_time = time.time()
                            
                            warning = threading.Thread(target=warning_process.process_warning, args=(frame,))
                            warning.start()
                            
                        print("Object detected, switching to shooting state...")
                        STATE = 2
                    else: 
                        STATE = 0
        
        if STATE == 2:
            real_x, real_y, pump, last_up_down_y, state_up_down = position_calculator.calc_angle(real_x, real_y, x_range, y_range, last_up_down_y, state_up_down)
            servo.send_angle(real_x, real_y, pump)
            if pump == 1:
                last_time = time.time()
                print(f"shooting at angle: {real_x}, {real_y}")
            
            # Trường hợp khi không phát hiện lửa
            if time.time() - last_time > 1.5 and pump == 0:
                last_time = time.time()
                
                if abs(real_x - last_real_x) < 5  and abs(real_y - last_real_y) < 5:
                    print("Switching to checking state...")
                    real_y = 70 # trả về góc giữa
                    STATE = 0
                else:
                    last_real_x, last_real_y = real_x, real_y

            camera.show_error_coordinates(frame, x_range,  y_range)
            
        # Show debug information
        camera.draw_bounding_boxes(frame, bboxs)
        
        camera.draw_centers_points(frame)
        
        camera.show_image(frame)

if __name__ == "__main__":
    start()