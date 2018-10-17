from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
#from minic.analysis import *
import copy
import sys

'''
From the command line in the directory of WSTool.py, execute:
python main.py <name of/path to C program>

'''

class ArrayIndicesVisitor(NodeVisitor):
    def __init__(self):
        # list of dictionaries that stores an index variable as a key
        # and a list of its update statements as its value
        self.loop_list = []

    def visit_For(self, fornode):
        indices = {}
        self.loop_list.append(indices)
        #print(fornode.next)
        if fornode.next is not None and isinstance(fornode.next, Assignment):
            loop_counter = fornode.next.lvalue
            loop_update = fornode.next.rvalue
        if fornode.stmt is not None and isinstance(fornode.stmt, Block):
            for node in fornode.stmt.block_items:
                if node is not None and isinstance(node, Assignment):
                    #indices_copy = copy.deepcopy(indices)
                    #indices_keys = indices_copy.keys()
                    if isinstance(node.lvalue, ArrayRef):
                        if node.lvalue.subscript not in indices.keys():
                            indices[node.lvalue.subscript] = []
                    else:
                        if node.lvalue in indices.keys():
                            indices[node.lvalue.subscript].append(node)
                

    def visit_While(self, whilenode):
        if whilenode.stmt is not None and isinstance(whilenode.stmt, Block):
            for node in whilenode.stmt.block_items:
                if node is not None and isinstance(node, Assignment):
                    self.writeset.add(node.lvalue.name)

    def visit_DoWhile(self, downode):
        if downode.stmt is not None and isinstance(downode.stmt, Block):
            for node in downode.stmt.block_items:
                if node is not None and isinstance(node, Assignment):
                    self.writeset.add(node.lvalue.name)
        

if __name__ == "__main__":
    sys.path.extend(['.', '..'])

    
    if len(sys.argv) != 2:
        print ("Usage: main <input_file>")
        sys.exit(0)

    file = sys.argv[1]
    

    #file = "./project1inputs/p1_input3.c"
    #file = "./project1inputs/constructs.c"

    ast = parse_file(file)

    # convert to minic ast
    m_ast = transform(ast)

    aiv = ArrayIndicesVisitor()
    aiv.visit(ast)
    i = 0
    while i < len(aiv.loop_list):
        print("Loop " + str(i + 1) + " :\n")
        for key in aiv.loop_list[i].keys():
            print("variable: " + key + "Statements :" + aiv.loop_list[i][key])
        i += 1
