import sys
import threading
import time

import cv2
import numpy
import serial
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
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
        self.isCreatingSample = True
        self.errorList = [0] * 5
        self.cameraIndex = 0
        self.btStart.clicked.connect(self.start_webcam)  # gán sự kiện click cho nút btStart
        self.motion_enabled = False
        self.sensorData = None
        self.btStop.clicked.connect(self.stopCamera)
        self.motionFrame = None
        self.btOpenSampleDataWindow.clicked.connect(self.openSampleDataWindow)
        self.btSaveSetting.clicked.connect(self.save_setting)
        self.imRealList = [self.imReal1, self.imReal2, self.imReal3, self.imReal4, self.imReal5]
        self.lbErrorList = [self.lbError1, self.lbError2, self.lbError3, self.lbError4, self.lbError5]
        for i in range(10):
            self.cbSelectCom.addItem(str(i + 1))
        for i in range(3):
            self.cbSelectCam.addItem(str(i))
        self.cbSelectCam.setCurrentIndex(1)

    def save_setting(self):
        # set com port
        try:
            self.sensorData = serial.Serial('COM' + self.cbSelectCom.currentText(), 9600)
            thread = threading.Thread(target=self.readSensorCreateSampleData, args=())
            thread.start()
        except serial.serialutil.SerialException as e:
            q = QMessageBox()
            q.setText('Lỗi: ' + str(e))
            q.exec()
        # set camera
        self.cameraIndex = int(self.cbSelectCam.currentText())
        q1 = QMessageBox()
        q1.setText('Lưu thành công')
        q1.exec()

    # def closeEvent(self, event):
    #     print ("User has clicked the red x on the main window")
    #     self.thread.wait()
    #     self.thread = None
    #     event.accept()

    def readSensorCreateSampleData(self):
        while True:
            while self.sensorData.inWaiting() == 0:
                pass
            textline = str(self.sensorData.readline())
            print(textline)
            if self.isCreatingSample:
                if textline == 'b\'CHUP ANH 1 \\n\'':
                    self.sample_data[0] = self.cvtColorAndBlur()
                    SampleDataWindow.display_image(self.sample_data[0], self.sampleDataDialog.imSample1)
                if textline == 'b\'CHUP ANH 2 \\n\'':
                    self.sample_data[1] = self.cvtColorAndBlur()
                    SampleDataWindow.display_image(self.sample_data[1], self.sampleDataDialog.imSample2)
                if textline == 'b\'CHUP ANH 3 \\n\'':
                    self.sample_data[2] = self.cvtColorAndBlur()
                    SampleDataWindow.display_image(self.sample_data[2], self.sampleDataDialog.imSample3)
                if textline == 'b\'CHUP ANH 4 \\n\'':
                    self.sample_data[3] = self.cvtColorAndBlur()
                    SampleDataWindow.display_image(self.sample_data[3], self.sampleDataDialog.imSample4)
                if textline == 'b\'CHUP ANH 5 \\n\'':
                    self.sample_data[4] = self.cvtColorAndBlur()
                    SampleDataWindow.display_image(self.sample_data[4], self.sampleDataDialog.imSample5)
            else:
                currentIndex = int(textline[11:12])
                # first run, current is 1
                if currentIndex > self.currentIndex:
                    detect_motion = self.detect_motion(self.cvtColorAndBlur2(), self.sample_data[currentIndex - 1])
                    SampleDataWindow.display_image(detect_motion, self.imRealList[currentIndex - 1])
                    print(self.errorList)
                    self.lbErrorList[currentIndex - 1].setText(str(self.errorList[currentIndex - 1]) + ' lỗi')
                    if currentIndex == 5:
                        self.currentIndex = 0  # restart vong lap
                    else:
                        self.currentIndex = currentIndex

            time.sleep(0.5)

    def cvtColorAndBlur(self):
        gray_image = cv2.cvtColor(self.sampleDataDialog.image.copy(), cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray_image, (11, 11), 0)
        # return cv2.GaussianBlur(self.sampleDataDialog.image.copy(), (11, 11), 0)

    def cvtColorAndBlur2(self):
        # gray_image = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2GRAY)
        # return cv2.GaussianBlur(gray_image, (11, 11), 0)
        return cv2.GaussianBlur(self.image.copy(), (11, 11), 0)

    def onClickDone(self):
        containNone = False
        for item in self.sample_data:
            if item is None:
                containNone = True
        if not containNone:
            self.lbStatus.setText('Da co du lieu mau')
            self.isCreatingSample = False
        else:
            self.lbStatus.setText('Co loi xay ra 101')
        self.sampleDataDialog.close()

    def openSampleDataWindow(self):
        self.sampleDataDialog = SampleDataWindow()
        self.sampleDataDialog.show()
        self.sampleDataDialog.btDone.clicked.connect(self.onClickDone)

    def detect_webcam_motion(self, status):
        if status:
            self.motion_enabled = True
        else:
            self.motion_enabled = False

    def stopCamera(self):
        self.timer.stop()

    def start_webcam(self):  # định nghĩa hàm bật cam
        if self.isCreatingSample:
            q = QMessageBox()
            q.setText('Ban chua co du lieu mau!')
            q.exec()
        else:
            try:
                self.capture = cv2.VideoCapture(self.cameraIndex)  # lấy hình ảnh từ camera 0
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # set chiều cao
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # set chiều rộng

                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(15)
            except:
                q1 = QMessageBox()
                q1.setText('Lỗi camera ')
                q1.exec()

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        # if self.motion_enabled:
        # if(self.currentIndex > )
        # detected_motion = self.detect_motion(self.image.copy(), self.motionFrame)
        # self.display_image(detected_motion, 1)
        # else:
        self.display_image(self.image, 1)

    def detect_motion(self, input_img, compareImage):
        assert type(input_img) is numpy.ndarray
        assert type(compareImage) is numpy.ndarray
        self.text = 'No motion'
        image1ToCompare = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)

        frame_diff = cv2.absdiff(compareImage, image1ToCompare)
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
            cv2.rectangle(input_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        self.errorList[self.currentIndex] = len(contour)

        # if max_x - min_x > 80 and max_y - min_y > 80:
        #     cv2.rectangle(input_img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        #     self.text = 'motion detected'
        # print text to image
        # cv2.putText(input_img, 'motion status: {}'.format(self.text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
        #             (0, 0, 255), 2)

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

    # def onToggle(self):
    #     self.isCreatingSample = not self.isCreatingSample
    #     self.btToggle.setText('creating sample' if self.isCreatingSample else 'check product')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow1()
    window.setWindowTitle('ktfv')
    window.show()
    app.setQuitOnLastWindowClosed(True)
    sys.exit(app.exec_())
