from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
import sys

'''
From the command line in the directory of checkin3b4a.py, execute:
python checkin3b4a.py <name of/path to C program>

After running, the set of index vectors, index variables, and index variable update statements
for each loop in the program will display in the terminal.
'''

# Visitor stores all index variables
class IndexSetVisitor(NodeVisitor):
    def __init__(self):
        self.indexset = {}
        self.updatestatements = {}
        self.loops = []
        self.indexvectors = {}
        self.stmts = {}
        self.blocks = set()
        
    #Converts Binary Operator node into string format 
    def bop2str(self, bopnode):
        if isinstance(bopnode.right, Constant):
            return (bopnode.left.name + " = " + bopnode.left.name + str(bopnode.op) +str(bopnode.right.value))
        else:
            return (bopnode.left.name + "=" + bopnode.left.name + str(bopnode.op) + str(bopnode.right.name))
        
    #Helper function for visit_ArrayRef. Handles array references with binary operators that themselves 
    #contain an array reference.  
    def binary_subscript(self, bopnode, top_fornode):
        #If the node's left hand side is a variable not in the index set, it adds it to the index set
        #and initializes an empty updatestatements dictionary for the index variable
        if bopnode.left.name not in self.indexset[top_fornode]:
            if isinstance(bopnode.left, ID):
                self.indexset[top_fornode].add(bopnode.left.name)
                self.updatestatements[top_fornode][bopnode.left.name] = []
        #If the node's right hand side is a variable not in the index set, it adds it to the index set
        # and initializes an empty updatestatements dictionary for the index variable
        if bopnode.right.name not in self.indexset[top_fornode]:
            if isinstance(bopnode.right, ID):
                self.indexset[top_fornode].add(bopnode.right.name)
                self.updatestatements[top_fornode][bopnode.right.name] = []
                
    #Coordinates visits to array references within binary operators. Handles nested binary operators.         
    def visit_BinaryOp(self, bopnode, top_fornode):
        if isinstance(bopnode.right, Assignment):
            self.visit_Assignment(bopnode.right, top_fornode)
        if isinstance(bopnode.right, ArrayRef):
            self.visit_ArrayRef(bopnode.right, top_fornode)
        if isinstance(bopnode.left, ArrayRef):
            self.visit_ArrayRef(bopnode.left, top_fornode)
        if isinstance(bopnode.right, BinaryOp):
            self.visit_BinaryOp(bopnode.right, top_fornode)
        if isinstance(bopnode.left, BinaryOp):
            self.visit_BinaryOp(bopnode.left, top_fornode)
    
    #Visitor for function call nodes
    def visit_FuncCall(self, funcnode, top_fornode=None):
        #goes through the expressions list of the function call to visit 
        #array references and binary operators
        for node in funcnode.args.exprs:
            try:
                if isinstance(node,ArrayRef):
                    self.visit_ArrayRef(node, top_fornode)
                if isinstance(node,BinaryOp):
                    self.visit_BinaryOp(node, top_fornode)
            except:
                pass
            
   #Visitor for array reference nodes
    def visit_ArrayRef(self, arefnode, top_fornode=None):
        #If the array reference is not in the index set and the subscript is variable
        #it adds it to the index set and initializes an empty updatestatements dictionary
        #for the variable
        if arefnode.subscript not in self.indexset[top_fornode]:
            if isinstance(arefnode.subscript, ID):
                self.indexset[top_fornode].add(arefnode.subscript.name)
                self.updatestatements[top_fornode][arefnode.subscript.name] = []
        #If the array reference subscript is a binary operator, it calls a helper function
        #to collect any index variables in the subscript
        if isinstance(arefnode.subscript, BinaryOp):
            self.binary_subscript(arefnode.subscript, top_fornode)
        if isinstance(arefnode.name, ArrayRef):
            self.visit_ArrayRef(arefnode.name, top_fornode)
        if isinstance(arefnode.subscript, ArrayRef):
            self.visit_ArrayRef(arefnode.subscript, top_fornode)
        if isinstance(arefnode.subscript, Assignment):
            self.indexset.add(arefnode.subscript.lvalue.lname)
        if isinstance(arefnode.subscript, Assignment):
            self.visit_Assignment(arefnode.subscript.right, top_fornode)
        #Handles array reference subscripts which have an expression list
        #i.e b[i-p, j-p] and collects index variables from these subscripts
        if isinstance(arefnode.subscript, ExprList):
            for expr in arefnode.subscript.exprs:
                self.binary_subscript(expr, top_fornode)
    
    #Visitor for block nodes
    def visit_Block(self, blocknode, top_fornode=None):
        self.blocks.add(blocknode)
        #Iterates through block items in block
        for node in blocknode.block_items:
            try:
                if isinstance(node,Assignment):
                    self.visit_Assignment(node, top_fornode)
                if isinstance(node,If):
                    self.visit_If(node, top_fornode)
                #Handles nested for loops within blocks
                if isinstance(node,For):
                    self.visit_For(node, top_fornode)
            except:
                pass
        #Second pass to handle index variable update statements
        #that occur before the index variable is referenced
        for node in blocknode.block_items:
            try:
                if isinstance(node,Assignment):
                    self.visit_Assignment(node, top_fornode)
                if isinstance(node,If):
                    self.visit_If(node, top_fornode)
                if isinstance(node,For):
                    self.visit_For(node, top_fornode)
            except:
                pass
    
    #Visitor for if nodes
    def visit_If(self, ifnode, top_fornode=None):
        #Visits both the if true branch and if false branch
        if isinstance(ifnode.cond, BinaryOp):
            self.visit_BinaryOp(ifnode.cond, top_fornode)
        if isinstance(ifnode.cond, BinaryOp):
            self.visit_BinaryOp(ifnode.cond, top_fornode)
        thenvisitor = copy.deepcopy(self)
        elsevisitor = copy.deepcopy(self)
        thenvisitor.visit_Block(ifnode.iftrue)
        if ifnode.iffalse is not None:
            elsevisitor.visit_Block(ifnode.iffalse, top_fornode)
        self.visit_Block(ifnode.iftrue, top_fornode)
        self.visit_Block(ifnode.iffalse, top_fornode)
    
    #Visitor for assignment nodes
    def visit_Assignment(self, anode, top_fornode=None):
        #Updates any updatestatement dictionaries for assignments where the 
        #variable being written to is an index variable
        if anode.lvalue.name in self.indexset[top_fornode]:
            if isinstance(anode.rvalue, BinaryOp):
                string = self.bop2str(anode.rvalue)
            if isinstance(anode.rvalue, FuncCall):
                string = str(anode.rvalue)
            self.updatestatements[top_fornode][anode.lvalue.name].extend([string])
        #Adds any index variables being read by the assignment
        if isinstance(anode.rvalue, ArrayRef):
            self.visit_ArrayRef(anode.rvalue, top_fornode)
        if isinstance(anode.rvalue, FuncCall):
            self.visit_FuncCall(anode.rvalue, top_fornode)
        if isinstance(anode.rvalue, BinaryOp):
            self.visit_BinaryOp(anode.rvalue, top_fornode)
        if isinstance(anode.lvalue, ArrayRef):
            self.visit_BinaryOp(anode.lvalue, top_fornode)
        if isinstance(anode.rvalue, Ternary):
            if isinstance(anode.rvalue.cond, ArrayRef):
                self.visit_ArrayRef(anode.rvalue.cond, top_fornode)
                
    #Visitor for for nodes
    def visit_For(self, fornode, top_fornode=None):
        self.loops.append(fornode)
        
        #If the for node is a nested for node, it will add the index vector to
        #the existing set of index vectors of the outermost for node 
        if top_fornode is not None:
            if(isinstance(fornode.init, Assignment)):
                self.indexvectors[top_fornode].append(fornode.init.lvalue.name)
            if(isinstance(fornode.init, DeclList)):
                for decl in fornode.init.decls:
                    self.indexvectors[fornode].append(decl.name)
        #If the for node does not have a parent that is a for node, it is the 
        #outermost for nod
        else:
            #Denote this node as being the outermost for node of a loop nest
            #Initializes loop nest dictionaries and sets required for checkin 3b and 4a
            top_fornode = fornode
            self.indexset[top_fornode] = set()
            if top_fornode not in self.updatestatements.keys():
                self.updatestatements[top_fornode] = {}
            if(isinstance(fornode.init, Assignment)):
                self.indexvectors[fornode] = [fornode.init.lvalue.name]
            if(isinstance(fornode.init, DeclList)):
                self.indexvectors[fornode] = []
                for decl in fornode.init.decls:
                    self.indexvectors[fornode].append(decl.name)
        if isinstance(fornode.stmt, Block):
            # map node id to statements
            self.stmts[fornode.nid] = fornode
            # store 'next' statement in the for declaration
            updatenid = fornode.next.nid
            for node in fornode.stmt.block_items:
                try:
                    if isinstance(node,Assignment):
                        self.visit_Assignment(node, top_fornode)
                    if isinstance(node,If):
                        self.visit_If(node, top_fornode)
                    self.visit_For(node, top_fornode)
                except:
                    pass
            #visit the 'next' statement in the for declaration
            #to add the loop update statements for index variables 
            self.visit_Assignment(fornode.next, top_fornode)
            self.stmts[updatenid] = fornode.next

    #Helper function can be used to print a binary operator strings
    def str_of_bop(sid, lnode, rnode):
        rdefs = self.stmt_rdefs[sid]
        stmt = self.stmts.get(sid)
        srepr = "statement %i (%s)" % (sid, stmt)
        if stmt.coord is not None:
            srepr += " at line %i:\n" % stmt.coord.line
        else:
            srepr += ":\n"

        for (vname, sidl) in rdefs.aslist():
            srepr += "\t%s <-- {%s}\n" % (str(vname),
                                          ", ".join(list(map(str, list(map(lambda x: self.stmts[x], sidl))))))
        return srepr

