"""CPU functionality."""
from typing import List, Tuple
import sys

CALL = 0
HLT = 1
LDI = 2
PRN = 7
PUSH = 5
POP = 6
CALL = 16
RET = 17
JEQ = 21
JNE = 22
JMP = 20
SP = 7



class MASK:
    PC = 16
    OP = 31
    ALU = 32


class CPU:
    """Main CPU class."""

    def __init__(self) -> None:
        """Construct a new CPU."""
        self.alu_table = {0: 'ADD', 1: 'SUB', 2: 'MUL', 3: 'DIV', 7: 'CMP'}
        self.branch_table = {}

        self.branch_table[LDI] = self.LDI
        self.branch_table[PRN] = self.PRN
        self.branch_table[HLT] = self.HLT
        self.branch_table[PUSH] = self.PUSH
        self.branch_table[POP] = self.POP
        self.branch_table[CALL] = self.CALL
        self.branch_table[RET] = self.RET
        self.branch_table[JMP] = self.JMP
        self.branch_table[JNE] = self.JNE
        self.branch_table[JEQ] = self.JEQ

        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.IR = 0
        self.FL = 0
        self.MDR = 0
        self.MAR = 0

    def load(self, file) -> None:
        """Load a program into memory."""
        program = open(file, 'r').readlines()

        address = 0

        for line in program:
            # Parse out comments
            comment_split = line.strip().split("#")

            # Cast the numbers from strings to ints
            value = comment_split[0].strip()

            # Ignore blank lines
            if value == "":
                continue

            num = int(value, 2)

            self.ram[address] = num
            address += 1

    def alu(self, op: str, reg_a: int, reg_b: int) -> None:
        """ALU operations."""


        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self/reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            a = self.reg[reg_a]
            b = self.reg[reg_b]

            self.FL = 0

            self.FL = (self.FL ^ (a < b)) << 1
            self.FL = (self.FL ^ (a > b)) << 1
            self.FL = (self.FL ^ (a == b))
            # print(f'CMP FLAG - {self.FL} - {self.pc}')
            return


        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")
        
        self.reg[reg_a] = self.reg[reg_a] & 255

    def trace(self) -> None:
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, addr: int) -> int:
        if addr > 255:
            print('MEMORY ADDRESS OUT OF BOUNDS')
            exit()

        return self.ram[addr]

    def ram_write(self, addr: int, value: int) -> None:
        if addr > 255:
            print('MEMORY ADDRESS OUT OF BOUNDS')
            exit()

        self.ram[addr] = value

    def PRN(self, operands: tuple) -> None:
        op_a, op_b = operands
        print(self.reg[op_a])

    def LDI(self, operands: tuple) -> None:
        op_a, op_b = operands
        self.reg[op_a] = op_b

    def HLT(self, _) -> None:
        # self.trace()
        exit()

    def PUSH(self, operands: tuple) -> None:
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[operands[0]]) 

    def POP(self, operands: tuple) -> None:
        self.reg[operands[0]] = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def CALL(self, operands: tuple) -> None:
        self.PUSH((self.pc,))
        self.pc = operands[0]

    def RET(self, operands: tuple) -> None:
        self.POP((4,))
        self.pc = self.reg[4]
    
    def JMP(self, operands: tuple) -> None:
        self.pc = self.reg[operands[0]]

    def JEQ(self, operands: tuple) -> None:
        if self.FL == 1:
            self.JMP(operands)
        else:
            self.pc += 2

    def JNE(self, operands: tuple) -> None:
        if self.FL != 1:
            self.JMP(operands)
        else:
            self.pc += 2

    def run(self) -> None:
        """Run the CPU."""
        self.pc = 0
        try:
            while True:
                word = self.ram_read(self.pc)
                op = word & MASK.OP
                operands = (self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))

                if (word & MASK.ALU) == MASK.ALU:
                    # print(word, self.pc)
                    self.alu(self.alu_table[op], operands[0], operands[1])
                elif self.branch_table.get(op):
                    self.branch_table[op](operands)
                    
                if (word & MASK.PC) != MASK.PC:
                    self.pc += (word >> 6) + 1 
                    # print(self.pc)              

        except KeyboardInterrupt:
            self.trace()
