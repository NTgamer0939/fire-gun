import cv2

cap = cv2.VideoCapture(0) 

# Đặt độ phân giải mong muốn
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Không thể mở camera")
    
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Độ phân giải được đặt: {width} x {height}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.line(frame, (width//2, height//2), (width//2, (height//2)+10), (0, 255, 0), 2)
    cv2.line(frame, (width//2, height//2), ((width//2)+10, height//2), (0, 255, 0), 2)
    
    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break