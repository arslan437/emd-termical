import wx
import serial
import serial.tools.list_ports
import threading
import time

baud_rates = ["9600", "19200", "28800", "38400", "57600", "76800", "115200"]

class MyFrame(wx.Frame):
    def __init__(self):
        # Create the frame
        wx.Frame.__init__(self, None, title="EMD Control")

        self.serial_thread_flag = False
        self.scroll_flag = False

        # Create a panel to hold the widgets
        panel = wx.Panel(self)

        # Create the port dropdown
        #self.port_dropdown = wx.ComboBox(panel, choices=port_names)
        self.port_dropdown = wx.ComboBox(panel,value = "Select Port")
        self.port_dropdown.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_port_dropdown)
        self.port_dropdown.SetMinSize((100, -1))

        # Create the baud rate dropdown
        self.baud_dropdown = wx.ComboBox(panel, value = "Baud Rate", choices=baud_rates)
        self.baud_dropdown.SetMinSize((100, -1))

        # Create the connect button
        self.connect_button = wx.Button(panel, label="Connect")
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect)
        
        # Create the clear button
        self.clear_button = wx.Button(panel, label="Clear")
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        # Create the text box
        self.text_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        # Create the checkbox
        self.checkbox = wx.CheckBox(panel, label="Auto Scroll")
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_toggled)

        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(self.port_dropdown, 0, wx.ALL, 5)
        horizontal_sizer.Add(self.baud_dropdown, 0, wx.ALL, 5)
        horizontal_sizer.Add(self.connect_button, 0, wx.ALL, 5)

        # Create a vertical sizer to hold the horizontal sizer and the text box
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        vertical_sizer.Add(horizontal_sizer, 0, wx.ALL, 5)
        vertical_sizer.Add(self.text_box, 1, wx.EXPAND|wx.ALL, 5)

        btn_clear_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_clear_row_sizer.Add(self.clear_button, 0, wx.ALL, 5)
        # btn_clear_row_sizer.Add(self.checkbox, 0, wx.ALL, 5)
        btn_clear_row_sizer.Add(self.checkbox, 1, wx.ALIGN_CENTER, 5)

        vertical_sizer.Add(btn_clear_row_sizer, 0, wx.ALL, 5)

        # Set the panel's sizer
        panel.SetSizer(vertical_sizer)
        
    def on_connect(self, event):
       # Check if a valid port and baud rate are selected
        if not self.is_valid_port(self.port_dropdown):
            wx.MessageBox("Please select a valid port")
            return
        if not self.is_valid_baud(self.baud_dropdown):
            wx.MessageBox("Please select a valid baud rate")
            return

        # Get the selected port and baud rate
        port = self.port_dropdown.GetValue()
        baud = self.baud_dropdown.GetValue()
        
        # Try to open a connection to the serial port
        try:
            self.ser = serial.Serial(port, baudrate=baud, timeout=3)
        except serial.serialutil.SerialException as e:
            # Show an error message if the connection fails
            wx.MessageBox(str(e))
            return
        
        # Change the button label to "Disconnect"
        self.connect_button.SetLabel("Disconnect")
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_disconnect)

        self.serial_thread_flag = True

        # Start the serial_reader thread
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.start()

    def on_disconnect(self, event):
        self.serial_thread_flag = False

        # Close the serial port connection
        self.ser.close()
        
        # Change the button label to "Connect"
        self.connect_button.SetLabel("Connect")
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect)

        # Stop the serial_reader thread
        # self.serial_thread.stop()
            
    def on_port_dropdown(self, event):
        # Get a list of available serial ports
        ports = serial.tools.list_ports.comports()
        port_names = [p.device for p in ports]

        # Update the choices in the dropdown
        self.port_dropdown.Clear()
        self.port_dropdown.Append(port_names)

    def on_clear(self, event):
        self.text_box.Clear()

    def serial_reader(self):
        # Continuously read data from the serial port and update the text box
        while True and self.serial_thread_flag:
            data = self.ser.readline()
            if data:
                wx.CallAfter(self.text_box.AppendText, data.decode("utf-8"))
                # If the checkbox is not checked, disable the auto scroll feature
                if not self.scroll_flag:
                    self.text_box.SetInsertionPoint(self.text_box.GetLastPosition())
        
    def is_valid_port(self, combo_box):
        # Get the current selection in the combobox
        selection = combo_box.GetValue()

        # Get a list of available serial ports
        ports = serial.tools.list_ports.comports()
        port_names = [p.device for p in ports]

        # Return True if the selection is in the list of available ports, False otherwise
        return selection in port_names

    
    def is_valid_baud(self, combo_box):
        # Get the current selection in the combobox
        selection = combo_box.GetValue()

        # Check if the selection is a valid baud rate
        if selection in baud_rates:
            return True
        else:
            return False

    def on_checkbox_toggled(self, event):
        # Get the current state of the checkbox
        self.scroll_flag = event.IsChecked()

    def on_close(self, event):
        # Stop the serial reader thread
        self.serial_thread_flag = False
        self.serial_thread.join()

        # Close the serial port connection
        try:
            self.ser.close()
        except Exception as e:
            print(e)
        

app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()
