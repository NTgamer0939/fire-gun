from ultralytics import YOLO
import cv2

# Load model (YOLOv8 pretrained)
model = YOLO("last_2.pt")  # hoặc yolov8s.pt, yolov8m.pt tùy độ nặng

# chạy yolo với pytorch cuda
model.to("cuda")  # Chuyển model sang GPU nếu có

# Mở webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Kiểm tra mở camera thành công
if not cap.isOpened():
    print("Không thể mở camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Chạy phát hiện vật thể
    results = model(frame)

    # Vẽ kết quả lên frame
    annotated_frame = results[0].plot()

    # Hiển thị kết quả
    cv2.imshow("YOLOv8 Detection", annotated_frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
