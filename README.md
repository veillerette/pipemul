# Pipeline Simulator

a RISC pipeline simulator of NASM file including :
 
 * real RISC processor emulator
 * semantic and structural hazards
 * memory cost
 * graphical visualization using tkinter

## Requirement
 * `Linux`
 * `python >= 3.5`
 * `tkinter >= 3.5`


## Launch

```python
python3 main.py asm_file.py
```
*where **asm_file** is a valid NASM program which respects some rules shown below*.

## The NASM file Rules

 * Valid instructions : mov, sub, add, mul, jmp, jne, je, jl, js, cmp, jcmp, call
 * All lines beginning by a dot '.' is ignored except labels and the header '.string'
 * The character '#' is used to comment.

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