class FuncIndexSetVisitor(NodeVisitor):
    def __init__(self):
        # The dict associates function names to write sets:
        self.indexsets = {}
        self.updatesets = {}
        self.indexvectors = {}

    def visit_FuncDef(self, funcdef):
        # Create an IndexSet visitor for the body of the function
        isv = IndexSetVisitor()
        # Execute it on the function's body
        isv.visit(funcdef.body)
        # Now it contains the index set of the function
        self.indexsets[funcdef] = isv.indexset
        self.updatesets[funcdef] = isv.updatestatements
        self.indexvectors[funcdef] = isv.indexvectors


if __name__ == "__main__":
    sys.path.extend(['.', '..'])

    if len(sys.argv) != 2:
        print ("Usage: project1 <input_file>")
        sys.exit(0)

    file = sys.argv[1]

    ast = parse_file(file)
    # convert to minic ast
    m_ast = transform(ast)

    fiv = FuncIndexSetVisitor()
    fiv.visit(m_ast)
    for fname, indexsets in fiv.indexsets.items():
        print ("%s has nested loops with the following properties:" % fname)
        for loop, indexset in indexsets.items():
            print ("\t%s has index %r" % (loop, indexset))
            print ("\t%s has update statements %r" % (loop, fiv.updatesets[fname][loop]))
            print ("\t%s has index vectors %r" % (loop, fiv.indexvectors[fname][loop]))
