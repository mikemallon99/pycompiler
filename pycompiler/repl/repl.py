from pycompiler.parser import Parser
from pycompiler.lexer import Lexer
from pycompiler.compiler import Compiler
from pycompiler.vm import VM

from typing import List

def run():
    while True:
        line = input(">> ")
        ast: List[Statement] = Parser(Lexer(line)).parse()

        compiler = Compiler()
        err = compiler.compile(ast)
        if err:
            print(err)
            continue

        vm = VM(compiler.bytecode())
        err = vm.run()
        if err:
            print(err)
            continue

        print(vm.last_popped())
    
