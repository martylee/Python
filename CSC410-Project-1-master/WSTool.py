from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
import sys

'''
WSTool extracts the set of written variables from each 'for' or 'while' loop
in a C program.

From the command line in the directory of WSTool.py, execute:
python WSTool.py <name of/path to C program>

After running, the set of written variables will display in the terminal.
'''

class WriteSetVisitor(NodeVisitor):
    def __init__(self):
        self.writeset = set()

    def visit_If(self, ifnode):
        wif = WriteSetVisitor()
        welse = WriteSetVisitor()
        wif.visit(ifnode.iftrue)
        welse.visit(ifnode.iffalse)
        self.writeset.union(wif.writeset.union(welse.writeset.union()))

    def visit_For(self, fornode):
        if fornode.init is not None and isinstance(fornode.init, Assignment):
            self.writeset.add(fornode.init.lvalue.name)
        if fornode.next is not None and isinstance(fornode.next, Assignment):
            self.writeset.add(fornode.next.lvalue.name)
        if fornode.stmt is not None and isinstance(fornode.stmt, Block):
            for node in fornode.stmt.block_items:
                if node is not None and isinstance(node, Assignment):
                    self.writeset.add(node.lvalue.name)

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


class PreLoopAssignmentVisitor(NodeVisitor):
    def __init__(self):
        self.initial = {}

    def visit_PreLoopVisitor(self, funcdefnode):
        print("HI") #it doesn't reach here =(....
        if funcdefnode is not None and isinstance(funcdefnode, FuncDef):
            print("HI2")
            for asnode in funcdefnode.body:
                if isinstance(asnode, Assignment):
                    if isinstance(asnode.rvalue, Constant):
                        self.currdefs[asnode.lvalue.name] = asnode.rvalue.value
                    else:
                        if isinstance(declnode.rvalue.right, Constant):
                            self.currdefs[asnode.lvalue.name] = (asnode.lvalue.name + " = " + asnode.rvalue.left.name + str(asnode.rvalue.op) +str(asnode.rvalue.right.value))

class ReachingDefinitionsVisitor(NodeVisitor):
    def __init__(self):
        self.currdefs = {}
        self.reachingdefs = {}
        self.currloop = 0

    def visit_For(self, fornode):
        if fornode.stmt is not None and isinstance(fornode.stmt, Block):
            for node in fornode.stmt.block_items:
                if node is not None and isinstance(node, Assignment):
                    if isinstance(node.rvalue, BinaryOp):
                        if isinstance(node.rvalue.right, Constant):
                            self.reachingdefs[node.lvalue.name] = (node.lvalue.name + " = " + node.rvalue.left.name + str(node.rvalue.op) +str(node.rvalue.right.value))
                        else:
                            self.reachingdefs[node.lvalue.name] = (node.lvalue.name + "=" + node.rvalue.left.name + str(node.rvalue.op) + str(node.rvalue.right.name))
                    if isinstance(node.rvalue, Constant):
                        self.reachingdefs[node.lvalue.name] = node.rvalue.value
        if fornode.init is not None and isinstance(fornode.next, Assignment):
            self.reachingdefs[fornode.init.lvalue.name] = fornode.next.lvalue.name + " = " + fornode.next.rvalue.left.name + str(node.rvalue.op) + str(fornode.next.rvalue.right.value)

class FuncWriteSetVisitor(NodeVisitor):
    def __init__(self):
        self.reachingdefsets = {}

    def visit_FuncDef(self, funcdef):
        wsv = WriteSetVisitor()
        wsv.visit(funcdef.body)
        self.writesets[funcdef.decl.name] = wsv.writeset

class FuncReachingDefinitionsVisitor(NodeVisitor):
    def __init__(self):
        self.reachingdefsets = {}

    def visit_FuncDef(self, funcdef):
        rdv = ReachingDefinitionsVisitor()
        rdv.visit(funcdef.body)
        self.reachingdefsets[funcdef.decl.name] = rdv.reachingdefs

if __name__ == "__main__":
    sys.path.extend(['.', '..'])

    #if len(sys.argv) != 2:
        #print ("Usage: project1 <input_file>")
        #sys.exit(0)


    #file = sys.argv[1]
    file = "./project1inputs/p1_input1.c"

    ast = parse_file(file)

    # convert to minic ast
    m_ast = transform(ast)

    #sast.show()

    frd = FuncReachingDefinitionsVisitor()
    frd.visit(m_ast)

    pla = PreLoopAssignmentVisitor()
    pla.visit(m_ast)


    for reachingdef, value in pla.initial.items():
        print("%s contains %r" % (reachingdef, value))
    for fname, reachingdefs in frd.reachingdefsets.items():
        print ("%s writes in %r" % (fname, reachingdefs))
