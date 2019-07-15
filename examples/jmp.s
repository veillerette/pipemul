_start:
    mov ax, 1
    mov bx, 2
    mov cx, 3
    jmp .L1
    add ax, 42  # not executed
.L1:
    add ax, 1
