from processor import *
from tkinter import *


class CPU_Window:

    def __init__(self, cpu):
        self.cpu = cpu
        self.cpuWindow = None
        self.frame = None
        self.f_mem = None
        self.output_var = StringVar(value="Empty")
        self.f_main = None
        self.grid = [None] * 32
        self.grid_mem = [None] * 100

    def open(self):
        if self.cpuWindow:
            return

        self.cpuWindow = Tk()
        self.cpuWindow.wm_attributes("-topmost", 1)

        self.cpuWindow.title("Processor Window")
        self.cpuWindow.configure(background="#aaadaf")

        self.f_main = Frame(self.cpuWindow, width=500, height=500, bd=1, padx=7, pady=5, bg="#687382")
        self.f_main.pack(side=TOP, expand=False)

        Label(self.f_main, text="Registers").pack(side=TOP)

        self.frame = Frame(self.f_main, width=500, height=500, bd=1, padx=7, pady=5, bg="#687382")
        self.frame.pack(side=TOP, expand=False)

        Label(self.f_main, text="Output Buffer").pack(side=TOP)

        tmp = Frame(self.f_main, width=500, height=500, bd=1, padx=7, pady=5, bg="#687382")
        tmp.pack(side=TOP, expand=True)
        Label(tmp, textvariable=self.output_var, padx=5, pady=3).pack(side=TOP, expand=True)

        Label(self.f_main, text="Local Memory").pack(side=TOP)

        self.f_mem = Frame(self.f_main, width=500, bd=1, padx=7, pady=5, bg="#687382")
        self.f_mem.pack(side=TOP, expand=False)

        self.maj()

    def clear(self):
        self.grid = [None]*32
        self.grid_mem = [None] * 100
        self.frame = None
        self.f_mem = None

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
                b = Entry(self.frame, width=5)
                b.insert(0, str(lst[j]))
                b.grid(row=0, column=j, sticky=E+W)
                c = Entry(self.frame, width=5)
                c.insert(0, str(self.cpu.registers[lst[j]]))
                c.grid(row=1, column=j, sticky=E+W)
                self.grid[j] = (b, c)
            tmp = self.grid[j]
            tmp[0].delete(0, len(tmp[0].get()))
            tmp[0].insert(0, str(lst[j]))
            tmp[1].delete(0, len(tmp[1].get()))
            tmp[1].insert(0, str(self.cpu.registers[lst[j]]))

    def maj_mem(self):
        lst = self.cpu.memory[:100]
        if self.cpuWindow is None:
            return
        i = 0
        for j in range(len(lst)):
            if self.grid_mem[j] is None:
                b = Entry(self.f_mem, width=5)
                b.insert(0, str(self.cpu.memory[j]))
                b.grid(column=j%20, row=j//20, padx=0)
                self.grid_mem[j] = b
            tmp = self.grid_mem[j]
            tmp.delete(0, len(tmp.get()))
            tmp.insert(0, str(self.cpu.memory[j]))


    def maj_output(self):
        if len(self.cpu.output) >= 1:
            self.output_var.set(self.cpu.output)

    def maj(self):
        try:
            self.maj_registers()
            self.maj_mem()
            self.maj_output()
        except:
            self.clear()