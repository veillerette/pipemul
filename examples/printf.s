.LC0:
	.string	"I'm %d years old, I've %d dollars and my name is %s !\n"
.LC1:
    .string "Linus"

_start:
    mov eax, 42
    mov ebx, 1337

    mov di, 0       # string .LC0
    mov	esi, eax    # first arg
    mov edx, ebx    # second arg
    mov ecx, 1      # third arg => string n°1 (.LC1)
	call printf