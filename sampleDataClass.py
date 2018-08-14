import cv2
import numpy
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class SampleDataWindow(QDialog):
    def __init__(self):  # ham khoi tao
        super(SampleDataWindow, self).__init__()  # gọi hàm khởi tạo của lớp cha
        loadUi('sampleData.ui', self)  # load file giao dien
        self.bt_sample_start.clicked.connect(self.start_webcam)
        self.timer = None
        self.image = None
        self.capture = None

    def start_webcam(self):  # định nghĩa hàm bật cam
        self.capture = cv2.VideoCapture(1)  # lấy hình ảnh từ camera 0
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # set chiều cao
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # set chiều rộng

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(15)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.display_image(self.image, self.vid_sample_camera)

    @staticmethod
    def display_image(img, imageBox):
        out_image = SampleDataWindow.convertDArrayToImage(img)
        out_image = out_image.rgbSwapped()
        # if window == 1:
        imageBox.setPixmap(QPixmap.fromImage(out_image))
        imageBox.setScaledContents(True)
        # elif window == 2:
        #     self.imSample1.setPixmap(QPixmap.fromImage(out_image))
        #     self.imSample1.setScaledContents(True)
        # elif window == 2:
        #     self.imSample1.setPixmap(QPixmap.fromImage(out_image))
        #     self.imSample1.setScaledContents(True)

    @staticmethod
    def convertDArrayToImage(img):
        assert type(img) is numpy.ndarray
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        return QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)


    def print(self):
        print("sssss")
