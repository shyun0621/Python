import tkinter as tk
import serial

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
        # self.ser.write(value)

class UI:
    def draw(self):
        scale_rtd = tk.LabelFrame(root,text = "RTD")
        scale_probe = tk.LabelFrame(root, text = "RROBE")
        frame_rtd = tk.LabelFrame(root, text = "RTD")
        frame_doorsw = tk.LabelFrame(root, width=8, text = "DOOR SW")
        frame_doorlock = tk.LabelFrame(root, width=8, text = "DOOR LOCK")
        frame_probe = tk.LabelFrame(root, width=8, text = "PROBE")
        frame_miswire = tk.LabelFrame(root, width=8, text = "MISWIRE")
        
        scale_rtd.grid(row=1, column=1, rowspan=3, columnspan=5, padx=10, pady=10)
        scale_probe.grid(row=2, column=1, rowspan=3, columnspan=5)
        frame_rtd.grid(row=1, column=6, padx=10, pady=10)
        frame_doorsw.grid(row=2, column=6)
        frame_doorlock.grid(row=3, column=6)
        frame_probe.grid(row=4, column=6)
        frame_miswire.grid(row=5, column=6)

        sc_rtd = tk.Scale(scale_rtd, variable=rtd_sc_var, command=select_rtd_scale, orient="horizontal", showvalue=True, tickinterval=0, to=450, length=300).pack()
        sc_probe = tk.Scale(scale_probe, variable=probe_sc_var, command=select_probe_scale, orient="horizontal", showvalue=True, tickinterval=0, to=450, length=300).pack()

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

def select_rtd_scale(val):
    serial.writeGEACommand(val);
    
def select_probe_scale(val):
    serial.writeGEACommand(val);

def check_rtd():
    serial.writeGEACommand(rtd_var.get());

def check_doorsw():
    serial.writeGEACommand(doorsw_var.get());

def check_doorlock():
    serial.writeGEACommand(doorlock_var.get());

def check_probe():
    serial.writeGEACommand(probe_var.get());

def check_miswire():
    serial.writeGEACommand(miswire_var.get());
   
root = tk.Tk()
serial = Serial()

rtd_sc_var = tk.IntVar()
probe_sc_var = tk.IntVar()
rtd_var = tk.BooleanVar()
doorsw_var = tk.BooleanVar()
doorlock_var = tk.BooleanVar()
probe_var = tk.BooleanVar()
miswire_var = tk.BooleanVar()

def main():
    root.title("Loadbox Emulator")
    root.geometry("500x400+200+200")
    
    ui = UI()
    ui.draw()
    
    root.mainloop()
    
if __name__ == "__main__":
	main()