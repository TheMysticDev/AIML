from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PIL import ImageGrab
import cv2
import numpy as np
from detection.object_detector import ObjectDetector
import sys

class AIMLApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.detector = ObjectDetector()
        self.aim_assist_active = False

    def initUI(self):
        self.setWindowTitle('AIM Assist')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        
        self.aim_assist_button = QPushButton('Start AIM Assist', self)
        self.aim_assist_button.clicked.connect(self.toggle_aim_assist)
        layout.addWidget(self.aim_assist_button)

        self.status_label = QLabel('AIM Assist OFF', self)
        layout.addWidget(self.status_label)

        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

        # Timer to periodically process the screen
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1000)  # Process every second

    def toggle_aim_assist(self):
        self.aim_assist_active = not self.aim_assist_active
        if self.aim_assist_active:
            self.aim_assist_button.setText('Stop AIM Assist')
            self.status_label.setText('AIM Assist ON')
            self.clear_button.setEnabled(False)  # Disable clear button while aim assist is active
        else:
            self.aim_assist_button.setText('Start AIM Assist')
            self.status_label.setText('AIM Assist OFF')
            self.clear_button.setEnabled(True)  # Enable clear button when aim assist is inactive

    def process_frame(self):
        if self.aim_assist_active:
            # Capture the screen
            screen = ImageGrab.grab()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with object detector
            detections = self.detector.detect(frame)
            if detections:
                message = f"Detected characters: {detections}"
                print(message)
                self.log_box.append(message)

    def clear_log(self):
        if not self.aim_assist_active:
            self.log_box.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIMLApp()
    window.show()
    sys.exit(app.exec_())
