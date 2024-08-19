import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor
import ctypes
import numpy as np
import cv2
from PIL import ImageGrab
from detection.object_detector import ObjectDetector
from pynput import mouse

class FOVOverlay(QWidget):
    def __init__(self, fov):
        super().__init__()
        self.fov = fov
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)

        screen_width = self.width()
        screen_height = self.height()
        center_x, center_y = screen_width // 2, screen_height // 2

        painter.drawEllipse(center_x - self.fov, center_y - self.fov, self.fov * 2, self.fov * 2)

    def update_fov(self, fov):
        self.fov = fov
        self.update()

class AIMLApp(QWidget):
    def __init__(self):
        super().__init__()
        self.fov = 100
        self.fov_adjustment_active = False
        self.initUI()
        self.detector = ObjectDetector()
        self.aim_assist_active = False
        self.locked_target = None

        self.fov_overlay = FOVOverlay(self.fov)
        self.fov_overlay.hide()

        self.right_click_pressed = False
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.center_x = None
        self.center_y = None

    def initUI(self):
        self.setWindowTitle('AIM Assist')
        self.setGeometry(100, 100, 400, 400)

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

        self.fov_button = QPushButton('Adjust FOV', self)
        self.fov_button.clicked.connect(self.toggle_fov_adjustment)
        layout.addWidget(self.fov_button)

        self.fov_slider = QSlider(Qt.Horizontal)
        self.fov_slider.setMinimum(50)
        self.fov_slider.setMaximum(300)
        self.fov_slider.setValue(self.fov)
        self.fov_slider.setEnabled(False)
        self.fov_slider.valueChanged.connect(self.update_fov)
        layout.addWidget(self.fov_slider)

        self.setLayout(layout)

        # Aplicar estilo personalizado
        self.apply_styles()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1000 // 30)

    def apply_styles(self):
        gradient_style = """
        QWidget {
            background-color: #0d0d0d;
            color: #ffffff;
        }
        QPushButton {
            background-color: #1a1a1a;
            border: 1px solid #00ccff;
            color: #00ccff;
            padding: 10px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #00ccff;
            color: #000000;
        }
        QLabel {
            font-size: 18px;
            color: #00ccff;
        }
        QTextEdit {
            background-color: #1a1a1a;
            border: 1px solid #00ccff;
            color: #00ccff;
            font-size: 14px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #00ccff;
            height: 8px;
            background: #1a1a1a;
        }
        QSlider::handle:horizontal {
            background: #00ccff;
            border: 1px solid #00ccff;
            width: 18px;
            margin: -2px 0;
        }
        """
        self.setStyleSheet(gradient_style)

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
            self.locked_target = None

    def toggle_fov_adjustment(self):
        self.fov_adjustment_active = not self.fov_adjustment_active
        self.fov_slider.setEnabled(self.fov_adjustment_active)
        if self.fov_adjustment_active:
            self.fov_button.setText('FOV Adjusting...')
            self.fov_overlay.show()
        else:
            self.fov_button.setText('Adjust FOV')
            self.fov_overlay.hide()

    def update_fov(self, value):
        self.fov = value
        self.fov_overlay.update_fov(self.fov)

    def process_frame(self):
        if self.aim_assist_active and self.is_right_click_pressed():
            screen = ImageGrab.grab()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.center_x is None or self.center_y is None:
                self.center_x = frame.shape[1] // 2
                self.center_y = frame.shape[0] // 2

            detections = self.detector.detect(frame)
            if detections:
                detections.sort(key=lambda d: np.linalg.norm(np.array([d[0] + d[2] // 2, d[1] + d[3] // 2]) - np.array([self.center_x, self.center_y])))
                target = detections[0]
                self.locked_target = (target[0] + target[2] // 2, target[1] + target[3] // 2)

                if self.locked_target:
                    self.log_box.append(f"Locked target: {self.locked_target}")
                    ctypes.windll.user32.SetCursorPos(int(self.locked_target[0]), int(self.locked_target[1]))

            self.log_box.append("No characters detected")

    def clear_log(self):
        if not self.aim_assist_active:
            self.log_box.clear()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            self.right_click_pressed = pressed

    def is_right_click_pressed(self):
        return self.right_click_pressed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AIMLApp()
    ex.show()
    sys.exit(app.exec_())
