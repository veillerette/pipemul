# Python File by Victor Veillerette
# 04/2019

# external
from random import randint, seed
from tkinter import *
import string

# intern
from processor import Processor
from tools import *

"""
# Simulateur de pipeline RISC un peu bidouillé
# Avec : 
# 	- Sauts conditionnel et simple
#   - Probabilité injectée dans les comparaisons (jcmp)
    OU
#   - Simulateur réel des registres / mémoires, de l'execution avec des vraies comparaisons.
# Construction du pipeline de la forme :
# 		(nb, tmp, bloc, lines[i])
# 	- nb : numéro de l'instruction
#	- tmp : Nombre de cycles stalled correspondants
# 	- bloc : bloc RISC de l'instruction : [F, D, E, M, W]
#	- line : ligne ASM simplifiée correspondante
"""

# instructions autorisées (les autres sont ignorées)
auth_instr = ['mov', 'sub', 'jmp', 'add', 'jne', 'je', 'cmp', 'jl', 'jcmp', 'js', 'call']


def replace_multi_instr(lines):
    """
     Transforme les instructions : ins mem1 mem2
     En : 	mov reg mem1
    		ins reg mem2
    		mov mem1 reg
     Gère les accès à la mémoire depuis une variable comme :
        mov mem(rax) val
    """
    r = []
    for i in lines:
        if i[0][:3] == 'mov':
            i[0] = 'mov'
        if (i[0] == 'add' or i[0] == 'sub') and is_mem(i[1]):
            if not is_reg(i[2]):
                r.append([i[0], transform_mem(i[1]), int(i[2])])
            else:
                r.append(['mov', 'zx', transform_mem(i[1])])
                if is_reg(i[2]):
                    r.append([i[0], 'zx', i[2]])
                else:
                    r.append([i[0], 'zx', int(i[2])])
                r.append(['mov', transform_mem(i[1]), 'zx'])
        elif i[0] == 'cmp' and is_mem(i[2]):
            r.append(['mov', 'yx', transform_mem(i[2])])
            r.append(['cmp', is_reg(i[1]), 'yx'])
        elif i[0] == 'cmp' and is_mem(i[1]):
            r.append(['mov', 'yx', transform_mem(i[1])])
            r.append(['cmp', 'yx', is_reg(i[2])])
        elif i[0] in auth_instr and len(i) == 3:
            print(i)
            if is_reg(i[1]) and i[2][:4] == "BYTE":
                access = i[2].split('[')[1].split("]")[0]
                if "+,-*" in access:
                    pass  # TODO
                r.append([i[0], is_reg(i[1]), "m" + is_reg(access)])
                continue
            if i[1][:4] == "BYTE":
                access = i[1].split('[')[1].split("]")[0]
                if "+,-*" in access:
                    pass  # TODO
                if is_reg(i[2]):
                    r.append([i[0], "m" + is_reg(access), is_reg(i[2])])
                else:
                    r.append([i[0], "m" + is_reg(access), int(i[2])])
                continue
            if is_mem(i[1]):
                if is_reg(i[2]):
                    r.append([i[0], transform_mem(i[1]), is_reg(i[2])])
                else:
                    r.append([i[0], transform_mem(i[1]), int(i[2])])
            elif is_mem(i[2]):
                r.append([i[0], is_reg(i[1]), transform_mem(i[2])])
            elif is_reg(i[1]) and is_reg(i[2]):
                r.append([i[0], is_reg(i[1]), is_reg(i[2])])
            elif is_reg(i[1]):
                try:
                    r.append([i[0], is_reg(i[1]), int(i[2])])
                except ValueError:
                    continue
        else:
            if is_flag(i[0]):
                r.append(i)
            if i[0] in auth_instr and len(i) == 2:
                r.append(i)
    return r


def parse_line(line):
    bloc = line.split(",")
    r = [line.split(" ")[0], (' '.join(bloc[0].split(" ")[1:])).strip()]
    if len(bloc) > 1:
        r.append(bloc[1].strip())
    return r


def parse_file(s):
    return [parse_line(i) for i in simplify_asm_file(s)]


