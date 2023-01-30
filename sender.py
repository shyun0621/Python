import tkinter as tk
import tkinter.ttk as ttk
import serial
import threading
import signal
import RPi.GPIO as GPIO
from time import sleep

PACKET_START_IDX=226
PACKET_END_IDX=227
COMMAND_RTD_SWITCH=0
COMMAND_DOORSW_SWITCH=1
COMMAND_DOORLOCK_SWITCH=2
COMMAND_PROBE_SWITCH=3
COMMAND_MISWIRE_SWITCH=4
COMMAND_RTD_FAHRENHEIT=6
COMMAND_PROBE_FAHRENHEIT=7
DATA_SWITCH_ON=1
DATA_SWITCH_OFF=0
buzzerPin=14

rtd = [
     32,  60,  80,  90, 100, 140, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270,
    280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 
    450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610,
    620, 650, 700, 750, 800, 825, 850, 875, 900, 950, 1000
]

probe = [
      0,   5,  10,  15,  20,  25,  30,  35,  40,  45,  50,  55,  60,  65,  70,  75,  80,
     85,  90,  95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 
    170, 175, 180, 185, 190, 195, 200
]

class Buzz:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(buzzerPin, GPIO.OUT)
        self.buzz = GPIO.PWM(buzzerPin, 440)
    
    def getBuzz(self):
        return self.buzz
    
    def buzzerPlay(self, freq, duty_cycle, duration):
        self.buzz.start(duty_cycle)
        self.buzz.ChangeFrequency(freq)
        sleep(duration)
        self.buzz.stop()

    def down_sound(self):
        print("down_sound")
        self.buzzerPlay(440, 95, 0.2)
        sleep(0.05)
        self.buzzerPlay(220, 95, 0.2)

    def up_sound(self):
        print("down_sound")
        self.buzzerPlay(220, 95, 0.2)
        sleep(0.05)
        self.buzzerPlay(440, 95, 0.2)

class Serial:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyAMA1',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )        

    def writeGEACommand(self, value):
        print(value)
        if type(value) is bool:
            self.ser.write(str(value).encode())
        elif type(value) is str:
            self.ser.write(value.encode())
        else:
            self.ser.write(value)

    def getSerial(self):
        return self.ser

class UI:
    def draw(self):
        frame_rtd_cb = tk.LabelFrame(root, text = "RTD")
        frame_probe_cb = tk.LabelFrame(root, text = "PROBE")
        frame_rtd = tk.LabelFrame(root, text = "RTD")
        frame_doorsw = tk.LabelFrame(root, width=8, text = "DOOR SW")
        frame_doorlock = tk.LabelFrame(root, width=8, text = "DOOR LOCK")
        frame_probe = tk.LabelFrame(root, width=8, text = "PROBE")
        frame_miswire = tk.LabelFrame(root, width=8, text = "MISWIRE")
        
        frame_rtd_cb.grid(row=1, column=1, rowspan=3, columnspan=5, padx=10, pady=10)
        frame_probe_cb.grid(row=3, column=1, rowspan=3, columnspan=5)
        frame_rtd.grid(row=1, column=6, padx=10, pady=10)
        frame_doorsw.grid(row=2, column=6)
        frame_doorlock.grid(row=3, column=6)
        frame_probe.grid(row=4, column=6)
        frame_miswire.grid(row=5, column=6)

        cb_rtd = ttk.Combobox(frame_rtd_cb, height=5, values=rtd)
        cb_rtd.set("Select RTD(F)")
        cb_rtd.pack()
        cb_rtd.bind("<<ComboboxSelected>>", rtd_changed)
        cb_probe = ttk.Combobox(frame_probe_cb, height=5, values=probe)
        cb_probe.set("Select PROBE(F)")
        cb_probe.pack()
        cb_probe.bind("<<ComboboxSelected>>", probe_changed)

        btn_rtd_on = tk.Radiobutton(frame_rtd, text="on", width=7, value=True, variable=rtd_var, command=check_rtd).pack()
        btn_rtd_off = tk.Radiobutton(frame_rtd, text="off", width=7, value=False, variable=rtd_var, command=check_rtd).pack()

        btn_doorsw_on = tk.Radiobutton(frame_doorsw, text="on", width=7, value=True, variable=doorsw_var, command=check_doorsw).pack()
        btn_doorsw_off = tk.Radiobutton(frame_doorsw, text="off", width=7, value=False, variable=doorsw_var, command=check_doorsw).pack()
        btn_doorlock_on = tk.Radiobutton(frame_doorlock, text="on", width=7, value=True, variable=doorlock_var, command=check_doorlock).pack()
        btn_doorlock_off = tk.Radiobutton(frame_doorlock, text="off", width=7, value=False, variable=doorlock_var, command=check_doorlock).pack()

        btn_probe_on = tk.Radiobutton(frame_probe, text="on", width=7, value=True, variable=probe_var, command=check_probe).pack()
        btn_probeoff = tk.Radiobutton(frame_probe, text="off", width=7, value=False, variable=probe_var, command=check_probe).pack()

        btn_miswire_on = tk.Radiobutton(frame_miswire, text="on", width=7, value=True, variable=miswire_var, command=check_miswire).pack()
        btn_miswire_off = tk.Radiobutton(frame_miswire, text="off", width=7, value=False, variable=miswire_var, command=check_miswire).pack()

