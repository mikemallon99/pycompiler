from pycompiler.objects import Object, IntObject, BooleanObject
from pycompiler.compiler import Bytecode
from pycompiler.code import Instructions, Opcode, lookup_opcode

from typing import Optional

STACK_SIZE = 2048

Error = str


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

    def last_popped(self) -> Object:
        return self.stack[self.sp]

    def push(self, obj: Object) -> Optional[Error]:
        if self.sp >= STACK_SIZE:
            return "Stack Overflow"

        self.stack[self.sp] = obj
        self.sp += 1
        return None

    def pop(self) -> Object:
        self.sp -= 1
        return self.stack[self.sp]

    def run(self) -> Optional[Error]:
        ip = 0 
        while ip < len(self.instructions):
            op = self.instructions[ip]
            if op == Opcode.CONSTANT.value:
                index = int.from_bytes(self.instructions[ip+1:ip+3], byteorder='big')
                ip += 2
                err = self.push(self.constants[index])
                if err:
                    return err
            elif op == Opcode.ADD.value or op == Opcode.SUB.value or op == Opcode.MUL.value or op == Opcode.DIV.value:
                err = self._execute_binary_op(op)
                if err:
                    return err
            elif op == Opcode.EQUAL.value or op == Opcode.NOTEQUAL.value or op == Opcode.GREATERTHAN.value:
                err = self._execute_comparison(op)
                if err:
                    return err
            elif op == Opcode.BANG.value:
                operand: Object = self.pop()
                match bool(operand.value):
                    case True:
                        err = self.push(BooleanObject(False))
                        if err:
                            return err
                    case False:
                        err = self.push(BooleanObject(True))
                        if err:
                            return err
                    case _:
                        return "Bang operation failed."
            elif op == Opcode.MINUS.value:
                operand: Object = self.pop()
                if isinstance(operand, IntObject):
                    err = self.push(IntObject(-1 * operand.value))
                    if err:
                        return err
                else:
                    return "- prefix is not supported for input type"
            elif op == Opcode.TRUE.value:
                err = self.push(BooleanObject(True))
                if err:
                    return err
            elif op == Opcode.FALSE.value:
                err = self.push(BooleanObject(False))
                if err:
                    return err
            elif op == Opcode.POP.value:
                self.pop()
            ip += 1

        return None

    def _execute_binary_op(self, op: Opcode) -> Error:
        right: Object = self.pop()
        left: Object = self.pop()

        if isinstance(left, IntObject) and isinstance(right, IntObject):
            right_val: int = right.value
            left_val: int = left.value
            match op:
                case Opcode.ADD.value:
                    out_val = left_val + right_val
                case Opcode.SUB.value:
                    out_val = left_val - right_val
                case Opcode.MUL.value:
                    out_val = left_val * right_val
                case Opcode.DIV.value:
                    out_val = left_val / right_val
                case _:
                    return f"IntObject arithmetic not found for {op}"

            err = self.push(IntObject(out_val))
            if err:
                return err
        else:
            return "Cannot find arithmetic function for input types."

        return None

    def _execute_comparison(self, op: Opcode) -> Error:
        right: Object = self.pop()
        left: Object = self.pop()

        if isinstance(left, IntObject) and isinstance(right, IntObject):
            right_val: int = right.value
            left_val: int = left.value
            match op:
                case Opcode.EQUAL.value:
                    out_val = left_val == right_val
                case Opcode.NOTEQUAL.value:
                    out_val = left_val != right_val
                case Opcode.GREATERTHAN.value:
                    out_val = left_val > right_val
                case _:
                    return f"IntObject comparison not found for {op}"
            err = self.push(BooleanObject(out_val))
            if err:
                return err
        else:
            match op:
                case Opcode.EQUAL.value:
                    err = self.push(BooleanObject(left.value == right.value))
                case Opcode.NOTEQUAL.value:
                    err = self.push(BooleanObject(left.value != right.value))
                case Opcode.GREATERTHAN.value:
                    err = self.push(BooleanObject(left.value > right.value))
                case _:
                    return f"Object comparison not found for {op}"
            if err:
                return err

        return None

