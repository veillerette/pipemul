from random import randint,seed
import string

# return False if no reg, else the id of reg
def is_reg(op):
    if len(op) > 4 or len(op) < 2:
        return False
    if op[-1] != 'i' and op[-1] != 'x' and op[-1] != 'p':
        return False
    if "PTR" in op:
        return False
    if len(op)==2:
        return op
    return op[1:]


def is_mem(op):
    """
    Return false si op n'est pas une case mémoire et son id sinon.
    """
    if "PTR" not in op:
        return False
    mem = op.split("[")[1][:-1].split("-")
    if len(mem) == 1:
        return False
    try:
        return int(mem[1])
    except ValueError:
        return int(mem[1].split("+")[0])


def is_flag(instr):
    if not (instr[0] == '.' and instr[1] == 'L') or (len(instr) >= 2 and not ('0' <= instr[2] <= '9')):
        return False
    if instr[-1] == ':':
        return int(instr[2:-1])
    return int(instr[2:])

def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def refactor_op(op):
    return 'm[' + str(op[1:]) + ']' if len(op)>=2 and op[0] == 'm' and op[:3] not in ["mov", "mul"] else op

def transform_mem(mem):
    return "m" + str(is_mem(mem))


def transform_flag(flag):
    return str(is_flag(flag))


def create_dic_flags(lines):
    """
    Crée un dictionnaire : nb_flag -> nb_ligne
    """
    return {is_flag(lines[i][0]): i for i in range(len(lines)) if is_flag(lines[i][0])}


def remove_com(line):
    """
    Retire les commentaires des lignes.
    """
    for i in range(len(line)):
        if line[i] == '#' or line[i] == ";":
            return line[0:i]
    return line


def simplify_asm_file(src):
    """
    Retire des choses inutiles (lignes vides, informations compilateur, espaces inutiles).
    """
    return list(filter(lambda i: (len(i) > 0) and (i[0] != '.' or ':' == i[-1]),
                       map(lambda i: remove_com(i).strip().replace("\t", " "), src.split("\n"))))


def extract_strings(src):
    """
    Extrait les chaines constantes et les indexe par ordre de lecture.
    """
    strlines = list(filter(lambda j: j[:7] == ".string", map(lambda i: i.strip(), src.split("\n"))))
    return list(map(lambda i: i.split('"')[1].replace("\\n", "\n"), strlines))


def tozero(a):
    return (a > 0) * a