def transform_bloc(line):
    """
     Transformation d'une line en bloc RISC : [F, D, E, M, W]
     On remplace 'D' par la liste des registres lues
     On remplace 'M' par la liste des cases mémoires lire/écrire
     On remplace 'W' par la liste des registres à écrire
    """
    b = ["F", [], "E", [], "W"]
    if line[0] == "add" or line[0] == "sub":
        b[4] = line[1]
        if type(line[2]) != int:
            b[1] = line[1]
        else:
            b[1] = line[1]

    if line[0] == "mov":
        if line[1][0] == 'm':
            b[3] += [line[1]]
        else:
            b[4] = line[1]
        if type(line[2]) != int:
            if line[2][0] == 'm':
                b[3] += [line[2]]
                if string.digits not in line[2]:
                    b[1] += [line[2][1:]]
            else:
                b[1] += [line[2]]
    if line[0] == "cmp":
        if line[1][0] == 'm':
            b[3] += [line[1]]
        else:
            b[1] += [line[1]]
        if type(line[2]) != int:
            if line[2][0] == 'm':
                b[3] += [line[2]]
            else:
                b[1] += [line[2]]
    # Cas spécial des sauts
    if line[0] in ("jmp", "jne", "jl"):
        b[0] = "jmp"
        b[1] = line[1]
    elif line[0] == "jcmp":
        b[0] = "jcmp"
        b[1] = line[1]
    return b


base_title = "Simul RISC with ASM"
window = Tk()
window.title(base_title)

CVS_WIDTH = 300
canvas = Canvas(window, width=CVS_WIDTH, height=700, bg='white')
canvas.pack(side=LEFT, padx=0, pady=0)

infos = {'i': 0, 'nb': 0, 'staled': 0, 'mem': 0, 'r': [], 'memcost': IntVar(value=1), "cycles": IntVar()}
stalledPerIns = {}
cpu = Processor()
infosGraphic = {'i': StringVar(), 'nb': StringVar(), 'staled': StringVar(), 'mem': StringVar(), "cycles": StringVar()}
cpuGraphic = [StringVar(value="") for i in range(len(cpu.counters) + 2)]
runned = False

# OPTIONS
speed = IntVar(value=15)
prob = DoubleVar(value=0.15)
DEBUG = IntVar(value=1)
STRUCT_DEP = IntVar(value=1)
decalD = IntVar(value=1)
decalM = IntVar(value=1)


def maj_graphical_cpu():
    global cpu
    global cpuGraphic
    cpu.graphical_output(cpuGraphic[-2], cpuGraphic[-1], cpuGraphic)


def add_stalled(ins, nb):
    if ins in stalledPerIns:
        stalledPerIns[ins] += nb
    else:
        stalledPerIns[ins] = nb


def majinfos(i, nb, staled, mem):
    infos['i'] = i
    infos['nb'] = nb
    infos['staled'] = staled
    infos['mem'] = mem
    majgraphics(i, nb, staled, mem)


def majgraphics(i, nb, staled, mem):
    infosGraphic['i'].set("Line n°: " + str(i))
    infosGraphic['nb'].set("Instructions: " + str(nb))
    infosGraphic['staled'].set("Stalled cycles: " + str(staled))
    infosGraphic['mem'].set("Mem Cost: " + str(mem))
    infosGraphic['cycles'].set("Cycles: " + str(infos['cycles'].get()))


def reset():
    infos['cycles'].set(0)
    majinfos(0, 0, 0, 0)
    infos['r'].clear()
    pipeline.clear()
    stalledPerIns.clear()
    global cpu
    cpu.reset()


def run(blocs, lines, dic_flags, take_cmp):
    if not runned:
        return
    strlines = list(map(lambda i: ' '.join(list(map(lambda j: str(j), i))), lines))
    next_step(blocs, lines, dic_flags, take_cmp, strlines)
    window.after(speed.get(), lambda: run(blocs, lines, dic_flags, take_cmp))


def start(blocs, lines, dic_flags, take_cmp):
    global runned
    if not runned:
        runned = True
        run(blocs, lines, dic_flags, take_cmp)