def handler(signum, frame):
    global exitThread
    print("Thread stop")
    exitThread = True

def readThread(ser):
    global exitThread
    while not exitThread:
        if ser.readable():
            res = ser.readline().decode('utf-8')
            if res:
                print(res)

def gen_packet(command, val):
    packet = '{:02X}'.format(PACKET_START_IDX) + '{:02X}'.format(command) + '{:04X}'.format(int(val)) + '{:02X}'.format(PACKET_END_IDX)
    return packet

def gen_packet_int(command, val):
    packet = bytearray(5)
    packet[0] = PACKET_START_IDX & 0x000000ff
    packet[1] = command & 0x000000ff
    packet[2] = int(val).to_bytes(2, 'big')[0]
    packet[3] = int(val).to_bytes(2, 'big')[1]
    packet[4] = PACKET_END_IDX & 0x000000ff
    return packet

def rtd_changed(event):
#    packet = gen_packet(COMMAND_RTD_FAHRENHEIT, event.widget.get())
    packet = gen_packet_int(COMMAND_RTD_FAHRENHEIT, event.widget.get())
    serial.writeGEACommand(packet)

def probe_changed(event):
    packet = gen_packet(COMMAND_PROBE_FAHRENHEIT, event.widget.get())
    serial.writeGEACommand(packet)

def check_rtd():
    if rtd_var.get():
        packet = gen_packet(COMMAND_RTD_SWITCH, DATA_SWITCH_ON)
        serial.writeGEACommand(packet);   
    else:
        packet = gen_packet(COMMAND_RTD_SWITCH, DATA_SWITCH_OFF)
        serial.writeGEACommand(packet);   

def check_doorsw():
    if doorsw_var.get():
        packet = gen_packet(COMMAND_DOORSW_SWITCH, DATA_SWITCH_ON)
        serial.writeGEACommand(packet);   
    else:
        packet = gen_packet(COMMAND_DOORSW_SWITCH, DATA_SWITCH_OFF)
        serial.writeGEACommand(packet);   

def check_doorlock():
    if doorlock_var.get():
        packet = gen_packet(COMMAND_DOORLOCK_SWITCH, DATA_SWITCH_ON)
        serial.writeGEACommand(packet);   
    else:
        packet = gen_packet(COMMAND_DOORLOCK_SWITCH, DATA_SWITCH_OFF)
        serial.writeGEACommand(packet);   

def check_probe():
    if probe_var.get():
        packet = gen_packet(COMMAND_PROBE_SWITCH, DATA_SWITCH_ON)
        serial.writeGEACommand(packet);   
    else:
        packet = gen_packet(COMMAND_PROBE_SWITCH, DATA_SWITCH_OFF)
        serial.writeGEACommand(packet);   

def check_miswire():
    if miswire_var.get():
        packet = gen_packet(COMMAND_MISWIRE_SWITCH, DATA_SWITCH_ON)
        serial.writeGEACommand(packet);   
    else:
        packet = gen_packet(COMMAND_MISWIRE_SWITCH, DATA_SWITCH_OFF)
        serial.writeGEACommand(packet);   

root = tk.Tk()
serial = Serial()

rtd_sc_var = tk.IntVar()
probe_sc_var = tk.IntVar()
rtd_var = tk.BooleanVar()
doorsw_var = tk.BooleanVar()
doorlock_var = tk.BooleanVar()
probe_var = tk.BooleanVar()
miswire_var = tk.BooleanVar()
exitThread = False
buzz = Buzz()

def main():
    root.title("Loadbox Emulator")
    root.geometry("500x400+200+200")
    
    ui = UI()
    ui.draw()

    signal.signal(signal.SIGINT|signal.SIGKILL, handler)    
    thread = threading.Thread(target=readThread, args=[serial.getSerial()])
    thread.start()

    root.mainloop()
    
if __name__ == "__main__":
	main()
