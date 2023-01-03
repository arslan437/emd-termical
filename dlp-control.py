import sys
import os
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QTextEdit, QMessageBox
from PyQt5 import QtGui, QtCore

baud_rates = ["9600", "19200", "28800", "38400", "57600", "76800", "115200"]


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("DLP Control")

    def initUI(self):

        # Create the scan button
        self.btn_scan = QPushButton("Scan Ports")
        self.btn_scan.clicked.connect(self.on_scan)

        # Create the port dropdown
        self.dpd_port = QComboBox()
        self.dpd_port.addItem("Select Port")
        self.dpd_port.setMinimumSize(100, 0)

        # Create the baud rate dropdown
        self.dpd_baud = QComboBox()
        self.dpd_baud.setCurrentIndex(0)
        for rate in baud_rates:
            self.dpd_baud.addItem(rate)
        self.dpd_baud.setMinimumSize(100, 0)

        # Create a "Connect" button
        self.btn_connect = QPushButton('Connect', self)
        self.btn_connect.clicked.connect(self.connect)

        # Create a "Jog up" button
        self.btn_up = QPushButton('UP', self)
        self.btn_up.clicked.connect(self.jogUp)
        self.btn_up.setEnabled(False)

        # Create a "Jog down" button
        self.btn_down = QPushButton('DOWN', self)
        self.btn_down.clicked.connect(self.jogDown)
        self.btn_down.setEnabled(False)

        # Create the clear button
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.on_clear)

        # Create the text box
        self.txt_msg_box = QTextEdit()

        # Create a vertical ly_controls to hold the widgets
        ly_controls = QVBoxLayout()
        ly_controls.addWidget(self.btn_scan)
        ly_controls.addWidget(self.dpd_port)
        ly_controls.addWidget(self.dpd_baud)
        ly_controls.addWidget(self.btn_connect)

        ly_controls.addWidget(self.btn_up)
        ly_controls.addWidget(self.btn_down)

        ly_controls.addWidget(self.txt_msg_box)
        ly_controls.addWidget(self.btn_clear)

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

        # Open the serial port
        self.serial = serial.Serial()

        # Start a thread to read incoming data from the serial port
        self.t = threading.Thread(target=self.readSerial)
        self.t.start()

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
        # Stop the serial thread
        # self.t.stop()
        
        # Close the serial port
        self.serial.close()
        
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
                break
            # Read a line of data from the serial port
            data = self.serial.readline().strip()
            # Print the data to the console
            print(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
