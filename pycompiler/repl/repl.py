from pycompiler.parser import Parser
from pycompiler.lexer import Lexer
from pycompiler.compiler import Compiler
from pycompiler.vm import VM

from typing import List


def new_compiler_with_state(old_compiler: Compiler) -> Compiler:
    new_compiler = Compiler()
    new_compiler.symbol_table = old_compiler.symbol_table
    return new_compiler


def new_vm_with_state(old_vm: VM, bytecode) -> VM:
    new_vm = VM(bytecode)
    new_vm.globals = old_vm.globals
    return new_vm


def run():
    compiler = None
    vm = None
    while True:
        line = input(">> ")
        ast: List[Statement] = Parser(Lexer(line)).parse()

        if compiler:
            compiler = new_compiler_with_state(compiler)
        else:
            compiler = Compiler()
        err = compiler.compile(ast)
        if err:
            print(err)
            continue

        if vm:
            vm = new_vm_with_state(vm, compiler.bytecode())
        else:
            vm = VM(compiler.bytecode())
        err = vm.run()
        if err:
            print(err)
            continue

        print(vm.last_popped())
