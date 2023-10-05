# if you want to use the "loop" and other files, then you can just try to identify if there is a semicolon, and then keep track of the line
# to tell you when to loop back

# Format: 4-bit Op Code, 4-bit destination register, 4-bit source register, 4-bit source register
ALU_OPS = { 
    'and': '0',
    'or': '1',
    'xor': '2',
    'add': '3',
    'sub': '4',
    'eq': '5',
    'lt': '6',
    'lteq': '7',
    'gteq': '8'
}


COND_JUMP_OPS = {
    'jz': 'd',
    'jnz': 'a',
    'jlz': 'b'
}

OTHER_OPS = {
    'ramstore': '9',
    'ramload': '8',
    'regset': 'e',
    'jump': 'f',
}


assembly = open('ex_code.txt')


for line_num, line in enumerate(assembly):
    # this is specific only to .txt cuz it adds \n
    print(line)
    print(line_num)

    output = ''
    tokens = line.split(' ')
    op = tokens[0]
    args = tokens[1:]

    if op in ALU_OPS.keys():
        print(ALU_OPS[op])
    elif op in COND_JUMP_OPS.keys():
        print(COND_JUMP_OPS[op])
    elif OTHER_OPS.keys():
        print(OTHER_OPS[op])
        print(hex(int(OTHER_OPS[op])))
    

    break







assembly.close()