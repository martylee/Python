from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
from check_ins.check_in1 import *
from check_ins.check_in2 import *
from check_ins.check_in3b4a import *
from check_ins.check_in3 import *
from LoopAnalyser import *
import sys
import copy

if __name__ == "__main__":
    
    '''
    sys.path.extend(['.', '..'])

    if len(sys.argv) != 2:
        print ("Usage: project1 <input_file>")
        sys.exit(0)

    file = sys.argv[1]
    #file = "./project1inputs/while.c"
    '''
    i = 1
    while i <= 8:
        fd = "./project1inputs/p1_input" + str(i) + ".c"
        print("### TESTING ON %s ###" %(fd))
        ast = parse_file(fd)
        # convert to minic ast
        m_ast = transform(ast)

        lic = LoopInfoCollection()
        lic.visit_all(m_ast)
        print(lic)
        i += 1
