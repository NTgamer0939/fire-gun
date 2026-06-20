import math
import time

def get_center_target(boxes):
    centers = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        centers.append((int((x1 + x2) / 2), int((y1 + y2) / 2)))
    return centers

def cal_degree(center_targets, width, height, last_angle_x, last_angle_y):
    # Take nearest target
    distance = 10000
    nearest = []
    x_center = width / 2
    y_center = height / 2 - 120
    for coor in center_targets:
        target_distance = abs(math.sqrt(((coor[0] - x_center) ** 2 ) + ((coor[1] - y_center) ** 2)))
        if target_distance < distance:
            distance = target_distance
            nearest = coor
    
    if distance < 10: return last_angle_x, last_angle_y, 1
    
    # Calculate degree
    x_distance = nearest[0] - x_center
    y_distance = nearest[1] - y_center
    
    x_degree = x_distance / (6.03 * 2)
    y_degree = y_distance / (10.4 * 2)
    
    if x_distance < x_center: x_degree *= -1
    #if y_distance < y_center: y_degree *= -1
    
    if (x_distance < width / 3) and (x_distance > width - width / 3): x_degree /= 2
    if (y_distance < width / 3) and (y_distance > width - width / 3): y_degree /= 2

    return x_degree, y_degree, 0