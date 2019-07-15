.LC0:
	.string	"I'm %d years old, I've %d dollars and my name is %s.\n And I count ... %d %d %d !\n"
.LC1:
    .string "Linus"

_start:
    mov rax, 42
    mov rbx, 1337

    mov rdi, 0       # string .LC0
    mov	rsi, rax     # first arg
    mov rdx, rbx     # second arg
    mov rcx, 1       # third arg => string n°1 (.LC1)
    mov r8x, 14      # etc...
    mov r9x, 15
    mov r10x, 16
	call printf