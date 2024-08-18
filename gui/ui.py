from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer
from PIL import ImageGrab
import cv2
import numpy as np
from detection.object_detector import ObjectDetector
import sys
from pynput import mouse
from pynput.mouse import Controller 
#TheMagic
class AIMLApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.detector = ObjectDetector()
        self.aim_assist_active = False
        self.right_click_held = False
        self.mouse_controller = Controller() 

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1000)  

    def toggle_aim_assist(self):
        self.aim_assist_active = not self.aim_assist_active
        if self.aim_assist_active:
            self.aim_assist_button.setText('Stop AIM Assist')
            self.status_label.setText('AIM Assist ON')
            self.clear_button.setEnabled(False) 
        else:
            self.aim_assist_button.setText('Start AIM Assist')
            self.status_label.setText('AIM Assist OFF')
            self.clear_button.setEnabled(True)  

    def process_frame(self):
        if self.aim_assist_active and self.right_click_held:

            screen = ImageGrab.grab()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            detections = self.detector.detect(frame)
            if detections:

                x, y, w, h = detections[0]
                target_x = x + w // 2
                target_y = y + h // 2
                
                screen_width, screen_height = screen.size
                current_x, current_y = self.mouse_controller.position
                move_x = target_x - (screen_width // 2)
                move_y = target_y - (screen_height // 2)
                self.mouse_controller.move(move_x, move_y)

                message = f"Detected characters: {detections}"
                print(message)
                self.log_box.append(message)

    def clear_log(self):
        if not self.aim_assist_active:
            self.log_box.clear()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            self.right_click_held = pressed

    def closeEvent(self, event):
        self.mouse_listener.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIMLApp()
    window.show()
    sys.exit(app.exec_())
