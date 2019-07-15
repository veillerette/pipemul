	.file	"kmp.c"
	.intel_syntax noprefix
	.text
.LC0:
	.string	"(kmp_for_asm) %d occurences\n"
	.globl	KMP
	.type	KMP, @function
KMP:
	# rsp contain pointer to the kmp table in memory
	mov	QWORD PTR [rbp-40], rdi		# y
	mov	DWORD PTR [rbp-44], esi		# n
	mov	QWORD PTR [rbp-56], rdx		# x
	mov	DWORD PTR [rbp-48], ecx		# m
	mov	DWORD PTR [rbp-12], 0		# s
	mov	DWORD PTR [rbp-8], 0		# j
	mov	DWORD PTR [rbp-4], 0		# i
	jmp	.L2
.L5:
	mov	eax, DWORD PTR [rbp-4]	
	add 	eax, rsp
	mov 	eax, BYTE PTR [rax]
	mov	DWORD PTR [rbp-4], eax # i = TAB[i]
.L3:
    mov ezx, -1
	cmp	DWORD PTR [rbp-4], ezx
	je	.L4
	mov	eax, DWORD PTR [rbp-4]		# i
	movsx	rdx, eax
	mov	rax, QWORD PTR [rbp-56]		# x
	add	rax, rdx			# x+i
	movzx	edx, BYTE PTR [rax]		# *(x+i)
	mov	eax, DWORD PTR [rbp-8]		# j
	movsx	rcx, eax	
	mov	rax, QWORD PTR [rbp-40]		# y
	add	rax, rcx			# y+j
	movzx	eax, BYTE PTR [rax]		# *(y+j)
	cmp	dx, ax				# !=
	jne	.L5				# jmp
.L4:
	add	DWORD PTR [rbp-4], 1
	add	DWORD PTR [rbp-8], 1
	mov	eax, DWORD PTR [rbp-4]
	cmp	eax, DWORD PTR [rbp-48]
	jne	.L2
	add	DWORD PTR [rbp-12], 1
	mov	eax, DWORD PTR [rbp-4]
	add eax, rsp
	mov eax, BYTE PTR [rax]
	mov	DWORD PTR [rbp-4], eax
.L2:
	mov	eax, DWORD PTR [rbp-8]
	cmp	eax, DWORD PTR [rbp-44]
	jl	.L3
    mov	eax, DWORD PTR [rbp-12]
	mov	esi, eax
	mov	edi, 0
	mov	eax, 0
	call	printf
