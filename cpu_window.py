from processor import *
from tkinter import *


class CPU_Window:

    def __init__(self, cpu):
        self.cpu = cpu
        self.cpuWindow = None
        self.frame = None
        self.grid = [None] * 32

    def open(self):
        if self.cpuWindow:
            return

        self.cpuWindow = Tk()
        self.cpuWindow.wm_attributes("-topmost", 1)

        self.cpuWindow.title("Processor Window")
        self.cpuWindow.configure(background="#aaadaf")

        self.frame = Frame(self.cpuWindow, width=500, height=500, bd=1, padx=7, pady=5, bg="#687382")
        self.frame.pack(side=TOP, expand=False)

        self.maj()

    def clear(self):
        self.grid = [None]*32
        self.frame = None

    def close(self):
        if self.cpuWindow is None:
            return
        try:
            self.clear()
            self.cpuWindow.destroy()
            self.cpuWindow = None
        except:
            self.clear()
            self.cpuWindow = None
            return self.open()

    def onClick(self):
        if self.cpuWindow:
            self.close()
        else:
            self.open()

    def maj_registers(self):
        lst = list(self.cpu.registers)
        if self.cpuWindow is None:
            return
        for j in range(len(lst)):
            if j >= len(self.grid):
                break
            if self.grid[j] is None:
                b = Entry(self.frame)
                b.insert(0, str(lst[j]))
                b.grid(row=0, column=j)
                c = Entry(self.frame)
                c.insert(0, str(self.cpu.registers[lst[j]]))
                c.grid(row=1, column=j)
                self.grid[j] = (b, c)
            tmp = self.grid[j]
            tmp[0].delete(0, len(tmp[0].get()))
            tmp[0].insert(0, str(lst[j]))
            tmp[1].delete(0, len(tmp[1].get()))
            tmp[1].insert(0, str(self.cpu.registers[lst[j]]))

    def maj(self):
        try:
            self.maj_registers()
        except:
            self.clear()