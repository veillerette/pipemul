# Python File by Victor Veillerette
# 04/2019

# Simulateur de pipeline RISC
# Avec :
# 	- Sauts conditionnel et simple
#   - Pipeline RISC à 5 micro instructions : Fetch, Decode, Execute, Memory, Write-Back
#   - Simulateur réel des registres / mémoires, de l'execution avec des vraies comparaisons.
# Construction du pipeline de la forme :
# 		(nb, tmp, bloc, lines[i])
# 	- nb : numéro de l'instruction
#	- tmp : Nombre de cycles stalled correspondants
# 	- bloc : bloc RISC de l'instruction : [F, D, E, M, W]
#	- line : ligne ASM simplifiée correspondante

from tkinter import *
from tools import *
from parser import *
from processor import Processor
from parser import parse_file


base_title = "Simul RISC with ASM"
window = Tk()
window.title(base_title)

CVS_WIDTH = 300
canvas = Canvas(window, width=CVS_WIDTH, height=window.maxsize()[1]-50, bg='white')
canvas.pack(side=LEFT, padx=0, pady=0)

infos = {'i': 0, 'nb': 0, 'staled': 0, 'mem': 0, 'r': [], 'memcost': IntVar(value=1), "cycles": IntVar()}
stalledPerIns = {}
cpu = Processor()
infosGraphic = {'i': StringVar(), 'nb': StringVar(), 'staled': StringVar(), 'mem': StringVar(), "cycles": StringVar()}
cpuGraphic = [StringVar(value="") for i in range(len(cpu.counters) + 2)]
runned = False

# OPTIONS
speed = IntVar(value=30)
prob = DoubleVar(value=0.15)
DEBUG = IntVar(value=0)
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
    next_step(blocs, lines, strlines)
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
            print("\t" * j, end="")
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

def next_step(blocs, lines, strlines):
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

    # passer les drapeaux
    #while (is_flag(lines[i]) or lines[i][0] == '.'):
    #    i+=1

    i = cpu.get_ptr()

    bloc = blocs[i]
    add_one_cycle()

    two = infos['r'][nb - 7:nb + 1]  # dernières instructions executées

    # Recherche d'interférences avec les précédentes instructions
    tmp = max([decal(last, bloc, nb) for last in two] + [0])

    # Décalage structurel
    if STRUCT_DEP.get() == 1 and len(pipeline) and (pipeline[-1][1][1]) == "wait" and tmp == 0:
        tmp = max(pipeline[-1][1].count("wait"), tmp)
    tmp2 = 0  # tmp2 = max([(last[0]+last[1]+4 - nb - 1) for last in two if len(set(last[2][3]).intersection(set(bloc[3]))) > 0]+[0])
    # Not usefull since in a classic RISC, the µ-ins M is divived in two blocs : Write-Memory first, Read-Memory then.

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

    if STRUCT_DEP.get() == 1:
        add_stalled(i, max(tmp - last_stalled, 0))
        staled += max(tmp - last_stalled, 0)
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
        canvas.create_text(10, tpos[1], fill="black", font="Mono 7", justify=LEFT, text=str(i))
        canvas.create_text(tpos[0], tpos[1], fill=color, font="Mono 10", justify=LEFT, text=lines[i])
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
        canvas.create_text(180, pos[1], fill="black", font="Mono 10", justify=LEFT, text=tostr)

    maj_graphical_cpu()

    canvas.update()
