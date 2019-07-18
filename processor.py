from tools import *


class Processor:
    VALUES_RESERVED = 100
    DEBUG = False
    DEFAULT_MAX_MEMORY = 10000

    def __init__(self, memory_size=DEFAULT_MAX_MEMORY):
        self.registers = {}
        self.memory = [0 for _ in
                       range(memory_size + Processor.VALUES_RESERVED)]  # 100 values are reserved for variables
        self.flags = {}
        self.i = 0  # instruction pointer
        self.output = ""
        self.lines = []
        self.dic_flags = {}
        self.memory_used = Processor.VALUES_RESERVED
        self.table = []

        # some stats
        self.counters = {"ins": 0}

        # sauv parameters
        self.text = ""
        self.pattern = ""
        self.strings = []

        # actions to do for each instruction
        self.dic = dict(mov=lambda a, b: self.action(a, b, self.reg_set, self.mem_set),
                        add=lambda a, b: self.action(a, b, self.reg_add, self.mem_add),
                        sub=lambda a, b: self.action(a, b, self.reg_sub, self.mem_sub),
                        mul=lambda a, b: self.action(a, b, self.reg_mul, self.mem_mul),
                        jmp=lambda a, b: self.jmp(self.dic_flags[is_flag(a)] + 1), cmp=lambda a, b: self.reg_cmp(a, b),
                        jcmp=lambda a, b: self.je(self.dic_flags[is_flag(a)]),
                        jl=lambda a, b: self.jl(self.dic_flags[is_flag(a)]),
                        je=lambda a, b: self.je(self.dic_flags[is_flag(a)]),
                        jne=lambda a, b: self.jne(self.dic_flags[is_flag(a)]),
                        jg=lambda a, b: self.js(self.dic_flags[is_flag(a)]),
                        call=lambda a, b: self.call(a))

    def init_prog(self, proglines, dic_flags):
        self.lines = proglines
        self.dic_flags = dic_flags

    def execute(self):
        ins = self.lines[self.i]
        if Processor.DEBUG:
            print("[CPU] execute ", ins)

        if ins[0][0] == '.':
            self.i += 1
            # self.execute()
            return

        # to prevent anomaly
        if len(ins) == 1:
            self.dic[ins[0]](0, 0)
        elif len(ins) == 2:
            self.dic[ins[0]](ins[1], 0)
        else:
            self.dic[ins[0]](ins[1], ins[2])
        self.counters["ins"] += 1
        self.debug()

    def inject_params(self, text, pattern):
        self.reg_set("si", len(text))
        for i in range(len(text)):
            self.mem_set(i + self.memory_used, ord(text[i]))
        self.reg_set("di", self.memory_used)

        self.reg_set("cx", len(pattern))
        for i in range(len(pattern)):
            self.mem_set(i + self.memory_used + len(text), ord(pattern[i]))
        self.reg_set("dx", self.memory_used + len(text))

        self.memory_used += len(text) + len(pattern)

        self.text = text
        self.pattern = pattern

    def inject_table(self, table):
        if len(table) == 0:
            return
        for i in range(len(table)):
            self.mem_set(i + self.memory_used, table[i])
        self.reg_set("sp", self.memory_used)

        self.memory_used += len(table)

    def attach_strings(self, attached):
        self.strings = attached[:]

    def memory_ptr(self, mem):
        try:
            ptr = int(mem[1:])
        except ValueError:
            ptr = self.reg_get(mem[1:])
        return ptr

    def action(self, A, B, reg_action, mem_action):
        if type(B) == int:
            if A[0] == 'm':
                mem_action(self.memory_ptr(A), B)
            else:
                reg_action(A, B)
        elif B[0] == 'm':
            reg_action(A, self.mem_get(self.memory_ptr(B)))
        elif A[0] == 'm':
            mem_action(self.memory_ptr(A), self.reg_get(B))
        else:
            reg_action(A, self.reg_get(B))
        self.i += 1

    def reset(self):
        self.memory = [0 for _ in range(len(self.memory))]
        for i in self.counters:
            self.counters[i] = 0
        self.registers.clear()
        self.i = 0
        self.flags.clear()
        self.memory_used = Processor.VALUES_RESERVED
        self.inject_params(self.text, self.pattern)
        self.inject_table(self.table)

    def reg_set(self, reg, val):
        self.registers[reg] = val

    def reg_get(self, reg):
        if reg not in self.registers:
            self.registers[reg] = 0
        return self.registers[reg]

    def reg_add(self, reg, val):
        self.reg_set(reg, self.reg_get(reg) + val)

    def reg_addreg(self, regA, regB):
        self.reg_add(regA, self.reg_get(regB))

    def reg_sub(self, reg, val):
        self.reg_set(reg, self.reg_get(reg) - val)

    def reg_mul(self, reg, val):
        self.reg_set(reg, self.reg_get(reg) * val);

    def reg_mulreg(self, A, B):
        self.reg_mul(A, self.reg_get(B));

    def reg_cmp(self, regA, regB):
        self.flags['cmp'] = (self.reg_get(regA) - self.reg_get(regB))
        self.i += 1

    def mem_set(self, i, val):
        self.memory[i] = val

    def mem_get(self, i):
        return self.memory[i]

    def mem_add(self, i, val):
        self.mem_set(i, self.mem_get(i) + val)

    def mem_sub(self, i, val):
        self.mem_set(i, self.mem_get(i) - val)

    def mem_mul(self, i, val):
        self.mem_set(i, self.mem_get(i) * val);

    def out(self):
        print(self.output)
        self.output = ""

    def jmp(self, where):
        self.i = where

    def cmpcond(self, cond):
        if 'cmp' not in self.flags:
            return False
        tmp = self.flags['cmp']
        del self.flags['cmp']
        if cond(tmp):
            return True
        return False

    def je(self, where):
        if self.cmpcond(lambda i: i == 0):
            self.jmp(where)
        self.i += 1

    def jne(self, where):
        if self.cmpcond(lambda i: i != 0):
            self.jmp(where)
        self.i += 1

    def jl(self, where):
        if self.cmpcond(lambda i: i < 0):
            self.jmp(where)
        self.i += 1

    def js(self, where):
        if self.cmpcond(lambda i: i > 0):
            self.jmp(where)
        self.i += 1

    def get_ptr(self):
        return self.i

    def nop(self):
        pass

    def call(self, fct):
        args = [self.reg_get("di"), self.reg_get("si"), self.reg_get("dx"), self.reg_get("cx")]
        args += [self.reg_get(str(j)+"x") for j in range(8,15) if str(j)+"x" in self.registers]

        if fct == "printf":
            self.fct_printf(args)
        else:
            print("Call", fct, "unsupported")

        self.i += 1

    def fct_printf(self, args):
        st = self.strings[args[0]]
        args = args[1:]
        tmp = st.split("%")[1:]
        for j in range(len(st.split("%")[1:])):
            if tmp[j][0] == 's': args[j] = self.strings[args[j]]
        self.output = st % tuple(args[:st.count("%")])
        print("[OUT] ", self.output)

    def debug(self):
        if not Processor.DEBUG:
            return
        print("[CPU] Registers :", self.registers)
        print("[CPU] Flags :", self.flags)
        print("[CPU] Reserved Memory [0..", Processor.VALUES_RESERVED - 1, "] :",
              self.memory[:Processor.VALUES_RESERVED])
        print("[CPU] Memory [", Processor.VALUES_RESERVED, "..", Processor.VALUES_RESERVED + 50, "] :",
              self.memory[Processor.VALUES_RESERVED:Processor.VALUES_RESERVED + 50])
        print("[CPU] Output buffer : ", self.output)
        print("[CPU] Instruction pointer :", self.i)
        print("[CPU] Counters :", self.counters)
        print()

    def graphical_output(self, ptr, buf, count):
        ptr.set("Ins ptr:" + str(self.i))
        buf.set(self.output)
        j = 0
        for i in self.counters:
            count[j].set(i + ":" + str(self.counters[i]))
            j += 1
