mov ax, 42
add ax, 1
mov bx, ax
mul bx, 3
mov	DWORD PTR [rbp-4], 1
mul DWORD PTR [rbp-4], bx