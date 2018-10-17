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
        
class FuncWriteSetVisitor(NodeVisitor):
    def __init__(self):
        self.writesets = {}

    def visit_FuncDef(self, funcdef):
        wsv = WriteSetVisitor()
        wsv.visit(funcdef.body)
        self.writesets[funcdef.decl.name] = wsv.writeset

if __name__ == "__main__":
    sys.path.extend(['.', '..'])
    
    #if len(sys.argv) != 2:
        #print ("Usage: project1 <input_file>")
        #sys.exit(0)
    

    #file = sys.argv[1]
    file = "./project1inputs/loop_analysis.c"
    
    ast = minic_parse_file(file)

    # convert to minic ast
    m_ast = transform(ast)

    fws = FuncWriteSetVisitor()
    fws.visit(m_ast)
    for fname, writeset in fws.writesets.items():
        print ("%s writes in %r" % (fname, writeset))