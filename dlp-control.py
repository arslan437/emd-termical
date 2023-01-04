import sys
import os
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QTextEdit, QMessageBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QThread

baud_rates = ["9600", "19200", "28800", "38400", "57600", "76800", "115200"]
control_width = 150

class serial_thread(QThread):
    updateTextSignal = pyqtSignal(str)

    def __init__(self, port, baud):
        super().__init__()
        # Open the serial port
        self.serial = serial.Serial(port, baud)

    def disconnect(self):
        # Close the serial port
        self.serial.close()

    def run(self):
            while True:
                if not self.serial.isOpen():
                    print("Getting out")
                    break
                # Read a line of data from the serial port
                # data = self.serial.readline().strip()
                data = self.serial.read().decode('utf-8')
                # Print the data to the console
                print(data)
                # self.txt_msg_box.append(data)
                self.updateTextSignal.emit(data)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DLP Control")
        self.initUI()

    def initUI(self):
        # Create the scan button
        self.btn_scan = QPushButton("Scan Ports")
        self.btn_scan.clicked.connect(self.on_scan)
        self.btn_scan.setFixedWidth(control_width)

        # Create the port dropdown
        self.dpd_port = QComboBox()
        self.dpd_port.addItem("Select Port")
        self.dpd_port.setFixedWidth(control_width)

        # Create the baud rate dropdown
        self.dpd_baud = QComboBox()
        self.dpd_baud.setCurrentIndex(0)
        for rate in baud_rates:
            self.dpd_baud.addItem(rate)
        self.dpd_baud.setFixedWidth(control_width)

        # Create a "Connect" button
        self.btn_connect = QPushButton('Connect', self)
        self.btn_connect.clicked.connect(self.connect)
        self.btn_connect.setFixedWidth(control_width)

        # Create a "Jog up" button
        self.btn_up = QPushButton('UP', self)
        self.btn_up.clicked.connect(self.jogUp)
        self.btn_up.setEnabled(False)
        self.btn_up.setFixedWidth(control_width)

        # Create a "Jog down" button
        self.btn_down = QPushButton('DOWN', self)
        self.btn_down.clicked.connect(self.jogDown)
        self.btn_down.setEnabled(False)
        self.btn_down.setFixedWidth(control_width)

        # Create the clear button
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_clear.setFixedWidth(control_width)

        # Create the text box
        self.txt_msg_box = QTextEdit()
        self.txt_msg_box.setFixedWidth(250)

        # Create a vertical ly_controls to hold the widgets
        ly_controls = QVBoxLayout()
        ly_controls.setAlignment(QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.btn_scan, alignment= QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.dpd_port, alignment= QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.dpd_baud, alignment= QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.btn_connect, alignment= QtCore.Qt.AlignHCenter)

        ly_controls.addWidget(self.btn_up, alignment= QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.btn_down, alignment= QtCore.Qt.AlignHCenter)

        ly_controls.addWidget(self.txt_msg_box, alignment= QtCore.Qt.AlignHCenter)
        ly_controls.addWidget(self.btn_clear, alignment= QtCore.Qt.AlignHCenter)

        self.photo = QLabel()
        self.photo.setMinimumHeight(500)
        self.photo.setMinimumWidth(500)
        self.photo.setText("")
        

        if os.path.exists('image.jpg'):
            # Load the image and display it
            image = QtGui.QPixmap('cat.jpg')
            self.photo.setPixmap(image)
        else:
            # Set the label's background color to black
            self.photo.setStyleSheet('background-color: black')

        ly_image = QHBoxLayout()
        ly_image.addLayout(ly_controls)
        ly_image.addWidget(self.photo)
        # Set the central widget to the ly_controls
        widget = QWidget(self)
        widget.setLayout(ly_image)
        self.setCentralWidget(widget)

    def connect(self):
        
        port =self.dpd_port.currentText() 
        baud = self.dpd_baud.currentText()
        

        # Check if a valid port and baud rate are selected
        if not self.is_valid_port(port):
            QMessageBox.warning(self, "Error", "Please select a valid port")
            return
        if not self.is_valid_baud(baud):
            QMessageBox.warning(self, "Error", "Please select a valid baud rate")
            return

        # Create the update text thread
        # self.update_text_thread = serial_thread(port, baud)
        self.update_text_thread = serial_thread(port, baud)
        self.update_text_thread.updateTextSignal.connect(self.updateText)

        # Start the thread
        self.update_text_thread.start()

        # Update the UI
        self.dpd_baud.setEnabled(False)
        self.dpd_port.setEnabled(False)
        self.btn_scan.setEnabled(False)
        self.btn_down.setEnabled(True)
        self.btn_up.setEnabled(True)
        self.btn_connect.setText("Disconnect")
        self.btn_connect.clicked.disconnect(self.connect)
        self.btn_connect.clicked.connect(self.disconnect)

    def disconnect(self):
        
        # self.update_text_thread.disconnect()
        # self.update_text_thread.quit()
        # self.update_text_thread.wait()
        srl = self.update_text_thread.serial
        srl.close()

        # Update the UI
        self.dpd_baud.setEnabled(True)
        self.dpd_port.setEnabled(True)
        self.btn_scan.setEnabled(True)
        self.btn_down.setEnabled(False)
        self.btn_up.setEnabled(False)
        self.btn_connect.setText("Connect")
        self.btn_connect.clicked.disconnect(self.disconnect)
        self.btn_connect.clicked.connect(self.connect)

    def is_valid_port(self, port):
        ports = serial.tools.list_ports.comports()
        port_names = [p.device for p in ports]

        # Return True if the selection is in the list of available ports, False otherwise
        return port in port_names
    
    def is_valid_baud(self, baud):
        # Check if the selection is a valid baud rate
        if baud in baud_rates:
            return True
        else:
            return False

    def on_scan(self):
        self.dpd_port.clear()
        ports = list(serial.tools.list_ports.comports())
        # print(ports)
        for port, _, _ in ports:
            self.dpd_port.addItem(port)

    def on_clear(self):
        self.txt_msg_box.clear()
    
    def updateText(self, text):
        self.txt_msg_box.append(text)

    def jogUp(self):
        if not self.serial.isOpen():
            return
        # Send the "jog up" command to the serial port
        self.serial.write(b'JOG_UP\n')

    def jogDown(self):
        if not self.serial.isOpen():
            return
        # Send the "jog down" command to the serial port
        self.serial.write(b'JOG_DOWN\n')

    def readSerial(self):

        while True:
            if not self.serial.isOpen():
                print("Getting out")
                break
            # Read a line of data from the serial port
            # data = self.serial.readline().strip()
            data = self.serial.read().decode('utf-8')
            # Print the data to the console
            print(data)
            # self.txt_msg_box.append(data)
            self.updateTextSignal.emit(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
