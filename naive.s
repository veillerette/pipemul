	.file	"naive.c"
	.intel_syntax noprefix
	.text
	.section	.rodata
.LC0:
	.string	"(naive_for_asm) %d occurences\n"
	.text
	.globl	naive_for_asm
	.type	naive_for_asm, @function
naive_for_asm:
	mov	QWORD PTR [rbp-24], rdi # y
	mov	DWORD PTR [rbp-28], esi # n

	mov	QWORD PTR [rbp-40], rdx	# x
	mov	DWORD PTR [rbp-32], ecx # m

	mov	DWORD PTR [rbp-4], 0 # s
	mov	DWORD PTR [rbp-8], 0 # i
	jmp	.L2
.L8:
	mov	DWORD PTR [rbp-12], 0
	jmp	.L3
.L6:
	mov	eax, DWORD PTR [rbp-12]
	movsx	rdx, eax
	mov	rax, QWORD PTR [rbp-40]
	add	rax, rdx	
	movzx	edx, BYTE PTR [rax]	
	mov	ecx, DWORD PTR [rbp-8]	
	mov	eax, DWORD PTR [rbp-12]		
	add	eax, ecx		
	movsx	rcx, eax			
	mov	rax, QWORD PTR [rbp-24]	
	add	rax, rcx			
	movzx	eax, BYTE PTR [rax]	
	cmp	dx, ax
	jne	.L5
	add	DWORD PTR [rbp-12], 1	
.L3:
	mov	eax, DWORD PTR [rbp-12]
	cmp	eax, DWORD PTR [rbp-32]
	jl	.L6
	jmp	.L5
.L5:
	mov	eax, DWORD PTR [rbp-12]
	cmp	eax, DWORD PTR [rbp-32]
	jne	.L7
	add	DWORD PTR [rbp-4], 1
.L7:
	add	DWORD PTR [rbp-8], 1
.L2:
	mov	eax, DWORD PTR [rbp-28]
	sub	eax, DWORD PTR [rbp-32]
	add eax, 1
	cmp	DWORD PTR [rbp-8], eax
	jl	.L8
	mov	eax, DWORD PTR [rbp-4]
	mov	esi, eax
	mov	edi, 0
	mov	eax, 0
	call	printf
