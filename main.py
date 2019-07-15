from pipeline import *
from random import randint, seed

def kmp_table(s):
    T = [0 for _ in range(len(s) + 1)]
    T[0] = -1
    i = 0
    j = -1
    s = s + "0"
    while i < len(s) - 1:
        while j > -1 and s[i] != s[j]:
            j = T[j]
        i += 1
        j += 1
        if s[i] == s[j]:
            T[i] = T[j]
        else:
            T[i] = j
    return T


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("python3 main.py nasm_file.s")
        sys.exit(1)

    seed()
    blocs, lines, dic, strs = construct_blocs(sys.argv[1])
    window.title(base_title + " : " + sys.argv[1])

    strlines = list(map(lambda i: ' '.join(list(map(lambda j: str(j), i))), lines))
    reset()

    ######################## TEXT INJECTION ########################
    ### 2 <= TEXT_SIZE + |pattern| + 1 < Processor.DEFAULT_MAX_MEMORY
    pattern = "AAAAAAA"
    TEXT_SIZE = 150
    ALPH = string.ascii_letters
    ################################################################

    text = ''.join([ALPH[randint(0, len(ALPH) - 1)] for i in range(TEXT_SIZE)])
    kmpTable = kmp_table(pattern)

    cpu.init_prog(lines, dic)
    cpu.inject_params(text, pattern)
    cpu.attach_strings(strs)
    cpu.inject_table(kmpTable)
    cpu.debug()

    ######################################################################################
    ############################### Window Buttons & Canvas ##############################
    ######################################################################################

    frameButtons = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    frameButtons.pack(side=TOP)

    A = Button(frameButtons, text='Step Forward',
               command=lambda: next_step(blocs, lines, strlines)).pack(side=LEFT)
    B = Button(frameButtons, text='RUN', command=lambda: start(blocs, lines, dic, lambda: randint(0, 100) >= prob.get() * 100)).pack(side=LEFT)
    C = Button(frameButtons, text='PAUSE', command=lambda: stop()).pack(side=LEFT)
    D = Button(frameButtons, text='RESET', command=reset).pack(side=LEFT)

    results = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    results.pack(side=TOP, expand=True)

    lstall = Label(results, textvariable=infosGraphic['staled']).pack(side=TOP)
    li = Label(results, textvariable=infosGraphic['i']).pack(side=TOP)
    lmem = Label(results, textvariable=infosGraphic['mem']).pack(side=TOP)
    lnb = Label(results, textvariable=infosGraphic['nb']).pack(side=TOP)
    tmp = Label(results, textvariable=infosGraphic['cycles']).pack(side=TOP)

    resultsCPU = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    resultsCPU.pack(side=TOP, expand=True)

    tmp = Label(resultsCPU, text="CPU stats")
    tmp.pack(side=TOP)

    for cpu_cnt in cpuGraphic[:-1]:
        Label(resultsCPU, textvariable=cpu_cnt, padx=5, pady=3).pack(side=TOP, expand=True)

    bufferCPU = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    bufferCPU.pack(side=TOP, expand=True)

    Label(bufferCPU, text="CPU Buffer Out").pack(side=TOP)
    Label(bufferCPU, textvariable=cpuGraphic[-1], padx=5, pady=2).pack(side=LEFT, expand=True)

    fconfig = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    fconfig.pack(side=TOP, expand=True)

    Scale(fconfig, orient='horizontal', from_=0, to=100,
               variable=speed,
               label='Speed:').pack(side=LEFT, expand=True)
    Scale(fconfig, orient='horizontal', from_=1, to=5,
               variable=infos['memcost'],
               label='Mem cost:').pack(side=LEFT, expand=True)

    otherConfig = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    otherConfig.pack(side=TOP, expand=True)
    Checkbutton(otherConfig, text='Register Hazards', variable=decalD).pack(side=LEFT, expand=True)
    Checkbutton(otherConfig, text='Memory Hazards', variable=decalM).pack(side=LEFT, expand=True)

    fdebug = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5)
    fdebug.pack(side=TOP, expand=True)
    check = Checkbutton(fdebug, text='Debug', variable=DEBUG).pack(side=LEFT, expand=True)
    check = Checkbutton(fdebug, text='Structural dep', variable=STRUCT_DEP).pack(side=BOTTOM, expand=True)

    draw_asm = lambda: draw_asm_canvas(strlines)
    draw_asm()
    window.mainloop()
