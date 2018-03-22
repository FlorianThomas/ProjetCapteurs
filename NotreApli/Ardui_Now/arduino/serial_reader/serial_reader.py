import re
import serial
import http.client

PORT = ''

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Arduino" in p[1]:
        PORT = p[0]
        break

SERVER = "localhost:5000"

connection = http.client.HTTPConnection(SERVER)

ser = serial.Serial(port=PORT, baudrate=115200)

while True:
    a = ser.readline().decode('latin-1')
    reg_capt = re.search("([0-9]+) ? (.+)", a)
    reg_pos = re.search("([0-9]+) % (.+)", a)
    if reg_capt or reg_pos:
        if reg_capt:
            capteur = getCapteur(num)
            capteur.addDonnée(data)
        else:
            capteur.setPosition(pos)
        reg = reg_capt or reg_pos
        r_type = "measure" if reg_capt else "position"
        sender, msg = reg.groups()
        sender = "0" + sender[-9:]
        print(sender + " : " + msg)
        connection.request('GET', '/%s/%s/%s' % (r_type, sender, msg,))
        print(connection.getresponse().read().decode())
