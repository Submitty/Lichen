# Example Hello World program

	.data
hello_world:	.asciiz "Hello, World!"

#############################################################################

	.text
main:
	li $v0, 4 	# syscall 4 (print_str)
	la $a0, hello_world # argument: string
	syscall 	# print the string

	jr $ra 		# return to caller
