from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
from check_ins.check_in1 import *
from check_ins.check_in2 import *
from check_ins.check_in3 import *
from check_ins.check_in3b4a import *
import sys
import copy




class LoopInfoCollection(NodeVisitor):
    def __init__(self):
        self.wsv = FuncWriteSetVisitor()
        self.rdv = FuncReachingDefsVisitor()
        self.fiv = FuncIndexSetVisitor()
        self.flv = FuncLiveVariableVisitor()
        self.frv = FuncReadVariableVisitor()
        
    def visit_all(self, ast):
        self.wsv.visit(ast)
        self.rdv.visit(ast)
        self.fiv.visit(ast)
        self.flv.visit(ast)
        self.frv.visit(ast)

    def __str__(self):
        string = ""
        for fname in self.wsv.writesets:
            
            string += "Function: %s\n" % (fname.decl.name)
            for loop in self.wsv.writesets[fname]:
                string += "     Loop at line %s\n" % (loop.coord.line)
            
                # Written Set
                #if self.wsv.loop_conds[fname][loop] != {}:
                string += "         Index: " + str(self.wsv.loop_conds[fname][loop][0]) + '\n'
                string += "         Loop Guard: " + str(self.wsv.loop_conds[fname][loop][1]) + '\n'
                string += "         Update Operation: " + str(self.wsv.loop_conds[fname][loop][2]) + '\n'
                    
                if self.wsv.loop_conds[fname][loop] != set():
                    string += "         Written Set Variables:\n"
                    string += "            "
                    for write in self.wsv.writesets[fname][loop]:
                        string += write + ", "
                    string += "\n"
##                else:
##                    string += "         Written Set Variables:\n"
##                    string += "            None\n"
                
                #Read Set
                if loop in self.frv.ReadVariable[fname].keys():
                    string += "         Read Variables:\n"
                    string  += "           "
                    for read in self.frv.ReadVariable[fname][loop]:
                        string += read + ", "
                    string += "\n"



                

                

                # Reaching Definitions 
                if self.rdv.ReachingDef[fname][loop] != {}:
                    string += "         Reaching Definitions:\n"
                    for var in self.rdv.ReachingDef[fname][loop]:
                        #for rdef in self.rdv.ReachingDef[fname][loop][var]:
                        string += "            " + var + "\n"
##                else:
##                    string += "         Reaching Definitions:\n"
##                    string += "            None\n"

                
               # Live Variable after loop
                if loop in self.flv.LiveVariable[fname].keys():
                    if self.flv.LiveVariable[fname][loop] != set():
                        string += "         Live Variables after Loop:\n"
                        for var in self.flv.LiveVariable[fname][loop]:
                                string += "            " + var + "\n"
##                else:
##                    string += "         Reaching Definitions:\n"
##                    string += "            None\n"

                # Index Set
                if loop in self.fiv.indexsets[fname].keys():
                    string += "         Index Set:\n"
                    if self.fiv.indexsets[fname][loop] != set():
                        string += "            "
                        for write in self.fiv.indexsets[fname][loop]:
                                 string += write + ", "
                        string += "\n"
                        
                # Update Statements
                if loop in self.fiv.updatesets[fname].keys():
                    string += "         Update Set:\n"
                    if self.fiv.updatesets[fname][loop] != {}:
                        string += "            "
                        for write in self.fiv.updatesets[fname][loop]:
                                 string += write + ", "
                        string += "\n"


                # Index Vectors
                if loop in self.fiv.indexvectors[fname].keys():
                    string += "         Index Vectors:\n"
                    if self.fiv.indexvectors[fname][loop] != []:
                        string += "            "
                        for write in self.fiv.indexvectors[fname][loop]:
                                 string += write + ", "
                        string += "\n"
##                    else:
##                        string += "         Index Vectors:\n"
##                        string += "            None\n"
                
            #string += " Index Set for function %s :\n   " % (fname.decl.name) + str(self.fiv.indexsets[fname]) + '\n'
            #string += " Update Set %s:\n   " % (fname.decl.name) + str(self.fiv.updatesets[fname]) + '\n'
        return string
        
        
        

if __name__ == "__main__":
    '''
    sys.path.extend(['.', '..'])
    if len(sys.argv) != 2:
        print ("Usage: project1 <input_file>")
        sys.exit(0)
    file = sys.argv[1]
    #file = "./project1inputs/while.c"
    '''
    file = "./project1inputs/p1_input8.c"
    ast = parse_file(file)
    # convert to minic ast
    m_ast = transform(ast)

    lic = LoopInfoCollection()
    lic.visit_all(m_ast)
    print(lic)

    fiv = FuncIndexSetVisitor()
    fiv.visit(m_ast)
##    for fname, indexset in fiv.indexsets.items():
##        print ("%s has index %r" % (fname, indexset))
##    for fname, upstate in fiv.updatesets.items():
##        print ("%s has update statements %r" % (fname, upstate))
##    for function, loop in fiv.indexvectors.items():
##        if len(loop.keys()) == 0:
##            print ("%s does not contain any loops" % function)
##        else:
##            string = ("%s has nested loop with index vectors: (" % function)
##            for loop, indexvectors in loop.items():
##                for vector in indexvectors:
##                    string += vector + ","
##            print string[:-1] + ")"
