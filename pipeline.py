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
from parsing import *
from processor import Processor

base_title = "Simul RISC with ASM"
window = Tk()
window.title(base_title)
window.configure(background="#464956")

CVS_WIDTH = 500
CVS_HEIGHT = 2000

frameCanvas = Frame(window, width=CVS_WIDTH)
frameCanvas.pack(side=LEFT, )
canvas = Canvas(frameCanvas, width=CVS_WIDTH, height=window.maxsize()[1] - 50, bg='#7c818b', highlightthickness=0,
                scrollregion=(0, 0, CVS_WIDTH, CVS_HEIGHT))

vbar = Scrollbar(frameCanvas, orient=VERTICAL)
vbar.pack(side=RIGHT, fill=Y)
vbar.config(command=canvas.yview)
canvas.config(yscrollcommand=vbar.set)

# TODO : must be tested on Windows. <3
canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll((1 if event.delta else -1), "units"))

canvas.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
canvas.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

canvas.config(width=CVS_WIDTH, height=CVS_HEIGHT)

canvas.pack(side=LEFT, expand=True, fill=BOTH)

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


def reset(strlines):
    infos['cycles'].set(0)
    majinfos(0, 0, 0, 0)
    infos['r'].clear()
    pipeline.clear()
    stalledPerIns.clear()
    global cpu
    cpu.reset()

    draw_asm_canvas(strlines)


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
        return False, 0
    for i in range(len(pipeline)):
        if pipeline[i][1].count("wait") <= 1:
            ok = False
        mini = min(mini, pipeline[i][1].count("wait") - 1)
    return ok, mini


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
    # while (is_flag(lines[i]) or lines[i][0] == '.'):
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
        tmp = min(tmp, pipeline[-1][1].count("wait") + 10)
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


def get_str_state_pipeline(ins):
    pip = pipeline[ins]
    if pip[0] == 999:
        return ""
    symb = ['F', 'D', 'E', 'M', 'W']
    tostr = pip[1][len(pipeline) - 1 - ins + pipelineStep]
    if len(tostr) == 0:
        return symb[len(pipeline) - 1 - ins + pipelineStep]
    return tostr


def round_rectangle(cvs, x1, y1, x2, y2, r, **kwargs):
    points = (
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2,
        x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1)
    return cvs.create_polygon(points, **kwargs, smooth=True)


def select_color_op(op):
    if is_int(op):
        return "#e87f48"

    if op in auth_instr:
        return "#59929a"

    return "#ffffff"


def draw_asm_canvas(lines):
    global window
    global canvas

    canvas.delete("all")
    if len(posLines) == 0:
        y = 15
        for i in range(len(lines)):
            x = 80
            if lines[i][0] == '.':
                x -= 50
            posLines[i] = (x, y)
            y += 22

    # canvas.create_line(150, 10, 150, posLines[len(lines) - 1][1] + 10)

    maxi0 = max([11 * len(l[0]) for l in list(map(lambda i: i.split(" "), lines))])
    maxi1 = max([11 * len(l[1]) for l in list(map(lambda i: i.split(" "), lines))])

    for i in range(len(lines)):
        tpos = posLines[i]
        bgc = "#4d4d4d"
        if infos['i'] == i:
            bgc = '#303030'

        canvas.create_text(10, tpos[1], fill="black", font="Mono 9 italic", justify=LEFT, text=str(i))
        l = lines[i].split(" ")
        for op in range(len(l)):
            if not l[op]:
                continue
            round_rectangle(canvas, tpos[0] - 5 + ((maxi0 + 10) * (op >= 1)) + ((maxi1 + 10) * (op >= 2)), tpos[1] - 9,
                            tpos[0] + 11 * len(l[op]) + 2 + ((maxi0 + 10) * (op >= 1)) + (
                                    (maxi1 + 10) * (op >= 2)), tpos[1] + 11, r=10, fill=bgc, width=0)
            canvas.create_text(tpos[0] + ((maxi0 + 10) * (op >= 1)) + ((maxi1 + 10) * (op >= 2)), tpos[1], fill=select_color_op(l[op]),
                               font="Mono 13", anchor="w", stipple='gray25', text=l[op])
        # canvas.create_line(10, tpos[1] + 6, 260, tpos[1] + 6, fill='gray70')

        tostr = str(stalledPerIns[i]) if i in stalledPerIns else "0"
        canvas.create_text(400, tpos[1], fill="black", font="Mono 9", justify=RIGHT, text=tostr)

    for ins in range(len(pipeline)):
        tostr = get_str_state_pipeline(ins)
        if not tostr:
            continue
        pos = posLines[pipeline[ins][0]]
        canvas.create_text(300, pos[1], fill="black", font="Mono 14", justify=LEFT, text=tostr)

    maj_graphical_cpu()

    canvas.update()
