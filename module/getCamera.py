import cv2
from ultralytics import YOLO
import torch

class FromCamera:
    def __init__ (self, model_path='last_3.pt', conf=0.7, width=1920, height=1080):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        else:
            print("Cam is open")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.model = YOLO(model_path)
        self.model.to(torch.device('cuda'))
        self.model.conf = conf

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

    def get_image(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Could not read frame")
        return frame

    def detect_fire(self, frame):
        results = self.model(frame, verbose = False)
        boxes = []
        info = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    if box.conf[0] >= self.model.conf:
                        boxes.append(box)
                        info.append(result)
        return boxes, result

    def draw_bounding_boxes(self, frame, info):
        if info == []: return
        for inf in info:
            for box in inf.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                label = f"conf: {box.conf[0]:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def draw_centers_points(self, frame):
        cv2.circle(frame, (self.width // 2, self.height // 2), 5, (255, 0, 0), -1)

    def show_error_coordinates(self, frame, x_range, y_range):
        if x_range is not None and y_range is not None:
            cv2.putText(frame, f"X: {x_range:.2f}, Y: {y_range:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def show_image(self, frame):
        cv2.imshow("Detected Objects", frame)
        cv2.waitKey(1)