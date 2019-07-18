# Pipeline Simulator

a RISC pipeline simulator of NASM file including :
 
 * real RISC processor emulator
 * semantic and structural hazards
 * memory cost
 * graphical visualization using tkinter
 

**Warning :** The goal of this simulator is to understand the pipeline through the execution of **ONE** function on random data.
So there is not a real *stack* and *call* instruction.

## Requirement
 * `Linux` or `Windows`
 * `python >= 3.5` or `pypy >= 3.5`
 * `tkinter >= 3.5`


## Launch

```python
python3 main.py asm_file.py
```
*where **asm_file** is a valid NASM program which respects the rules shown below*.

## NASM language

 * Supported instructions : 
 
| mov | sub | add | mul | jmp | jne | je | jl | js | cmp | jcmp | call |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |  :---: | :---: |

 * All lines beginning by a dot '.' is ignored except labels and the header '.string'
 * The character '#' is used to comment, it can be put everywhere.
 * The only function supported with call is `printf`.
 You can pass up to 15 arguments with the following order convention (from left to right) :

| di |  si | dx | cx | r8 | r9 | r10 | r11 | r12 | r13 | r14 | r15
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |  :---: | :---: |
 
 * **static strings** must be put in a `.string` linked to a label (see `examples/printf.s`) :
 ```asm
    .LC0:
        .string "Linus"
 ```

## RISC Pipeline

Pipeline used is a RISC 5-µInstructions pipeline :

 * **F**etch:
 * **D**ecode:
 * **E**xecute:
 * **M**emory:
 * **W**rite **B**ack:
 
 ### Example :
 With the program :
 ```
    mov ax, 42
    add ax, 1
    mov bx, ax
 ```
 
 We obtain the pipeline below :
 
cycle n° | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| mov ax, val | F | D | E | M | W | | |
| add ax, 1| | F | ? | D | E | M | W |
| mov bx, ax| | | F | ? | ? | D | E | M | W |






