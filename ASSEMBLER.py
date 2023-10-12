import sys

ERROR = 'ffff'
MIN_SIGNED = -128
MAX_SIGNED = 127
MIN_UNSIGNED = 0
MAX_UNSIGNED = 255
MIN_REGISTER = 0
MAX_REGISTER = 15


TESTCASES = [
    ['add r0 r15 r12', '30fc'],
    ['and r1 r14 r13', '01ed'],
    ['or r2 r11 r8', '12b8'],
    ['xor r3 r4 r5', '2345'],
    ['sub r3 r3 r3', '4333'],
    ['eq r6 r10 r9', '56a9'],
    ['lt r7 r7 r10', '677a'],
    ['gteq r3 r7 r9', '7379'],
    ['ramstore 0 r3', '9003'],
    ['ramstore c2 r15', '9c2f'],
    ['ramstore ff r12', '9ffc'],
    ['ramload r8 02', '8802'],
    ['ramload r13 6a', '8d6a'],
    ['ramload r4 38', '8438'],
    ['regset r10 0', 'ea00'],
    ['regset r8 -128', 'e880'],
    ['regset r3 -1', 'e3ff'],
    ['regset r8 -103', 'e899'],
    ['regset r11 127', 'eb7f'],
    ['regset r6 3', 'e603'],
    ['regset r14 23', 'ee17'],
    ['jump 25', 'f250'],
    ['jump ea', 'fea0'],
    ['jz ef r5', 'def5'],
    ['jz 00 r12', 'd00c'],
    ['jz a r5', 'd0a5'],
    ['lteq r11 r1 r11', ERROR ], # not an operation in ALU yet
    ['foo r5 r6 r8', ERROR], # not a real operation
    ['add r0 r1 r2 r3', ERROR], # too many arguments
    ['add r2 r5', ERROR], # too few arguments
    ['and r1', ERROR], # too few arguments
    ['or 2 3 8', ERROR], # not registers
    ['xor r3 8 r14', ERROR], # one not a register
    ['sub r16 r3 r12', ERROR], # register too big
    ['eq r1 r10 r127', ERROR], # register too big
    ['lt r4 r-2 r8', ERROR], # register negative
    ['lteq rx r12 r6', ERROR], # register not a number
    ['add r2h r12 r6', ERROR], # register not a number
    ['and r5 r9 r*2', ERROR], # register contains other characters
    ['ramstore 18', ERROR], # not enough arguments
    ['ramload r5', ERROR], # not enough arguments
    ['ramstore r1 6a 92', ERROR], # too many arguments
    ['ramload', ERROR], # not enough arguments
    ['ramstore 25 6', ERROR], # second argument not register
    ['ramload 7 fb', ERROR], # first argument not register
    ['ramstore 67 r20', ERROR], # register too big
    ['ramload r7 132', ERROR], # address too big
    ['ramstore sy r3', ERROR], # address not a number
    ['ramload r# 71', ERROR], # register not a number
    ['ramload r4 -25', ERROR], # negative address
    ['regset r5', ERROR], # too few arguments
    ['regset r10 9b a3', ERROR], # too many arguments
    ['regset r62 80', ERROR], # register too big
    ['regset rh2 80', ERROR], # register not a number
    ['regset r13 323', ERROR], # address too big
    ['regset rd ui', ERROR], # address not a number
    ['jump', ERROR], # too few arguments
    ['jump 9b a3', ERROR], # too many arguments
    ['jump 32a', ERROR], # address too big
    ['jump -25', ERROR], # negative address
    ['jump p', ERROR], # address not a number
    ['jz 12', ERROR], # too few arguments
    ['jz 1a r3 bd', ERROR], # too many arguments
    ['jz 93 r17', ERROR], # register too big
    ['jz a9 r$', ERROR], # register not a number
    ['jz 135 r11', ERROR], # address too big
    ['jz -35 r3', ERROR], # negative address
    ['jz 6r r8', ERROR], # address not a number
]
# Format: 4-bit Op Code, 4-bit destination register, 4-bit source register, 4-bit source register
ALU_OPS = { 
    'and': '0',
    'or': '1',
    'xor': '2',
    'add': '3',
    'sub': '4',
    'eq': '5',
    'lt': '6',
    'gteq': '7'
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


print_errors = True

def display_error(msg, line_num):
    if print_errors:
        sys.stderr.write('Error on line {}: {}\n'.format(line_num,  msg))


def translate_address(value, line_num):
    # try to translate the value as hexadecimal. If it fails, set it to an invalid value
    try:
        num = int(value, 16) 
    except ValueError:
        num = MIN_UNSIGNED - 1 

    if num < MIN_UNSIGNED or num > MAX_UNSIGNED:
        display_error('"{}" not valid 8-bit hexadecimal'.format(value), line_num)
        return ERROR
    else:
        # 0>2 says to put a zero on the left if needed to make it two characters wide
        return '{:0>2}'.format(value)


def translate_register(register, line_num):
    # try to read the register as an integer. If it fails, set it to an invalid value
    try:
        num = int(register[1:])
    except ValueError:
        num = MIN_REGISTER - 1 

    if register[0] != 'r' or num < MIN_REGISTER or num > MAX_REGISTER:
        display_error('"{}" is not a valid register'.format(register), line_num)
        return ERROR
    else:
        # the x tells it to use hexadecimal
        return '{:x}'.format(num)


def translate_constant(constant, line_num):
    try:
        num = int(constant)
    except ValueError:
        num = MIN_SIGNED - 1

    if num < MIN_SIGNED or num > MAX_SIGNED:
        display_error('"{}" is not a valid 8-bit constant'.format(constant), line_num)
        return ERROR
    else:
        # 0>2 says to put a zero on the left if needed to make it two characters wide
        # the x tells it to use hexadecimal
        # The '& 0xff' pulls off the high bits, to make this 8 bits (necessary for negative numbers)
        return '{:0>2x}'.format(num & 0xff)


def translate_ALU(op, args, line_num):

    if len(args) != 3:
        return ERROR
    
    operation = ALU_OPS[op]
    destination_register = translate_register(args[0], line_num)
    source_register_one = translate_register(args[1], line_num)
    source_register_two = translate_register(args[2], line_num)

    if operation == ERROR or destination_register == ERROR or source_register_one == ERROR or source_register_two == ERROR:
        return ERROR
    else:
        return operation + destination_register + source_register_one + source_register_two



def translate_ramstore(args, line_num):
    address = translate_address(args[0], line_num)
    register = translate_register(args[1], line_num)
    if address == ERROR or register == ERROR:
        return ERROR
    else:
        return OTHER_OPS['ramstore'] + address + register

        
def translate_ramload(args, line_num): # this is just like the inverse of translate_ramstore
    register = translate_register(args[0], line_num)
    address = translate_address(args[1], line_num)
    if address == ERROR or register == ERROR:
        return ERROR
    else:
        return OTHER_OPS['ramload'] + register + address 
    


def translate_regset(args, line_num):
    register = translate_register(args[0], line_num)
    constant = translate_constant(args[1], line_num)
    if constant == ERROR or register == ERROR:
        return ERROR
    else:
        return OTHER_OPS['regset'] + register + constant 
   


def translate_jump(args, line_num): # unconditional jump
    if len(args) != 1:
        display_error('jump takes one argument', line_num)
        return ERROR
    else:
        address = translate_address(args[0], line_num)
        if address == ERROR:
            return ERROR
        else:
            return OTHER_OPS['jump'] + address + '0'


def translate_conditional_jump(op, args, line_num):
    if len(args) != 2:
        display_error('cond jump takes two arguments', line_num)
        return ERROR
    else:
        operation = COND_JUMP_OPS[op]
        address = translate_address(args[0], line_num)
        register = translate_register(args[1], line_num)
        if address == ERROR or register == ERROR or operation == ERROR:
            return ERROR
        else:
            return operation + address + register
    


def translate_line(command, line_num):
    output = ''
    tokens = command.split(' ')
    op = tokens[0]
    args = tokens[1:]

    if op in ALU_OPS:
        output = translate_ALU(op, args, line_num)
    elif op == 'jump':
        output = translate_jump(args, line_num)
    elif len(args) != 2:
        # all other operations take two arguments
        display_error('{} takes two arguments'.format(op), line_num)
        output = ERROR
    elif op == 'ramstore':
        output = translate_ramstore(args, line_num)
    elif op == 'ramload':
        output = translate_ramload(args, line_num)
    elif op == 'regset':
        output = translate_regset(args, line_num)
    elif op == 'jz' or  op == 'jnz' or  op == 'jlz':
        output = translate_conditional_jump(op, args, line_num)
    else:
        display_error('Unsupported operation ' + op, line_num)
        output = ERROR

    return output


def translate_program(assembly):
    machine_code = []
    # Logisim memory has this as the first line
    current_line = 'v2.0 raw'

    for line_num, line in enumerate(assembly):
        # 16-bit Logisim memory puts a newline every eight 16-bit segments
        if line_num % 8 == 0:
            machine_code.append(current_line)
            current_line = ''

        if line != '':
            current_line += translate_line(line, line_num + 1) + ' '
    machine_code.append(current_line)

    return machine_code


def run_tests():
    # Some test cases purposely cause errors. This will prevent errors from printing
    global print_errors
    print_errors = False

    num_errors = 0
    results = []
    for num, testcase in enumerate(TESTCASES):
        assembly, expected_machine_code = testcase
        machine_code = translate_line(assembly, num)
        if machine_code != expected_machine_code:
            num_errors += 1
            results.append('FAILURE: Testcase {}: Expected {} but got {}'.format(
                assembly, expected_machine_code, machine_code))
    
    print('\n'.join(results))
    print('=' * 80)

    if num_errors == 0:
        print('All {} tests passed!'.format(len(TESTCASES)))
    else:
        print('{}/{} tests failed'.format(num_errors, len(TESTCASES)))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please give me the name of a file with assembly code or the word "test" to run the tests')
        sys.exit(1)

    if sys.argv[1] == 'test':
        run_tests()

    else:
        assembly = open(sys.argv[1]).read().split('\n')
        machine_code = translate_program(assembly)
        print('\n'.join(machine_code))