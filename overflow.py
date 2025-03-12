import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import mss

class OverlayWindow(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Absolute MESS")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(screen_width, screen_height)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(100)

    def update_overlay(self):
        with mss.mss() as sct:
            monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        global prev_frame
        if prev_frame is None:
            prev_frame = gray_frame
            return

        frame_diff = cv2.absdiff(prev_frame, gray_frame)
        _, thresh = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img)
        self.setPixmap(pixmap)

        prev_frame = gray_frame

def main():
    global screen_width, screen_height, prev_frame

    screen_width, screen_height = 800, 600
    app = QApplication(sys.argv)
    
    overlay = OverlayWindow()
    overlay.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    prev_frame = None
    main()
