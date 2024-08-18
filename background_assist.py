import cv2
import numpy as np
from PIL import ImageGrab
from detection.object_detector import ObjectDetector

class BackgroundAssist:
    def __init__(self):
        self.detector = ObjectDetector()
        self.fov_radius = 100  # Default radius for FOV circle
        self.fov_active = False

    def update_fov(self, radius):
        self.fov_radius = radius

    def toggle_fov(self, state):
        self.fov_active = state

    def process(self):
        while True:
            screen = ImageGrab.grab()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.fov_active:
                height, width = frame.shape[:2]
                center = (width // 2, height // 2)
                cv2.circle(frame, center, self.fov_radius, (0, 255, 0), 2)

            detections = self.detector.detect(frame, self.fov_radius)
            if detections:
                print(f"Detected characters: {detections}")

            cv2.imshow('AIM Assist', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    assist = BackgroundAssist()
    assist.process()