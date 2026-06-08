import math

class PositionCalculator:
    def __init__(self, width_camera, height_camera, P, I, D, range_angle_x, range_angle_y, dir_x=1, dir_y=1):
        self.width = width_camera
        self.height = height_camera
        self.center_x = width_camera // 2
        self.center_y = height_camera // 2
        self.P = P
        self.I = I
        self.D = D
        self.range_angle_x = range_angle_x
        self.range_angle_y = range_angle_y
        self.dir_x = dir_x
        self.dir_y = dir_y
        
    def choose_target(self, target_position):
        if not target_position:
            return None
        
        distance_check = 1000
        for target in target_position:
            # choose nearest target
            distance = math.sqrt((target[0] - self.center_x) ** 2 + (target[1] - self.center_y) ** 2)
            if distance < distance_check:
                distance_check = distance
        return target

    def convert_center_coordinates(self, results):
        if not results:
            return None
        
        target_position = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                target_position.append((center_x, center_y))
        return target_position
        
    def calculate_position(self, target_position):
        if not target_position:
            return None, None
        
        target = self.choose_target(target_position)
        if target is None:
            return None, None
        
        # calculate pid
        error_x = target[0] - self.center_x
        error_y = target[1] - self.center_y
        
        return error_x, error_y
    
    def calc_angle(self, real_x, real_y, error_x, error_y, last_up_down_y, state_up_down, dead_zone=20):
        pump = 0
        if error_x is None or error_y is None:
            return real_x, real_y, pump, last_up_down_y, state_up_down

        if abs(error_x) < dead_zone and abs(error_y) < dead_zone and state_up_down == 0:
            pump = 1
            state_up_down = 1
            last_up_down_y = real_y
            return real_x, real_y, pump, last_up_down_y, state_up_down
        
        if abs(error_x) < dead_zone and state_up_down == 1:
            pump = 1
            if real_y - last_up_down_y > 8:
                real_y = last_up_down_y
            else:
                real_y += 0.4
            return real_x, real_y, pump, last_up_down_y, state_up_down
        
        elif abs(error_x) > dead_zone:
            state_up_down = 0
            
        # mirror values
        error_x = -error_x
        # error_y = -error_y
        # calculate new angle
        real_x = round(real_x + (error_x*self.P), 1)
        real_y = round(real_y + (error_y*self.P), 1)
        
        if real_x < self.range_angle_x[0]:
            real_x = self.range_angle_x[0]
        if real_x > self.range_angle_x[1]:
            real_x = self.range_angle_x[1]
            
        if real_y < self.range_angle_y[0]:
            real_y = self.range_angle_y[0]
        if real_y > self.range_angle_y[1]:
            real_y = self.range_angle_y[1]
        
        #print(f"real_x: {real_x}, real_y: {real_y}")
        return real_x, real_y, pump, last_up_down_y, state_up_down
    
    def dir_changer(self, real_x, real_y, dir_x, dir_y):
        if dir_x == 1:
            real_x += 1
            if real_x > self.range_angle_x[1] - 10:
                dir_x = -1
                
        elif dir_x == -1:
            real_x -= 1
            if real_x < self.range_angle_x[0] + 10:
                dir_x = 1
        
        
        #print(f"real_x: {real_x}, real_y: {real_y}, dir_x: {dir_x}, dir_y: {dir_y}")
        return real_x, real_y, dir_x, dir_y