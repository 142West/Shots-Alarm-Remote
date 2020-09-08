import socket
import struct
import time
import atexit

from gpiozero import LED, Button

INET = ('shots-alarm.142.life', 8675)  # The server's hostname or IP address

led = LED(17)
pull_station = Button(27, bounce_time=.01)


class ShotsRemote:

    def __init__(self):
        self.connected = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(False)

    def shotsGo(self):
        if self.connected:
            print("Alarm Triggered and request sent")
            try:
                self.s.sendall(b'ACTIVATE')
                ack = self.s.recv(1024)
                if not ack:
                    self.connected = False
                    self.connect(True)

            except:
                self.connected = False
                self.connect(True)

        else:
            print("Alarm Triggered but connected = " + self.connected)

    def shotsAbort(self):
        if self.connected:
            print("Canceling Alarm")
            try:
                self.s.sendall(b'ABORT')
                ack = self.s.recv(1024)
                if not ack:
                    self.connected = False
                    self.connect(True)

            except:
                self.connected = False
                self.connect(True)
        else:
            print("Alarm Canceled but connected = " + self.connected)

    def shutdown(self):
        self.s.close()
        exit()

    def connect(self, reconnect):
        if reconnect:
            self.s.close()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while not self.connected:
                try:
                    self.s.connect(INET)
                    led.on()
                    self.connected = True
                    print("Connected to " + INET[0])

                except socket.error as exc:
                    print("Caught exception socket.error : %s" % exc)
                    print("Trying to connect to " + INET[0] + "...")
                    led.on()
                    time.sleep(.5)
                    led.off()
                    time.sleep(.5)


remote = ShotsRemote()
pull_station.when_pressed = remote.shotsGo
pull_station.when_released = remote.shotsAbort
atexit.register(remote.shutdown)

while 1:
    time.sleep(0.5)
