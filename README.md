# RAM

Random access machine (shortly denoted as RAM) is a well-known model of computation. The power of RAM is equivalent to the power of a Turing machine. However, it's architecture is much more similar to current computers because it allows direct access to data registers, while a Turing machine needs to go through it's tape step by step to reach a single memory cell.

RAM can work with unlimited data registers which can store arbitrary large integers. Formally, the RAM consists of a finite set of input registers I = {i_1, i_2, ..., i_m}; a RAM program Π = {π_1, π_2, ..., π_k}, which is a finite set of instructions; a potentialy infinite set of data registers R = {r_0, r_1, r_2, ...} and a program counter κ.

## RAM instructions

There is a limited list of instructions which could be executed by a RAM. Most of the instructions take exactly one argument. We distinguish three types of arguments:

- X : direct memory access or a line number
- (X) : indirect memory access
- =X : constant or a line number

Some of the single argument instructions allow us to use all three types of arguments, while the others do not. Here is the list of all possible instructions which could be used in this RAM implementation.

- HALT : stops execution of the code and sets the program counter κ to 0
- HALF : divides a value in r_0 by 2 and floors the value
- PASS : does nothing (this instruction is also an internal representation of an empty line)

- READ X : puts a value which is stored in the input register X to r0
- READ (X) : gets a value Y which is stored in r_X and puts a value which is stored in the input register Y to r_0
- STORE X : puts the value which is stored in r_0 to r_X
- STORE (X) : gets a value Y which is stored in r_X and puts a value which is stored in r_0 to r_Y
- JUMP X : continues from the line X
- JUMP =X : continues from the line X
- JPOS X : continues from the line X if r_0 > 0
- JPOS =X : continues from the line X if r_0 > 0
- JZERO X : continues from the line X if r_0 = 0
- JZERO =X : continues from the line X if r_0 = 0
- JNEG X : continues from the line X if r_0 < 0
- JNEG =X : continues from the line X if r_0 < 0
- LOAD X : puts the value which is stored in r_X to r_0
- LOAD (X) : gets a value Y which is stored in rX and puts a value which is stored in r_Y to r_0
- LOAD =X : puts the value X to r_0
- ADD X : adds the value which is stored in r_X to r_0
- ADD (X) : gets a value Y which is stored in r_X and adds a value which is stored in r_Y to r_0
- ADD =X : adds the value X to r_0
- SUB X : subtracts the value which is stored in r_X from r_0
- SUB (X) : gets a value Y which is stored in r_X and subtracts a value which is stored in r_Y from r_0
- SUB =X : subtracts the value X from r_0

## RAM program

A RAM program is a sequence of RAM instructions. The execution of a RAM program stops as soons as the program counter κ happens to equal 0 (which could by done by executing HALT, JUMP 0, JZERO 0, JNEG 0, JPOS 0) or as soon as the last instruction of the program is executed (and it does not change the program flow by JUMP, JZERO, JNEG, JPOS). The output of the RAM program corresponds to a value which is stored in the accumulator r_0 as soon as the program stops it's execution.

This implementation allows us to use comments in the RAM program. Everything which is written after a symbol # would be considered to be a comment.

Note that each RAM instruction has to be writter on it's own line. Empty lines are allowed in this implementation. However, the internal representation of an empty line corresponds to a instruction PASS which could be seen in the debugging mode.

### Examples of a RAM program

Here are few examples of RAM programs. Note that the line numbers are not part of the code.

#### Maximum of two elements

```
1. READ 1 # r_0 = i_1
2. STORE 1 # r_1 = r_0, which means that r_1 == i_1
3. READ 2 # r_0 = i_2
4. SUB 1 # r_0 = i_2 - i_1
5. JNEG 8 # if(i_2 - i_1 < 0) κ = 8;
6. READ 2 # r_0 = i_2
7. HALT # κ = 0, the program stops, output : i_2
8. LOAD 1 # r_0 = i_1
9. HALT # κ = 0, the program stops, output : i_1
```

#### Integer division

```
1. READ 1 # r_0 = i_1
2. STORE 1 # r_1 = r_0, which means that r_1 == i_1
3. READ 2 # r_0 = i_2
4. STORE 2 # r_2 = r_0, which means that r_2 == i_2
5. LOAD 1 # r_0 = r_1
6. SUB 2 # r_0 = r_1 - r_2
7. JNEG 13 # if(r_1 - r_2 < 0) κ = 13;
8. STORE 1 # r_1 = r_0
9. LOAD 3 # r_0 = r_3
10. ADD =1 # r_0++
11. STORE 3 # r_3 = r_0
12. JUMP 5 # κ = 5;
13. LOAD 3 # r_0 = r_3
14. HALT # κ = 0, the program stops, output : i_1 div i_2
```

Note that in case of i_2 == 0, the code won't ever terminate.

## Running the simulator

Run with: `python3 RAM.py [INPUT_REGISTERS_LIST] [-h/--help] [-i/--instructions] [-d/--debug] < RAM_PROGRAM_FILE`

where

- `-h` : prints a brief help
- `-i` : prints a list of instructions and their usage
- `-d` : runs machine in the debug mode

### Example

`python3 RAM.py 20 8 < DIV`

where DIV is a file that contains the code shown above which computes the integer division.

Output: 2

### Debug mode

It is possible to use the debugging mode to see what is stored in the data registers after executing each step of computation. Consider the code shown above which computes the maximum of two elements. Suppose that the command below would be executed.

`python3 RAM.py 20 8 -d < MAX2`

The output would be as follows:

```
>>> Debugging mode <<<
-----------------------
Initial state:
Input registers : ['20', '8']
Data registers : {0: 0}
Program counter : 1
-----------------------
Step : 1
Program counter value : 1
Executing an instruction : READ 1
Input registers : ['20', '8']
Data registers : {0: 20}
New program counter value : 2
-----------------------
Step : 2
Program counter value : 2
Executing an instruction : STORE 1
Input registers : ['20', '8']
Data registers : {0: 20, 1: 20}
New program counter value : 3
-----------------------
Step : 3
Program counter value : 3
Executing an instruction : READ 2
Input registers : ['20', '8']
Data registers : {0: 8, 1: 20}
New program counter value : 4
-----------------------
Step : 4
Program counter value : 4
Executing an instruction : SUB 1
Input registers : ['20', '8']
Data registers : {0: -12, 1: 20}
New program counter value : 5
-----------------------
Step : 5
Program counter value : 5
Executing an instruction : JNEG 8
Input registers : ['20', '8']
Data registers : {0: -12, 1: 20}
New program counter value : 8
-----------------------
Step : 6
Program counter value : 8
Executing an instruction : LOAD 1
Input registers : ['20', '8']
Data registers : {0: 20, 1: 20}
New program counter value : 9
-----------------------
Step : 7
Program counter value : 9
Executing an instruction : HALT
Input registers : ['20', '8']
Data registers : {0: 20, 1: 20}
Program has ended succesfully.
-----------------------
Output : 20
```
