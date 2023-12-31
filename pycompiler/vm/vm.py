from pycompiler.objects import (
    Object,
    IntObject,
    BooleanObject,
    NullObject,
    StringObject,
    ArrayObject,
    MapObject,
    CompiledFunctionObject,
    ClosureObject,
    Builtin,
    BUILTINS,
)
from pycompiler.compiler import Bytecode
from pycompiler.code import Instructions, Opcode

from typing import List, Dict

STACK_SIZE = 2048
GLOBALS_SIZE = 65536

Error = str


class Frame:
    def __init__(self, cl, base_pointer: int) -> None:
        self.ip: int = -1
        self.cl: ClosureObject = cl
        self.base_pointer: int = base_pointer

    def get_instructions(self) -> Instructions:
        return self.cl.func.value


class VM:
    def __init__(self, bytecode: Bytecode):
        self.constants: List[Object] = bytecode[1]

        self.frames: List[Frame] = [Frame(ClosureObject(CompiledFunctionObject(bytecode[0], 0, 0), []), 0)]
        self.frame_index: int = 0

        self.stack: List[Object] = [Object()] * STACK_SIZE
        self.sp: int = 0

        self.globals: List[Object] = [Object()] * GLOBALS_SIZE

    def stack_top(self) -> Object:
        if self.sp == 0:
            return Object()
        return self.stack[self.sp - 1]

    def last_popped(self) -> Object:
        return self.stack[self.sp]

    def push(self, obj: Object) -> Error | None:
        if self.sp >= STACK_SIZE:
            return "Stack Overflow"

        self.stack[self.sp] = obj
        self.sp += 1
        return None

    def pop(self) -> Object:
        self.sp -= 1
        return self.stack[self.sp]

    def run(self) -> Error | None:
        ip: int
        ins: Instructions
        op: Opcode
        operand: Object

        while self._current_frame().ip < len(self._current_frame().get_instructions()) - 1:
            self._current_frame().ip += 1
            ip = self._current_frame().ip
            ins = self._current_frame().get_instructions()
            op = Opcode(ins[ip])

            if op == Opcode.CONSTANT:
                index = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2
                err = self.push(self.constants[index])
                if err:
                    return err
            elif op == Opcode.CLOSURE:
                index = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                num_free = int.from_bytes(
                    ins[ip + 3 : ip + 4], byteorder="big"
                )
                self._current_frame().ip += 3
                free = []
                for i in range(0, num_free):
                    free.append(self.stack[self.sp-num_free+i])
                err = self.push(ClosureObject(self.constants[index], free))
                if err:
                    return err
            elif (
                op == Opcode.ADD
                or op == Opcode.SUB
                or op == Opcode.MUL
                or op == Opcode.DIV
            ):
                err = self._execute_binary_op(op)
                if err:
                    return err
            elif (
                op == Opcode.EQUAL or op == Opcode.NOTEQUAL or op == Opcode.GREATERTHAN
            ):
                err = self._execute_comparison(op)
                if err:
                    return err
            elif op == Opcode.BANG:
                operand = self.pop()
                err = self.push(BooleanObject(not self._is_truthy(operand)))
                if err:
                    return err
            elif op == Opcode.MINUS:
                operand = self.pop()
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
                pos = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip = pos - 1
            elif op == Opcode.JUMPCOND:
                pos = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2

                if not self._is_truthy(self.pop()):
                    self._current_frame().ip = pos - 1
            elif op == Opcode.SETGLOBAL:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2
                self.globals[idx] = self.pop()
            elif op == Opcode.GETGLOBAL:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2
                err = self.push(self.globals[idx])
                if err:
                    return err
            elif op == Opcode.SETLOCAL:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 2], byteorder="big"
                )
                self._current_frame().ip += 1
                self.stack[self._current_frame().base_pointer + idx] = self.pop()
            elif op == Opcode.GETLOCAL:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 2], byteorder="big"
                )
                self._current_frame().ip += 1
                err = self.push(self.stack[self._current_frame().base_pointer + idx])
                if err:
                    return err
            elif op == Opcode.GETBUILTIN:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 2], byteorder="big"
                )
                self._current_frame().ip += 1
                err = self.push(BUILTINS[idx])
                if err:
                    return err
            elif op == Opcode.GETFREE:
                idx = int.from_bytes(
                    ins[ip + 1 : ip + 2], byteorder="big"
                )
                self._current_frame().ip += 1
                err = self.push(self._current_frame().cl.free[idx])
                if err:
                    return err
            elif op == Opcode.CURRENTCLOSURE:
                err = self.push(self._current_frame().cl)
                if err:
                    return err
            elif op == Opcode.POP:
                self.pop()
            elif op == Opcode.ARRAY:
                arr_size = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2
                elems: List[Object] = [Object()] * arr_size
                for i in range(0, arr_size):
                    elems[i] = self.stack[self.sp - arr_size + i]
                self.sp = self.sp - arr_size
                err = self.push(ArrayObject(elems))
                if err:
                    return err
            elif op == Opcode.MAP:
                map_size = int.from_bytes(
                    ins[ip + 1 : ip + 3], byteorder="big"
                )
                self._current_frame().ip += 2
                map: Dict[Object, Object] = {}
                for i in range(0, map_size):
                    key: Object = self.stack[self.sp - map_size * 2 + 2 * i]
                    value: Object = self.stack[self.sp - map_size * 2 + 2 * i + 1]
                    map[key] = value

                self.sp = self.sp - map_size * 2
                err = self.push(MapObject(map))
                if err:
                    return err
            elif op == Opcode.INDEX:
                right = self.pop()
                left = self.pop()
                if isinstance(left, ArrayObject) and isinstance(right, IntObject):
                    err = self.push(left.get(right))
                    if err:
                        return err
                elif isinstance(left, MapObject):
                    err = self.push(left.get(right))
                    if err:
                        return err
                else:
                    return "Index operator not implemented for input types"
            elif op == Opcode.CALL:
                num_args = int.from_bytes(
                    ins[ip + 1 : ip + 2], byteorder="big"
                )
                self._current_frame().ip += 1
                err = self._execute_call(num_args)
                if err:
                    return err
            elif op == Opcode.RETURNVALUE:
                value = self.pop()
                # Return to base ptr & Pop compiled function object from stack
                self.sp = self._current_frame().base_pointer - 1
                self._pop_frame()
                err = self.push(value)
                if err:
                    return err
            elif op == Opcode.RETURN:
                # Return to base ptr & Pop compiled function object from stack
                self.sp = self._current_frame().base_pointer - 1
                self._pop_frame()
                err = self.push(NullObject())
                if err:
                    return err
            elif op == Opcode.NULL:
                err = self.push(NullObject())
                if err:
                    return err

        return None

    def _execute_call(self, num_args: int) -> Error | None:
        fn = self.stack[self.sp - num_args - 1]
        if isinstance(fn, ClosureObject):
            return self._execute_closure(fn, num_args)
        elif isinstance(fn, Builtin):
            return self._execute_builtin(fn, num_args)
        else:
            return "Error attempting to call non-function"

    def _execute_closure(self, cl: ClosureObject, num_args: int) -> Error | None:
        if num_args != cl.func.num_args:
            return f"wrong number of args: want {cl.func.num_args}, got {num_args}"
        frame = Frame(cl, self.sp - num_args)
        self._push_frame(frame)
        self.sp = frame.base_pointer + cl.func.num_locals

    def _execute_builtin(self, fn: Builtin, num_args: int) -> Error | None:
        args = self.stack[self.sp - num_args:self.sp]
        result = fn.func(args)
        self.sp = self.sp - num_args - 1
        if isinstance(result, Error):
            return result
        err = self.push(result)
        if err:
            return err


    def _execute_binary_op(self, op: Opcode) -> Error | None:
        right: Object = self.pop()
        left: Object = self.pop()

        if isinstance(left, IntObject) and isinstance(right, IntObject):
            right_int: int = right.value
            left_int: int = left.value
            out_int: int
            match op:
                case Opcode.ADD:
                    out_int = left_int + right_int
                case Opcode.SUB:
                    out_int = left_int - right_int
                case Opcode.MUL:
                    out_int = left_int * right_int
                case Opcode.DIV:
                    out_int = left_int // right_int
                case _:
                    return f"IntObject arithmetic not found for {op}"
            err = self.push(IntObject(out_int))
            if err:
                return err
        elif isinstance(left, StringObject) and isinstance(right, StringObject):
            right_str: str = right.value
            left_str: str = left.value
            out_str: str
            match op:
                case Opcode.ADD:
                    out_str = left_str + right_str
                case _:
                    return f"IntObject arithmetic not found for {op}"
            err = self.push(StringObject(out_str))
            if err:
                return err
        else:
            return "Cannot find arithmetic function for input types."

        return None

    def _execute_comparison(self, op: Opcode) -> Error | None:
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
        elif isinstance(left, NullObject) and isinstance(right, NullObject):
            err = self.push(BooleanObject(True))
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
        if isinstance(obj, NullObject):
            return False
        else:
            return bool(obj.value)

    def _current_frame(self) -> Frame:
        return self.frames[self.frame_index]

    def _push_frame(self, frame: Frame) -> None:
        self.frames.append(frame)
        self.frame_index += 1

    def _pop_frame(self) -> Frame:
        self.frame_index -= 1
        return self.frames.pop()
