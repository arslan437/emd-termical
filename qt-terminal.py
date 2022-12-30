import serial
import serial.tools.list_ports
import threading
import time
import sys

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout, 
                             QVBoxLayout, QTextEdit, QPushButton, QCheckBox)

baud_rates = ["9600", "19200", "28800", "38400", "57600", "76800", "115200"]

class MyFrame(QFrame):
    def __init__(self):
        # Create the frame
        super().__init__()
        self.setWindowTitle("EMD Control")

        self.serial_thread_flag = False
        self.scroll_flag = False
        self.serial_port = None

        # Create the port dropdown
        self.port_dropdown = QComboBox()
        self.port_dropdown.addItem("Select Port")
        # self.port_dropdown.activated.connect(self.on_port_dropdown)
        self.port_dropdown.setMinimumSize(100, 0)

        # Create the baud rate dropdown
        self.baud_dropdown = QComboBox()
        self.baud_dropdown.addItem("Baud Rate")
        for rate in baud_rates:
            self.baud_dropdown.addItem(rate)
        self.baud_dropdown.setMinimumSize(100, 0)

        # Create the connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect)
        
        # Create the scan button
        self.scan_button = QPushButton("Scan Ports")
        self.scan_button.clicked.connect(self.on_scan)
        
        # Create the clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear)

        # Create the text box
        self.text_box = QTextEdit()

        # Create the checkbox
        self.checkbox = QCheckBox("Auto Scroll")
        self.checkbox.stateChanged.connect(self.on_checkbox_toggled)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.scan_button)
        horizontal_layout.addWidget(self.port_dropdown)
        horizontal_layout.addWidget(self.baud_dropdown)
        horizontal_layout.addWidget(self.connect_button)

        # Create a vertical layout to hold the horizontal layout and the text box
        vertical_layout = QVBoxLayout(self)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.text_box)

        btn_clear_row_layout = QHBoxLayout()
        btn_clear_row_layout.addWidget(self.clear_button)
        btn_clear_row_layout.addWidget(self.checkbox, Qt.AlignCenter)
        vertical_layout.addLayout(btn_clear_row_layout)
        
    def on_connect(self):
        # Check if a valid port and baud rate are selected
        if not self.is_valid_port(self.port_dropdown):
            QMessageBox.warning(self, "Error", "Please select a valid port")
            return
        if not self.is_valid_baud(self.baud_dropdown):
            QMessageBox.warning(self, "Error", "Please select a valid baud rate")
            return

        # Get the selected port and baud rate
        port = self.port_dropdown.currentText()
        baud = self.baud_dropdown.currentText()
        
        # Close the serial port if it is open
        if self.serial_port is not None and self.serial_port.is_open:
            self.serial_port.close()
            
        # Try to open the serial port
        try:
            self.serial_port = serial.Serial(port, baud)
        except serial.serialutil.SerialException as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        
        # Create and start the serial thread
        self.serial_thread = SerialThread(port, baud)
        self.serial_thread.start()
        self.serial_thread_flag = True
        
        # Update the UI
        self.port_dropdown.setEnabled(False)
        self.baud_dropdown.setEnabled(False)
        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.disconnect(self.on_connect)
        self.connect_button.clicked.connect(self.on_disconnect)

    def on_data_received(self):
        print("data")
    def on_disconnect(self):
        # Stop the serial thread
        self.serial_thread.stop()
        self.serial_thread_flag = False
        
        # Close the serial port
        self.serial_port.close()
        
        # Update the UI
        self.port_dropdown.setEnabled(True)
        self.baud_dropdown.setEnabled(True)
        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect(self.on_disconnect)
        self.connect_button.clicked.connect(self.on_connect)
    
    def on_scan(self):
        self.port_dropdown.clear()
        ports = list(serial.tools.list_ports.comports())
        # print(ports)
        for port, _, _ in ports:
            self.port_dropdown.addItem(port)
    
    def on_clear(self):
        self.text_box.clear()
        
    def on_checkbox_toggled(self):
        self.scroll_flag = self.checkbox.isChecked()
        
    def is_valid_port(self, port_dropdown):
        return port_dropdown.currentIndex() > 0
    
    def is_valid_baud(self, baud_dropdown):
        return baud_dropdown.currentIndex() > 0

class SerialThread(QThread):
    data_received = pyqtSignal(str)  # Define the data_received signal

    def __init__(self, port, baud):
        # Initialize the thread
        super().__init__()
        self.port = port
        self.baud = baud
        self.serial_thread_flag = False
    
    def run(self):
        # Open the serial port
        self.serial_port = serial.Serial(self.port, self.baud, timeout=1)
        self.serial_thread_flag = True
        while self.serial_thread_flag:
            # Read data from the serial port
            data = self.serial_port.readline().decode('utf-8')
            if data:
                # Emit the data_received signal with the received data
                self.data_received.emit(data)
    
    def stop(self):
        self.serial_thread_flag = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    frame = MyFrame()
    frame.show()
    sys.exit(app.exec_())