def stop():
    global runned
    runned = False


pipeline = []
pipelineStep = 0


def print_pip(pip):
    print('\t'.join(pip))


def is_pipeline_simplified():
    global pipeline
    ok = True
    mini = 9999
    if len(pipeline) <= 4:
        return False,0
    for i in range(len(pipeline)):
        if pipeline[i][1].count("wait") <= 1:
            ok = False
        mini = min(mini, pipeline[i][1].count("wait")-1)
    return ok,mini


def add_pipeline(i, bloc):
    global pipeline
    global pipelineStep

    ret = True
    if len(pipeline) == 0:
        pipeline.append((i, bloc))
        pipelineStep = 0
        return True

    if len(pipeline) == 5:
        ok, mini = is_pipeline_simplified()
        if ok:
            for i in range(len(pipeline)):
                for j in range(mini):
                    pipeline[i][1].pop(1)

    if len(pipeline) == 5:
        if DEBUG.get() == 1:
            print("pipeline full")
        if len(pipeline[0][1]) <= 5 + pipelineStep:
            if DEBUG.get() == 1:
                print("first bloc finished")
            pipeline = pipeline[1:]
            pipelineStep = 0
        else:
            pipelineStep += 1
            ret = False

    if ret:
        pipeline.append((i, bloc))


    if DEBUG.get() == 1:
        print("\n", "pipelineStep =", pipelineStep)
        for j in range(len(pipeline)):
            print("\t" * j, end='')
            print(pipeline[j])
    return ret


def add_one_cycle():
    global infos
    infos['cycles'].set(infos['cycles'].get() + 1)


def decal(last, bloc, nb):
    if last[2][-1] in bloc[1]:
        base = last[0] + last[1] + len(last[2]) - nb - 1
        if last[2][-2] and decalM.get() == 1:
            return base - 1
        elif decalD.get() == 1:
            return base - 2
        else:
            return 0
    else:
        return 0

def next_step(blocs, lines, dic_flags, take_cmp, strlines):
    i = infos['i']
    nb = infos['nb']
    staled = infos['staled']
    mem = infos['mem']

    global pipeline

    if i >= len(lines) and pipeline[0][0] != 999:
        add_pipeline(999, ['', 'wait', 'wait', '', '', '', '', '', ''])
        add_one_cycle()
        majinfos(i, nb, staled, mem)
        draw_asm_canvas(strlines)
        return
    elif i >= len(lines):
        draw_asm_canvas(strlines)
        stop()
        return
    """	
    # passer les drapeaux
    while(is_flag(lines[i]) or lines[i][0]=='.'):
        i+=1
    """

    i = cpu.get_ptr()

    bloc = blocs[i]
    add_one_cycle()


    """
    # Saut inconditionnel
    if(bloc[0] == "jmp"):
        add_pipeline(i, bloc)
        i = dic_flags[is_flag(bloc[1])]
        majinfos(i, nb, staled, mem)
        return
    # Saut conditionnel. Ici on ne compare pas vraiment, on simule l'execution en insérant une probabilité donnée
    elif(bloc[0] == "jcmp"):
        add_pipeline(i, bloc)
        if(take_cmp()):
            i = dic_flags[is_flag(bloc[1])]
        else:
            i+=1
        majinfos(i, nb, staled, mem)
        return
    """
    two = infos['r'][nb - 7:nb + 1]  # dernières instructions executées

    # Recherche d'interférences avec les précédentes instructions
    tmp = max([decal(last, bloc, nb) for last in two] + [0])

    # Décalage structurel
    if STRUCT_DEP.get() == 1 and len(pipeline) and (pipeline[-1][1][1]) == "wait" and tmp == 0:
        tmp = max(pipeline[-1][1].count("wait"), tmp)
    tmp2 = 0  # tmp2 = max([(last[0]+last[1]+4 - nb - 1) for last in two if len(set(last[2][3]).intersection(set(bloc[3]))) > 0]+[0])

    if len(pipeline):
       tmp = min(tmp, pipeline[-1][1].count("wait")+10)
    symb = ['F', 'D', 'E', 'M', 'W']

    tmpbloc = symb[:]
    if tmp > 0:
        for tmpi in range(tmp):
            tmpbloc.insert(1, "wait")
    if infos['memcost'].get() > 1:
        for tmpmem in range(infos['memcost'].get() - 1):
            tmpbloc.insert(-1, "M")

    # ajout au pipeline
    if not add_pipeline(i, tmpbloc):
        if runned and speed.get() <= 1:
            return
        draw_asm_canvas(strlines)
        return

    last_stalled = max([0] + [last[1] for last in infos['r'][-1:]])
    tmp += tmp2

    goodTmp = tmp

    if STRUCT_DEP.get() == 1:
        add_stalled(i, max(tmp - last_stalled, 0))
        staled += max(tmp - last_stalled, 0)
        goodTmp =  max(tmp - last_stalled, 0)
    else:
        add_stalled(i, tmp)
        staled += tmp

    mcost = 0
    if len(bloc[3]):
        mcost = infos['memcost'].get()

    cpu.execute()

    # Maj infos
    infos['r'].append((nb, tmp, bloc, lines[i]))
    nb += 1  # nombre d'instructions executées
    # staled += mcost + max(tmp - last_stalled, 0)  # nombre de cycles stalled
    i = cpu.get_ptr()
    mem += mcost

    # Maj graphic infos
    majinfos(i, nb, staled, mem)

    if runned and speed.get() <= 1:
        return
    draw_asm_canvas(strlines)


