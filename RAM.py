#!/usr/bin/env python3
#
# Author : Tomáš Kocourek
# Title : Random access machine simulator
# Date : 3rd March 2022
#

import sys

keys = ['READ', 'STORE', 'LOAD', 'ADD', 'SUB', 'HALF', 'JUMP', 'JPOS', 'JZERO', 'JNEG', 'HALT', 'PASS']

class Token():
    def __init__(self):
        self.type = None
        self.value = None
        self.linenum = None

class Instruction():
    def __init__(self):
        self.instruction = None
        self.type = None
        self.arg = None
        self.linenum = None

class Scanner():
    def __init__(self):
        self.line = None
        self.genline = None
        self.end = False
        self.token = None
        self.linenum = 0
    def generator(self):
        for line in sys.stdin:
            self.linenum += 1
            yield list(line) if list(line)[-1] == '\n' else list(line) + ['\n']    
    def nextline(self):
        try:
            if(self.genline == None):
                genline = self.generator()
            self.line = next(genline)
        except StopIteration:
            self.end = True
    def scan(self):
        if(not self.line):
            self.nextline()
        if(self.end):
            return None
        self.token = Token()
        self.token.linenum = self.linenum
        char = ''
        while True:
            char = self.line.pop(0)
            if(char == '#'):
                char = '\n'
                self.line = []
            if(char == '('):
                self.token.type = '('
                return self.token
            if(char == ')'):
                self.token.type = ')'
                return self.token
            if(char == '='):
                self.token.type = '='
                return self.token
            if(char == '\n'):
                self.token.type = 'newline'
                return self.token
            if(char.isnumeric()):
                self.token.type = 'num'
                self.token.value = char
                while True:
                    char = self.line.pop(0)
                    if(char.isnumeric()):
                        self.token.value = self.token.value + char
                    elif(char == ' '):
                        return self.token
                    elif(char == '\n'):
                        self.line.insert(0, char)
                        return self.token
                    elif(char == ')'):
                        self.line.insert(0, char)
                        return self.token                            
                    else:
                        print("Error on line " + str(self.linenum) + " : Scanner error. Not a valid number : " + self.token.value + char)
                        exit(1)
            if(char.isalpha()):
                self.token.type = 'keyword'
                self.token.value = char
                while True:
                    char = self.line.pop(0)
                    if(char.isalpha()):
                        self.token.value = self.token.value + char
                    elif(char == ' '):
                        if(self.token.value in keys):
                            return self.token
                        print("Error on line " + str(self.linenum) + " : Scanner error. Unknown instruction : " + self.token.value)
                        exit(1)
                    elif(char == '\n'):
                        self.line.insert(0, char)
                        return self.token
                    else:
                        print("Error on line " + str(self.linenum) + " : Scanner error. Not a valid instruction : " + self.token.value + char)
                        exit(1)
            else:
                print("Error on line " + str(self.linenum) + " : Scanner error. Invalid symbol : " + char)
                exit(1)
            

