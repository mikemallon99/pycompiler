from pycompiler.objects import Object
from pycompiler.compiler import Bytecode
from pycompiler.code import Instructions, Opcode

STACK_SIZE = 2048


class VM:
    def __init__(self, bytecode: Bytecode):
        self.instructions: Instructions = bytecode[0]
        self.constants: List[Object] = bytecode[1]
        
        self.stack: List[Object] = [Object()] * STACK_SIZE
        self.sp: int = 0

    def stack_top(self) -> Object:
        if self.sp == 0:
            return Object()
        return self.stack[self.sp - 1]

    def run(self):
        for ip in range(0, len(self.instructions)):
            op: Opcode = Opcode.NULL