def construct_blocs(path):
    f = open(path, "r")
    s = f.read()
    strs = extract_strings(s)
    s = parse_file(s)
    lines = replace_multi_instr(s)
    blocs = [transform_bloc(i) for i in lines]
    for i in range(len(lines)):
        print(i, lines[i], transform_bloc(lines[i]))
    f.close()
    dic = create_dic_flags(lines)

    return blocs, lines, dic, strs

posLines = dict()

def draw_asm_canvas(lines):
    global window
    global canvas



    canvas.delete("all")
    if len(posLines) == 0:
        y = 15
        for i in range(len(lines)):
            x = 100
            if lines[i][0] == '.':
                x -= 50
            posLines[i] = (x, y)
            y += 12

    canvas.create_line(150, 10, 150, posLines[len(lines) - 1][1] + 10)
    for i in range(len(lines)):
        tpos = posLines[i]
        color = "black"
        if infos['i'] == i:
            color = 'white'
            canvas.create_rectangle(20, tpos[1] - 6, 150, tpos[1] + 6, fill="red")
        canvas.create_text(10, tpos[1], fill="black", font="Mono 8", justify=LEFT, text=str(i))
        canvas.create_text(tpos[0], tpos[1], fill=color, font="Mono 11", justify=LEFT, text=lines[i])
        canvas.create_line(10, tpos[1] + 6, 260, tpos[1] + 6, fill='gray70')

        tostr = "0"
        if i in stalledPerIns:
            tostr = str(stalledPerIns[i])

        canvas.create_text(250, tpos[1], fill="black", font="Mono 9", justify=RIGHT, text=tostr)

    for ins in range(len(pipeline)):
        pip = pipeline[ins]
        if pip[0] == 999:
            continue
        pos = posLines[pip[0]]

        symb = ['F', 'D', 'E', 'M', 'W']

        tostr = pip[1][len(pipeline) - 1 - ins + pipelineStep]
        if len(tostr) == 0:
            tostr = symb[len(pipeline) - 1 - ins + pipelineStep]
        canvas.create_text(180, pos[1], fill="black", font="Mono 11", justify=LEFT, text=tostr)

    maj_graphical_cpu()

    canvas.update()


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
        print("python3 parse_asm.py file.s")
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
               command=lambda: next_step(blocs, lines, dic, lambda: randint(0, 100) >= prob.get() * 100, strlines)).pack(side=LEFT)
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
    #Scale(fconfig, orient='horizontal', from_=0.01, to=1.0,
    #           variable=prob, resolution=0.01,
    #           label='Prob jcmp:').pack(side=LEFT, expand=True)
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
