# Python File by Victor Veillerette
# 04/2019


# intern
from tools import *

# instructions autorisées
auth_instr = ['mov', 'sub', 'jmp', 'add', 'mul', 'jne', 'je', 'cmp', 'jl', 'jcmp', 'js', 'call']


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
        if (i[0] in {"add", "sub", "mul"}) and is_mem(i[1]):
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


def parse_file(s):
    return [parse_line(i) for i in simplify_asm_file(s)]


def parse_line(line):
    bloc = line.split(",")
    r = [line.split(" ")[0], (' '.join(bloc[0].split(" ")[1:])).strip()]
    if len(bloc) > 1:
        r.append(bloc[1].strip())
    return r


def transform_bloc(line):
    """
     Transformation d'une line en bloc RISC : [F, D, E, M, W]
     On remplace 'D' par la liste des registres lues
     On remplace 'M' par la liste des cases mémoires lire/écrire
     On remplace 'W' par la liste des registres à écrire
    """
    b = ["F", [], "E", [], "W"]
    if  line[0] in {"add", "sub", "mul"}:
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
