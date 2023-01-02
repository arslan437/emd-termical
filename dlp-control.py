import sys
import serial
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QTextEdit

baud_rates = ["9600", "19200", "28800", "38400", "57600", "76800", "115200"]


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("DLP Control")

    def initUI(self):

        # Create the scan button
        scan_button = QPushButton("Scan Ports")
        scan_button.clicked.connect(self.on_scan)

        # Create the port dropdown
        port_dropdown = QComboBox()
        port_dropdown.addItem("Select Port")
        port_dropdown.setMinimumSize(100, 0)

        # Create the baud rate dropdown
        baud_dropdown = QComboBox()
        baud_dropdown.addItem("Baud Rate")
        for rate in baud_rates:
            baud_dropdown.addItem(rate)
        baud_dropdown.setMinimumSize(100, 0)

        # Create a "Connect" button
        connect_button = QPushButton('Connect', self)
        connect_button.clicked.connect(self.connect)

        # Create a "Jog up" button
        jog_up_button = QPushButton('UP', self)
        jog_up_button.clicked.connect(self.jogUp)

        # Create a "Jog down" button
        jog_down_button = QPushButton('DOWN', self)
        jog_down_button.clicked.connect(self.jogDown)

        # Create the clear button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.on_clear)

        # Create the text box
        text_box = QTextEdit()

        # Create a vertical layout to hold the widgets
        layout = QVBoxLayout()
        layout.addChildWidget(scan_button)
        layout.addChildWidget(port_dropdown)
        layout.addChildWidget(baud_dropdown)
        layout.addChildWidget(connect_button)
        layout.addChildWidget(text_box)
        layout.addChildWidget(clear_button)

        # Set the central widget to the layout
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def connect(self):
        # Get the serial port and baud rate from the line edits
        self.serial_port = self.serial_port_edit.text()
        self.baud_rate = int(self.baud_rate_edit.text())

        # Open the serial port
        self.serial = serial.Serial(self.serial_port, self.baud_rate)

        # Start a thread to read incoming data from the serial port
        t = threading.Thread(target=self.readSerial)
        t.start()

    def on_scan(self):
        port_dropdown.clear()
        ports = list(serial.tools.list_ports.comports())
        # print(ports)
        for port, _, _ in ports:
            self.port_dropdown.addItem(port)

    def on_clear(self):
        self.text_box.clear()

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
