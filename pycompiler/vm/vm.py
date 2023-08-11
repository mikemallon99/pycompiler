from pycompiler.objects import Object, IntObject, BooleanObject, NullObject
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
            op = Opcode(self.instructions[ip])
            if op == Opcode.CONSTANT:
                index = int.from_bytes(self.instructions[ip+1:ip+3], byteorder='big')
                ip += 2
                err = self.push(self.constants[index])
                if err:
                    return err
            elif op == Opcode.ADD or op == Opcode.SUB or op == Opcode.MUL or op == Opcode.DIV:
                err = self._execute_binary_op(op)
                if err:
                    return err
            elif op == Opcode.EQUAL or op == Opcode.NOTEQUAL or op == Opcode.GREATERTHAN:
                err = self._execute_comparison(op)
                if err:
                    return err
            elif op == Opcode.BANG:
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
            elif op == Opcode.MINUS:
                operand: Object = self.pop()
                if isinstance(operand, IntObject):
                    err = self.push(IntObject(-1 * operand.value))
                    if err:
                        return err
                else:
                    return "- prefix is not supported for input type"
            elif op == Opcode.TRUE:
                err = self.push(BooleanObject(True))
                if err:
                    return err
            elif op == Opcode.FALSE:
                err = self.push(BooleanObject(False))
                if err:
                    return err
            elif op == Opcode.JUMP:
                pos = int.from_bytes(self.instructions[ip+1:ip+3], byteorder='big')
                ip = pos - 1
            elif op == Opcode.JUMPCOND:
                pos = int.from_bytes(self.instructions[ip+1:ip+3], byteorder='big')
                ip += 2

                if not self._is_truthy(self.pop()):
                    ip = pos - 1
            elif op == Opcode.POP:
                self.pop()
            elif op == Opcode.NULL:
                err = self.push(NullObject())
                if err:
                    return err
            ip += 1

        return None

    def _execute_binary_op(self, op: Opcode) -> Error:
        right: Object = self.pop()
        left: Object = self.pop()

        if isinstance(left, IntObject) and isinstance(right, IntObject):
            right_val: int = right.value
            left_val: int = left.value
            match op:
                case Opcode.ADD:
                    out_val = left_val + right_val
                case Opcode.SUB:
                    out_val = left_val - right_val
                case Opcode.MUL:
                    out_val = left_val * right_val
                case Opcode.DIV:
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
                case Opcode.EQUAL:
                    out_val = left_val == right_val
                case Opcode.NOTEQUAL:
                    out_val = left_val != right_val
                case Opcode.GREATERTHAN:
                    out_val = left_val > right_val
                case _:
                    return f"IntObject comparison not found for {op}"
            err = self.push(BooleanObject(out_val))
            if err:
                return err
        else:
            match op:
                case Opcode.EQUAL:
                    err = self.push(BooleanObject(left.value == right.value))
                case Opcode.NOTEQUAL:
                    err = self.push(BooleanObject(left.value != right.value))
                case Opcode.GREATERTHAN:
                    err = self.push(BooleanObject(left.value > right.value))
                case _:
                    return f"Object comparison not found for {op}"
            if err:
                return err

        return None

    def _is_truthy(self, obj: Object) -> bool:
        return bool(obj.value)
