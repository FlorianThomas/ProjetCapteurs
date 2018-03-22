import re
import serial
import http.client
# from ../Web/Apply/app import app, db
import datetime

PORT = ''
from serial.tools import list_ports
ports = list(list_ports.comports())
# ports = list(serial.tools.list_ports.comports())
print(ports)
for p in ports:
    if "Arduino" in p[1]:
        PORT = p[0]
        print(p)

SERVER = "localhost:5000"

ser = serial.Serial(port=PORT, baudrate=115200)

while True:
    a = ser.readline().decode('latin-1')
    reg_capt = re.search("([0-9]+) @ (.+)", a)
    reg_pos = re.search("([0-9]+) % (.+)", a)
    if reg_capt or reg_pos:
        sender, msg = reg_capt.groups()
        sender = "0" + sender[-9:]
        print(sender + " : " + msg)
        capteur = 2
        # capteur = get_capteur_phone(sender)
        if capteur != None:
            if reg_capt:
                # d = Donnee(value   = msg[2:],
                #            date    = datetime.strptime(datetime.datetime.now(), '%b %d %Y %I:%M%p'),
                #            capteur = capteur.get_id(),
                #            parterre = capteur.get_parterre())
                # capteur.add_data(d)
                # db.session.commit()
                print("Mesure")
            else:
                msg=msg[2:]
                msg.split(";")
                # capteur.set_X(float(msg[0]))
                # capteur.set_Y(float(msg[1]))
                # db.session.commit()
                print(msg)
# from winregistry import WinRegistry as winreg
# import itertools
#
# def enumerate_serial_ports():
#     """ Uses the Win32 registry to return an
#         iterator of serial (COM) ports
#         existing on this computer.
#     """
#     path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
#     try:
#         key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
#     except WindowsError:
#         raise IterationError
#
#     for i in itertools.count():
#         try:
#             val = winreg.EnumValue(key, i)
#             yield str(val[1])
#         except EnvironmentError:
#             break
# import re
#
# def full_port_name(portname):
#     """ Given a port-name (of the form COM7,
#         COM12, CNCA0, etc.) returns a full
#         name suitable for opening with the
#         Serial class.
#     """
#     m = re.match('^COM(\d+)$', portname)
#     if m and int(m.group(1)) < 10:
#         return portname
#     return '\\\\.\\' + portname
#
# import sys
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
#
# import serial
# from serial.serialutil import SerialException
# from serialutils import full_port_name, enumerate_serial_ports
#
#
# class ListPortsDialog(QDialog):
#     def __init__(self, parent=None):
#         super(ListPortsDialog, self).__init__(parent)
#         self.setWindowTitle('List of serial ports')
#
#         self.ports_list = QListWidget()
#         self.tryopen_button = QPushButton('Try to open')
#         self.connect(self.tryopen_button, SIGNAL('clicked()'),
#             self.on_tryopen)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.ports_list)
#         layout.addWidget(self.tryopen_button)
#         self.setLayout(layout)
#
#         self.fill_ports_list()
#
#     def on_tryopen(self):
#         cur_item = self.ports_list.currentItem()
#         if cur_item is not None:
#             fullname = full_port_name(str(cur_item.text()))
#             try:
#                 ser = serial.Serial(fullname, 38400)
#                 ser.close()
#                 QMessageBox.information(self, 'Success',
#                     'Opened %s successfully' % cur_item.text())
#             except SerialException:
#                 QMessageBox.critical(self, 'Failure',
#                     'Failed to open %s:\n%s' % (
#                         cur_item.text(), e))
#
#     def fill_ports_list(self):
#         for portname in enumerate_serial_ports():
#             self.ports_list.addItem(portname)
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     form = ListPortsDialog()
#     form.show()
#     app.exec_()
