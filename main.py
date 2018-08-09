import sys
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage


class MainWindow1(QMainWindow):
    def __init__(self):
        super(MainWindow1, self).__init__()
        loadUi('main_window.ui', self)
        self.image = None
        self.startButton.clicked.connect(self.start_webcam)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(1)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.display_image(self.image, 1)

    def display_image(self, img, window = 1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)

        out_image = out_image.rgbSwapped()
        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(out_image))
            self.imgLabel.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow1()
    window.setWindowTitle('Hellooooooooooooo')
    window.show()
    sys.exit(app.exec_())