class Parser():

    def __init__(self):
        self.scanner = Scanner()
        self.instructions = [None]

    def getCode(self):
        while True:
            tkn = self.scanner.scan()
            if(tkn == None):
                return self.instructions
            elif(tkn.type == "newline"):
                instruction = Instruction()
                instruction.instruction = "PASS"
                instruction.linenum = tkn.linenum
                self.instructions.append(instruction)
            elif(tkn.type == "keyword"):
                instruction = Instruction()
                instruction.instruction = tkn.value
                instruction.linenum = tkn.linenum
                if(tkn.value in ["READ", "STORE"]):
                    instruction = self.argDirIndir(instruction)
                elif(tkn.value in ["JUMP", "JPOS", "JZERO", "JNEG"]):
                    instruction = self.argConst(instruction)
                elif(tkn.value in ["LOAD", "ADD", "SUB"]):
                    instruction = self.argDirIndirConst(instruction)
                self.instructions.append(instruction)
                tkn = self.scanner.scan()
                if(tkn.type != "newline"):
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Multiple instructions in one line detected : " + str(tkn.value))
                    exit(1)
            else:
                print("Error on line " + str(tkn.linenum) + " : Parse error. Too much arguments or no instruction name : " + str(tkn.value))
                exit(1)

    def argDirIndir(self, instruction):
            tkn = self.scanner.scan()
            if(tkn == None):
                print("Error on the last instruction : Parse error. Incomplete instruction: " + instruction.instruction)
                exit(1)
            elif(tkn.type == "num"):
                instruction.type = "direct"
                instruction.arg = int(tkn.value)
                return instruction
            elif(tkn.type == '('):
                instruction.type = "indirect"
                tkn = self.scanner.scan()
                if(tkn.type == "num"):                
                    instruction.arg = int(tkn.value)
                else:
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Non-numeric token after '(' : " + tkn.value)
                    exit(1)
                tkn = self.scanner.scan()
                if(tkn.type == ')'):
                    return instruction
                else:
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Missing ')'")
                    exit(1)
            print("Error on line " + str(tkn.linenum) + " : Parse error. Incomplete instruction : " + instruction.instruction)
            exit(1)

    def argConst(self, instruction):
            tkn = self.scanner.scan()
            if(tkn == None):
                print("Error on the last instruction : Parse error. Incomplete instruction: " + instruction.instruction)
                exit(1)
            elif(tkn.type == "="):
                instruction.type = "constant"
                tkn = self.scanner.scan()
                if(tkn.type == "num"):
                    instruction.arg = int(tkn.value)
                    return instruction
                else:
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Expected a numeric value after a token '=' : " + instruction.instruction)
                    exit(1)
            elif(tkn.type == "num"):
                instruction.arg = int(tkn.value)
                return instruction

            else:
                print("Error on line " + str(tkn.linenum) + " : Parse error. A token '=' was expected in front of a constant after a instruction : " + instruction.instruction)
                exit(1)

    def argDirIndirConst(self, instruction):
            tkn = self.scanner.scan()
            if(tkn == None):
                print("Error on the last instruction : Parse error. Incomplete instruction: " + instruction.instruction)
                exit(1)
            elif(tkn.type == "num"):
                instruction.type = "direct"
                instruction.arg = int(tkn.value)
                return instruction
            elif(tkn.type == '('):
                instruction.type = "indirect"
                tkn = self.scanner.scan()
                if(tkn.type == "num"):                
                    instruction.arg = int(tkn.value)
                else:
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Non-numeric token after '(' : " + tkn.value)
                    exit(1)
                tkn = self.scanner.scan()
                if(tkn.type == ')'):
                    return instruction
            elif(tkn.type == "="):
                instruction.type = "constant"
                tkn = self.scanner.scan()
                if(tkn.type == "num"):
                    instruction.arg = int(tkn.value)
                    return instruction
                else:
                    print("Error on line " + str(tkn.linenum) + " : Parse error. Expected a numeric value after a token '=' : " + instruction.instruction)
                    exit(1)
            print("Error on line " + str(tkn.linenum) + " : Parse error. Incomplete instruction : " + instruction.instruction)
            exit(1)


