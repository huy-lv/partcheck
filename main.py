import sys
import threading
import time

import cv2
import serial
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from sampleDataClass import SampleDataWindow


class MainWindow1(QMainWindow):

    def __init__(self):  # ham khoi tao
        super(MainWindow1, self).__init__()  # gọi hàm khởi tạo của lớp cha
        loadUi('main_window.ui', self)  # load file giao dien
        # khởi tạo các giá trị
        self.image = None
        self.text = None
        self.timer = None
        self.capture = None
        self.sample_data = [None] * 5
        self.currentIndex = 0

        self.btStart.clicked.connect(self.start_webcam)  # gán sự kiện click cho nút btStart
        self.btDetect.setCheckable(True)
        self.btDetect.toggled.connect(self.detect_webcam_motion)
        self.motion_enabled = False

        self.btRefer.clicked.connect(self.set_motion_image)
        self.motionFrame = None
        self.btOpenSampleDataWindow.clicked.connect(self.openSampleDataWindow)
        self.sensorData = serial.Serial('COM4', 9600)
        thread = threading.Thread(target=self.readSensor, args=())
        thread.start()

    def readSensor(self):
        while True:
            while (self.sensorData.inWaiting() == 0):
                pass
            textline = str(self.sensorData.readline())
            print(textline)
            if textline == 'b\'CHUP ANH 1 \\n\'':
                self.sample_data[0] = self.cvtColorAndBlur()
                self.sampleDataDialog.display_image(self.sample_data[0], self.sampleDataDialog.imSample1)
            if textline == 'b\'CHUP ANH 2 \\n\'':
                self.sample_data[1] = self.cvtColorAndBlur()
                self.sampleDataDialog.display_image(self.sample_data[1], self.sampleDataDialog.imSample2)
            if textline == 'b\'CHUP ANH 3 \\n\'':
                self.sample_data[2] = self.cvtColorAndBlur()
                self.sampleDataDialog.display_image(self.sample_data[2], self.sampleDataDialog.imSample3)
            if textline == 'b\'CHUP ANH 4 \\n\'':
                self.sample_data[3] = self.cvtColorAndBlur()
                self.sampleDataDialog.display_image(self.sample_data[3], self.sampleDataDialog.imSample4)
            if textline == 'b\'CHUP ANH 5 \\n\'':
                self.sample_data[4] = self.cvtColorAndBlur()
                self.sampleDataDialog.display_image(self.sample_data[4], self.sampleDataDialog.imSample5)
            time.sleep(0.5)

    def cvtColorAndBlur(self):
        gray_image = cv2.cvtColor(self.sampleDataDialog.image.copy(), cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray_image, (11, 11), 0)

    def onClickDone(self):
        containNone = False
        for item in self.sample_data:
            if item is None:
                containNone = True
        if not containNone:
            self.lbStatus.setText('Da co du lieu mau')
        self.sampleDataDialog.close()

    def openSampleDataWindow(self):
        self.sampleDataDialog = SampleDataWindow()
        self.sampleDataDialog.show()
        self.sampleDataDialog.btDone.clicked.connect(self.onClickDone)

    def detect_webcam_motion(self, status):
        if status:
            self.motion_enabled = True
            self.btDetect.setText('Stop motion')
        else:
            self.motion_enabled = False
            self.btDetect.setText('Detect motion')

    def set_motion_image(self):
        gray_image = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (21, 21), 0)
        self.motionFrame = gray_image
        self.display_image(self.motionFrame, 2)

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
        # if self.motion_enabled:
        # if(self.currentIndex > )
        detected_motion = self.detect_motion(self.image.copy(), self.motionFrame)
        self.display_image(detected_motion, 1)
        # else:
        #     self.display_image(self.image, 1)

    def detect_motion(self, input_img, compareImage):
        self.text = 'No motion'
        gray_image = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (21, 21), 0)
        frame_diff = cv2.absdiff(compareImage, gray_image)
        thresh = cv2.threshold(frame_diff, 40, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=5)
        im2, contour, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        try:
            hierarchy = hierarchy[0]
        except:
            hierarchy = []
        height, width, channels = input_img.shape
        min_x, min_y = width, height
        max_x = max_y = 0
        for ct, hier in zip(contour, hierarchy):
            (x, y, w, h) = cv2.boundingRect(ct)
            min_x, max_x = min(x, min_x), max(x + w, max_x)
            min_y, max_y = min(y, min_y), max(y + h, max_y)
            self.lb1.setText(str(x) + ' ' + str(y))
            cv2.rectangle(input_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # if max_x - min_x > 80 and max_y - min_y > 80:
        #     cv2.rectangle(input_img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        #     self.text = 'motion detected'
        cv2.putText(input_img, 'motion status: {}'.format(self.text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 0, 255), 2)

        return input_img

    def display_image(self, img, window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)

        out_image = out_image.rgbSwapped()
        if window == 1:
            self.vidMain.setPixmap(QPixmap.fromImage(out_image))
            self.vidMain.setScaledContents(True)
        if window == 2:
            self.vidRefer.setPixmap(QPixmap.fromImage(out_image))
            self.vidRefer.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow1()
    window.setWindowTitle('Hellooooooooooooo')
    window.show()
    app.setQuitOnLastWindowClosed(True)
    sys.exit(app.exec_())
