from pycparser import parse_file
from minic.c_ast_to_minic import transform
from minic.minic_ast import *
import sys


# Identifying Live Variables in functions which include for, while loop and return statement.
# If statement still needs to be checked, may not work


# Function definition from tutorial.py modifed
class FunctionDefVisitor(NodeVisitor):
    def visit_FuncDef(self, funcdef):
        if funcdef.decl.name != '__main__':
            #Create Visitor object & Visit the functions body.
            visitor = LiveVisitor()
            visitor.visit(funcdef.body)
            for item in visitor.livevariables:
                print(item, "is a live variable")

class LiveVisitor(NodeVisitor):
    # Class which analyzes the loop body inherited from minic_ast
    def __init__(self):
        self.livevariables = []
        self.nodes = []

    # Return Statement
    def visit_Return(self, Return):
        self.nodes.append(Return)
        if len(self.nodes) != 0:
            for node in self.nodes:
                if isinstance(node, For) or isinstance(node, While) or isinstance(node, If):
                    variable = Return.expr.name
                    self.livevariables.append(variable)
    # For Loop
    def visit_For(self, For):
        self.nodes.append(For)

    # For While Loop
    def visit_While(self, While):
        self.nodes.append(While)

    # Needs to be checked but for If statement
    def visit_If(self, If):
        self.nodes.append(If)


if __name__ == "__main__":
    sys.path.extend(['.', '..'])
    for i in range(1, 5):
        # AST to work with
        ast = parse_file("./project1inputs/p1_input{}.c".format(i))
        # convert to minic ast
        m_ast = transform(ast)
        print("Live Variable Analysis for" + " p1_input{}.txt".format(i))
        FunctionDefVisitor().visit(m_ast)