class RAM():
    def __init__(self, prog, inp):
        self.inp = inp
        self.prog = prog
        self.reg = {0 : 0}
        self.PC = 1

    def run(self):
        while(self.PC):
            if(self.PC == len(self.prog)):
                self.PC = 0
                break
            getattr(self, self.prog[self.PC].instruction)()
        return self.reg[0]

    def debug(self):
        step = 1
        print("Initial state:")
        print("Input registers : " + str(sys.argv[1:]))
        print("Data registers : " + str(self.reg))
        print("Program counter : " + str(self.PC))
        print("-----------------------")
        while(self.PC):
            if(self.PC == len(self.prog)):
                self.PC = 0
                print("Output : " + str(self.reg[0]))
                return
            print("Step : " + str(step))
            print("Program counter value : " + str(self.PC))
            step += 1
            instruction = self.prog[self.PC]
            getattr(self, self.prog[self.PC].instruction)()
            if(instruction.type == "direct"):
                code = instruction.instruction + " " + str(instruction.arg)
            elif(instruction.type == "indirect"):
                code = instruction.instruction + " (" + str(instruction.arg) + ")"
            elif(instruction.type == "constant"):
                code = instruction.instruction + " =" + str(instruction.arg)
            elif(instruction.arg != None):
                code = instruction.instruction + " " + str(instruction.arg)            
            else:
                code = instruction.instruction
            print("Executing an instruction : " + code)
            print("Input registers : " + str(sys.argv[1:]))
            print("Data registers : " + str(self.reg))
            if(self.PC):
                print("New program counter value : " + str(self.PC))
            else:
                print("Program has ended succesfully.")        
            print("-----------------------")
        print("Output : " + str(self.reg[0]))
        return
            
    

    def READ(self):
        instruction = self.prog[self.PC]
        if(instruction.type == "direct"):
            if(len(self.inp) < instruction.arg):
                print("Error on line " + str(instruction.linenum) + " : Runtime error. It is not possible to read from the input register " + str(instruction.arg) + ". There is no such a input register. Instruction : READ")
                exit(1)
            self.reg[0] = int(self.inp[instruction.arg - 1])
        elif(instruction.type == "indirect"):
            if(instruction.arg not in self.reg.keys()):
                print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid indirect addressing. Since the data register " + str(instruction.arg) + " has not been used yet, it's value is equal to 0. However, there is no such a input register 0. Instruction : READ")
                exit(1)
            if(self.reg[instruction.arg] not in range(1,(len(self.inp) + 1))):
                print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid indirect addressing. The data register " + str(instruction.arg) + " contains a value " + str(self.reg[instruction.arg]) + ". However, there is no such a input register. Instruction : READ")
                exit(1)
            self.reg[0] = int(self.inp[self.reg[instruction.arg]])
        self.PC += 1

    def STORE(self):
        instruction = self.prog[self.PC]
        if(instruction.type == "direct"):
            self.reg[instruction.arg] = int(self.reg[0])
        elif(instruction.type == "indirect"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] = int(self.reg[0])
            else:
                self.reg[self.reg[instruction.arg]] = int(self.reg[0])
        self.PC += 1

    def LOAD(self):
        instruction = self.prog[self.PC]
        if(instruction.type == "direct"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] = 0
            else:
                self.reg[0] = int(self.reg[instruction.arg])
        elif(instruction.type == "indirect"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] = int(self.reg[0])
            elif(self.reg[instruction.arg] not in self.reg.keys()):
                self.reg[0] = 0
            else:
                self.reg[0] = int(self.reg[self.reg[instruction.reg]])
        elif(instruction.type == "constant"):
            self.reg[0] = int(instruction.arg)
        self.PC += 1

    def ADD(self):
        instruction = self.prog[self.PC]
        if(instruction.type == "direct"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] += 0
            else:
                self.reg[0] += int(self.reg[instruction.arg])
        elif(instruction.type == "indirect"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] += int(self.reg[0])
            elif(self.reg[instruction.arg] not in self.reg.keys()):
                self.reg[0] += 0
            else:
                self.reg[0] += int(self.reg[self.reg[instruction.reg]])
        elif(instruction.type == "constant"):
            self.reg[0] += int(instruction.arg)
        self.PC += 1                    

    def SUB(self):
        instruction = self.prog[self.PC]
        if(instruction.type == "direct"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] -= 0
            else:
                self.reg[0] -= int(self.reg[instruction.arg])
        elif(instruction.type == "indirect"):
            if(instruction.arg not in self.reg.keys()):
                self.reg[0] -= int(self.reg[0])
            elif(self.reg[instruction.arg] not in self.reg.keys()):
                self.reg[0] -= 0
            else:
                self.reg[0] -= int(self.reg[self.reg[instruction.reg]])
        elif(instruction.type == "constant"):
            self.reg[0] -= int(instruction.arg)
        self.PC += 1 

    def HALF(self):
        self.reg[0] = int(self.reg[0] / 2)
        self.PC += 1

    def JUMP(self):
        instruction = self.prog[self.PC]
        if(int(instruction.arg) > len(self.prog) - 1):
            print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid jump. There is no line " + str(instruction.arg) + " in the code. Instruction : JUMP")
            exit(1)
        self.PC = int(instruction.arg)

    def JPOS(self):
        instruction = self.prog[self.PC]
        if(int(instruction.arg) > len(self.prog) - 1):
            print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid jump. There is no line " + str(instruction.arg) + " in the code. Instruction : JPOS")
            exit(1)
        if(self.reg[0] > 0):
            self.PC = int(instruction.arg)
        else:
            self.PC += 1

    def JZERO(self):
        instruction = self.prog[self.PC]
        if(int(instruction.arg) > len(self.prog) - 1):
            print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid jump. There is no line " + str(instruction.arg) + " in the code. Instruction : JZERO")
            exit(1)
        if(self.reg[0] == 0):
            self.PC = int(instruction.arg)
        else:
            self.PC += 1

    def JNEG(self):
        instruction = self.prog[self.PC]
        if(int(instruction.arg) > len(self.prog) - 1):
            print("Error on line " + str(instruction.linenum) + " : Runtime error. Invalid jump. There is no line " + str(instruction.arg) + " in the code. Instruction : JNEG")
            exit(1)
        if(self.reg[0] < 0):
            self.PC = int(instruction.arg)
        else:
            self.PC += 1

    def HALT(self):
        self.PC = 0

    def PASS(self):
        self.PC += 1

