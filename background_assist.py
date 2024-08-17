import time
import numpy as np
from PIL import ImageGrab
import cv2
from detection.object_detector import ObjectDetector
from PyQt5.QtCore import QThread, pyqtSignal

class BackgroundAssistThread(QThread):
    detection_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.detector = ObjectDetector()
        self.running = True

    def run(self):
        while self.running:
            # Capture the screen
            screen = ImageGrab.grab()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect characters
            detections = self.detector.detect(frame)
            if detections:
                self.detection_signal.emit(detections)
            
            time.sleep(1)  # Adjust the sleep time as needed

    def stop(self):
        self.running = False
        self.wait()
