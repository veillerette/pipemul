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

    strlines = list(map(lambda i: ' '.join(list(map(lambda j: refactor_op(str(j)), i))), lines))
    print("STR = ", strlines)
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

    frameButtons = Frame(window, bd=1, relief=SUNKEN, padx=7, pady=5, bg="#687382")
    frameButtons.pack(side=TOP)

    testB = Button(window, text="TEST WIN", command=lambda: Tk()).pack(side=LEFT, expand="True")

    A = Button(frameButtons, text='ONE STEP',
               command=lambda: next_step(blocs, lines, strlines), highlightthickness=0, bg="#2aa1d3", highlightbackground="#27b9f3", activebackground="#27b9f3", fg="#ffffff",
               font="Mono 12 bold").pack(side=LEFT,
                                         padx=3)
    B = Button(frameButtons, text='RUN',
               command=lambda: start(blocs, lines, dic, lambda: randint(0, 100) >= prob.get() * 100),
               highlightthickness=0, bg="#2aa1d3", highlightbackground="#27b9f3", activebackground="#27b9f3", fg="white", font="Mono 12 bold").pack(side=LEFT, padx=3)
    C = Button(frameButtons, text='PAUSE', command=lambda: stop(), highlightthickness=0, bg="#2aa1d3", highlightbackground="#27b9f3", activebackground="#27b9f3", fg="white",
               font="Mono 12 bold").pack(side=LEFT, padx=3)
    D = Button(frameButtons, text='RESET', command=lambda: reset(strlines), highlightthickness=0, bg="#d32a2f", highlightbackground="#f6242b", activebackground="#f6242b",
               fg="white",
               font="Mono 12 bold").pack(side=LEFT, padx=3)

    results = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    results.pack(side=TOP, expand=True)

    lstall = Label(results, textvariable=infosGraphic['staled'], bg="#687382").pack(side=TOP)
    li = Label(results, textvariable=infosGraphic['i'], bg="#687382").pack(side=TOP)
    lmem = Label(results, textvariable=infosGraphic['mem'], bg="#687382").pack(side=TOP)
    lnb = Label(results, textvariable=infosGraphic['nb'], bg="#687382").pack(side=TOP)
    tmp = Label(results, textvariable=infosGraphic['cycles'], bg="#687382").pack(side=TOP)

    resultsCPU = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    resultsCPU.pack(side=TOP, expand=True)

    tmp = Label(resultsCPU, text="CPU stats", bg="#687382")
    tmp.pack(side=TOP)

    for cpu_cnt in cpuGraphic[:-1]:
        Label(resultsCPU, textvariable=cpu_cnt, padx=5, pady=3, bg="#687382").pack(side=TOP, expand=True)

    bufferCPU = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    bufferCPU.pack(side=TOP, expand=True)

    Label(bufferCPU, text="CPU Buffer Out", bg="#687382").pack(side=TOP)
    Label(bufferCPU, textvariable=cpuGraphic[-1], padx=5, pady=2, bg="#687382").pack(side=LEFT, expand=True)

    fconfig = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    fconfig.pack(side=TOP, expand=True)
    """
    Scale(fconfig, orient='horizontal', from_=0, to=100,
          variable=speed,
          highlightthickness=0,
          label='Speed:', bg="#687382").pack(side=LEFT)
    """
    Label(fconfig, text="Speed", bg="#687382").pack(side=LEFT)
    _vals = [30, 6, 0]
    _etiq = ["x1", "x5", "inf"]
    _col = ['#4bc04b', '#4c4bc0', '#c04b4b']
    for i in range(len(_vals)):
        b = Radiobutton(fconfig, variable=speed, indicatoron=0, text=_etiq[i], value=_vals[i], highlightthickness=0,
                        bg="#687382", highlightbackground=_col[i], activebackground=_col[i], selectcolor=_col[i], padx=5, pady=5, borderwidth=2, relief="flat")
        if i==0:
            b.invoke()
        b.pack(side=LEFT, expand=True)

    Scale(fconfig, orient='horizontal', from_=1, to=5,
          highlightthickness=0,
          variable=infos['memcost'],
          label='Mem cost:', bg="#687382").pack(side=LEFT)

    otherConfig = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    otherConfig.pack(side=TOP, expand=True)
    Checkbutton(otherConfig, text='Register Hazards', variable=decalD,
                highlightthickness=0, bg="#687382").pack(side=LEFT, expand=True)
    Checkbutton(otherConfig, text='Memory Hazards', variable=decalM, highlightthickness=0, bg="#687382").pack(side=LEFT,
                                                                                                              expand=True)

    fdebug = Frame(window, bd=1, padx=7, pady=5, bg="#687382")
    fdebug.pack(side=TOP, expand=True)
    check = Checkbutton(fdebug, text='Debug', variable=DEBUG, highlightthickness=0, bg="#687382").pack(side=LEFT,
                                                                                                       expand=True)
    check = Checkbutton(fdebug, text='Structural dep', variable=STRUCT_DEP, highlightthickness=0, bg="#687382").pack(
        side=BOTTOM, expand=True)

    draw_asm = lambda: draw_asm_canvas(strlines)
    draw_asm()

    reset(strlines)
    window.mainloop()