if('-h' in sys.argv[1:] or '--help' in sys.argv[1:]):
    print(">>> Random access machine simulator <<<")
    print("Run with: python3 RAM.py [INPUT_REGISTERS_LIST] [-h/--help] [-i/--instructions] [-d/--debug] < RAM_PROGRAM_FILE")
    print("\nwhere:\n")
    print(">>> -h : prints a brief help")
    print(">>> -i : prints a list of instructions and their usage")
    print(">>> -d : runs machine in the debug mode")
    print("\n>>> EXAMPLE : python3 RAM.py 1 2 < prog")
    print("where the file prog contains this code:\n")
    print("# The content of the line after '#' will be ignored")
    print("READ 1 # r0 <- i1")
    print("STORE 1 # r1 <- r0")
    print("READ 2 # r0 <- i2")
    print("ADD 1 # r0 <- r0 + r1")
    print("ADD =1 # r0 <- r0 + 1")
    print("# a value which is stored in r0 corresponds to the RAM's output\n")
    print("Output: 4") 
    exit(0)

if('-i' in sys.argv[1:] or '--instructions' in sys.argv[1:]):
    print(">>> Random access machine simulator <<<")
    print("Types of arguments :")
    print("X : direct address of a register (or a line of the code)")
    print("(X) : indirect address of a register")
    print("=X : constant (or a line of the code)")
    print("Instructions:\n")
    print("HALT : stops execution of the code")
    print("HALF : divides a value in r0 by 2 and floors the value")
    print("READ X : puts a value which is stored in the input register X to r0")
    print("READ (X) : gets a value Y which is stored in rX and puts a value which is stored in the input register Y to r0")
    print("STORE X : puts the value which is stored in r0 to rX")
    print("STORE (X) : gets a value Y which is stored in rX and put a value which is stored in r0 to rY")
    print("JUMP X : continues from the line X")
    print("JUMP =X : continues from the line X")
    print("JPOS X : continues from the line X if r0 > 0")
    print("JPOS =X : continues from the line X if r0 > 0")
    print("JZERO X : continues from the line X if r0 = 0")
    print("JZERO =X : continues from the line X if r0 = 0")
    print("JNEG X : continues from the line X if r0 < 0")
    print("JNEG =X : continues from the line X if r0 < 0")
    print("LOAD X : puts the value which is stored in rX to r0")
    print("LOAD (X) : gets a value Y which is stored in rX and puts a value which is stored in rY to r0")
    print("LOAD =X : puts the value X to r0")
    print("ADD X : adds the value which is stored in rX to r0")
    print("ADD (X) : gets a value Y which is stored in rX and adds a value which is stored in rY to r0")
    print("ADD =X : adds the value X to r0")
    print("SUB X : subtracts the value which is stored in rX from r0")
    print("SUB (X) : gets a value Y which is stored in rX and subtracts a value which is stored in rY from r0")
    print("SUB =X : subtracts the value X from r0")
    exit(0)

if('-d' in sys.argv[1:] or '--debug' in sys.argv[1:]):
    if '-d' in sys.argv:
        sys.argv.remove('-d')
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
    for i in sys.argv[1:]:
        if(not i.isnumeric()):
                print("Error : Invalid non-numeric argument " + i)
                exit(1)
    parser = Parser()
    parser.getCode()
    ram = RAM(parser.getCode(), sys.argv[1:])
    print(">>> Debugging mode <<<")
    print("-----------------------")
    ram.debug()
    exit(0)

for i in sys.argv[1:]:
    if(not i.isnumeric()):
            print("Error : Invalid non-numeric argument " + i)
            print("Rerun with 'python3 RAM.py -h' to see a brief help")
            exit(1)

parser = Parser()

ram = RAM(parser.getCode(), sys.argv[1:])
print(ram.run())