import cv2
import numpy as np
#TheMagic
class ObjectDetector:
    def __init__(self):
        pass

    def detect(self, frame):

        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        radius = min(width, height) // 4  

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  
                x, y, w, h = cv2.boundingRect(contour)
                
                obj_center_x = x + w // 2
                obj_center_y = y + h // 2
                
                distance = np.sqrt((obj_center_x - center_x) ** 2 + (obj_center_y - center_y) ** 2)

                if distance <= radius:
                    detections.append((x, y, w, h))

        return detections
