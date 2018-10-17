from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
from check_in1 import *
from check_in2 import *
import sys
import copy

class ReadVariable(NodeVisitor):
    def __init__(self):
        #record the loop in function
        #self.loop = {}
        #use each pointer variable as key and its update index set inside the loop as value
        self.readvar = set()
        

    def visit_ExprList(self,exprlist):
        if isinstance(exprlist,ExprList):
            #self.livevar[str(exprlist)] = exprlist.nid
            for e in exprlist.exprs:
                self.visit(e)

    #a[...]
    def visit_ArrayRef(self,arrayref):
        if isinstance(arrayref,ArrayRef):
            self.readvar.add(str(arrayref))
            
            #if arrayref.name not in self.readvar:
                #self.readvar[str(arrayref.name)] = set()
                #self.readvar[str(arrayref.name)].add(str(arrayref.subscript))
            #else:
                #self.readvar[str(arrayref.name)].add(str(arrayref.subscript))
            '''
            if isinstance(arrayref.name,ArrayRef):
                if arrayref.name not in self.readvar:
                    self.readvar[str(arrayref.name)] = set()
                    self.readvar[str(arrayref.name)].add(str(arrayref.subscript))
                else:
                    self.readvar[str(arrayref.name)].add(subscript)
            '''


        self.visit(arrayref.name)
            
    
    
    def visit_FuncCall(self,funccall):
        if isinstance(funccall,FuncCall):
            self.visit(funccall.args)
    

    '''
    def visit_For(self,fornode):
        if isinstance(fornode,For):
            
            #add For object to the dict
           
                #print (fornode.nid)
            #get variable in For body,init and cond
            #self.visit(fornode.init)
            self.visit(fornode.cond)
            self.visit(fornode.next)

          
            for node in fornode.stmt.block_items:
                self.visit(node)
            self.loop[fornode] = self.readvar
    '''     
            
    def visit_FuncDecl(self,funcdecl):
        if isinstance(funcdecl,FuncDecl):
            self.visit(funcdecl.args)
    
    
    #visit declare
    def visit_Decl(self,decl):
        if isinstance(decl,Decl):
            self.readvar.add(decl.name)
    
    def visit_PtrDecl(self,ptrdecl):
        if isinstance(ptrdecl,PtrDecl):
            self.readvar.add(ptrdecl.name)

    
    #visit assignment
    def visit_Assignment(self,assignment):
        if isinstance(assignment,Assignment):
            #self.visit(assignment.lvalue)
            self.visit(assignment.rvalue)
            
    
    def visit_Return(self,ret):
        if isinstance(ret, Return):
            self.visit(ret.expr)

    
    
    def visit_BinaryOp(self,binaryop):
        if isinstance(binaryop, BinaryOp):
            self.visit(binaryop.left)
            self.visit(binaryop.right)
            

    def visit_UnaryOp(self,unaryop):
        if isinstance(unaryop,UnaryOp):
            self.visit(unaryop.expr)
           

    
   

    def visit_If(self,ifnode):
        if isinstance(ifnode,If):
            self.visit(ifnode.cond)
            self.visit(ifnode.iftrue)
            self.visit(ifnode.iffalse)

    
    def visit_Block(self,block):
        if isinstance(block,Block):
            for node in block.block_items:
                self.visit(node)
   

    def visit_If(self,ifnode):
        if isinstance(ifnode,If):
            
            self.visit(ifnode.cond)
            self.visit(ifnode.iftrue)
            if ifnode.iffalse is not None:
                self.visit(ifnode.iffalse)
            
    
    def visit_ID(self,idnode):
        if isinstance(idnode,ID):
            self.readvar.add(str(idnode))

class LoopReadVariable(NodeVisitor):
    def __init__(self):
        self.loop = {}


    def visit_For(self,fornode):
        ivv = ReadVariable()
        
        ivv.visit(fornode)
        ivv.visit(fornode.init)
        ivv.visit(fornode.cond)
        ivv.visit(fornode.next)

        try:
            for node in fornode.stmt.block_items:
                self.visit_For(node)
        except:
            pass
        if isinstance(fornode,For):
            self.loop[fornode] = ivv.readvar
            
        
        


          
        #print(self.loop)
        






class FuncReadVariableVisitor(NodeVisitor):
    def __init__(self):
        # The dict associates function names to write sets:
        self.ReadVariable = {}

    def visit_FuncDef(self, funcdef):
        # Create a WriteSet visitor for the body of the function
        liv = LoopReadVariable()
        # Execute it on the function's body
        liv.visit(funcdef.body)

        
        
        # Now it contains the writeset of the function
        self.ReadVariable[funcdef] = liv.loop

        #print("BOY\n")
        #print(liv.loop)
        #for loop in lvv.loop:
            #print(loop.nid)


    






if __name__ == "__main__":
    '''
    sys.path.extend(['.', '..'])
    
    if len(sys.argv) != 2:
        print ("Usage: checkin2 <input_file>")
        sys.exit(0)
    

    file = sys.argv[1]
    '''
    file = "./p1_input8.c"
    #file = "./test.c"
    
    ast = parse_file(file)

    # convert to minic ast
    m_ast = transform(ast)
    

    fiv = FuncReadVariableVisitor()
    fiv.visit(m_ast)
    print(fiv.ReadVariable)

'''
# # Now print the write sets for each function:
    
    for fname in fiv.ReadVariable:
#     
        print ("\nIn function %s\n" % (fname))
        for loop in fiv.ReadVariable[fname]:
            print ("After Loop at line %s\nIndex Variable:" %(loop.coord.line))
            print(fiv.ReadVariable[fname][loop])
'''