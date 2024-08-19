import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        pass

    def detect(self, frame):
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray_frame, 30, 100) 

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                obj_center_x = x + w // 2
                obj_center_y = y + h // 2

                if self.is_character(x, y, w, h):
                    detections.append((x, y, w, h))

        return detections

    def is_character(self, x, y, w, h):
        min_width = 10
        max_width = 300
        min_height = 20
        max_height = 500

        return min_width < w < max_width and min_height < h < max_height
