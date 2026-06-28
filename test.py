import cv2
from module.getCamera import FromCamera

cam = FromCamera()

while True:
    frame = cam.get_image()
    
    cam.draw_centers_points(frame)
    
    
    cam.show_image(frame)

cam.release()
cv2.destroyAllWindows()