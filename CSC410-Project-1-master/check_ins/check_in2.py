from __future__ import print_function
from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
from check_in1 import*
import copy
import sys

class ReachingDefs(NodeVisitor):
	def __init__(self):

		# maps for variable name to collection of reaching defs and its position
		self.defs = {}

		#{[key:decl or lvalue] : [[nid, statement],...]}
		
		#self.lws = FuncWriteSetVisitor()

		#self.loopinfo = set()


	def visit_ExprList(self,exprlist):
		if isinstance(exprlist,ExprList):
			#self.livevar[str(exprlist)] = exprlist.nid
			for e in exprlist.exprs:
				self.visit(e)

	#a[...]
	def visit_ArrayRef(self,arrayref):
		if isinstance(arrayref,ArrayRef):
			self.visit(arrayref.name)
			self.visit(arrayref.subscript)
	
	
	def visit_FuncCall(self,funccall):
		if isinstance(funccall,FuncCall):
			self.visit(funccall.args)
	

	def visit_For(self,fornode):
		if isinstance(fornode,For):
			
			#add For object to the dict
			#if fornode not in self.loop:
				#self.loop[fornode] = set()
				#print (fornode.nid)
			#get variable in For body,init and cond
			self.visit(fornode.init)
			self.visit(fornode.cond)
			self.visit(fornode.next)

		  
			for node in fornode.stmt.block_items:
				self.visit(node)
			
	def visit_FuncDecl(self,funcdecl):
		if isinstance(funcdecl,FuncDecl):
			self.defs[funcdecl.args.name] = [[funcdecl.coord.line,str(funcdecl.type) + " " + funcdecl.args.name]]
	
	#visit declare
	def visit_Decl(self,decl):
		if isinstance(decl,Decl):
			#self.livevar[decl.name] = decl.nid
			
			self.defs[decl.name] = [[decl.coord.line,str(decl)]]
			 
	


	def visit_PtrDecl(self,ptrdecl):
		if isinstance(ptrdecl,PtrDecl):
			self.defs[ptrdecl.type] = [[ptrdecl.coord.line,str(ptrdecl)]]


	#visit assignment
	def visit_Assignment(self,assignment):
		if isinstance(assignment,Assignment):

			if assignment.lvalue.name in self.defs and assignment.coord is not None:
				self.defs[assignment.lvalue.name].append([assignment.coord.line,str(assignment)])
			elif assignment.coord is not None:
				self.defs[assignment.lvalue.name]=[[assignment.coord.line,str(assignment)]]
			#self.visit(assignment.lvalue)
			#self.visit(assignment.rvalue)
			
	
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
			
	
	'''
	def visit_ID(self,idnode):
		if isinstance(idnode,ID):
			if idnode.name not in self.livevar:
				self.livevar[idnode.name] = idnode.nid
			else:
				self.livevar[idnode.name] = max(idnode.nid,self.livevar[idnode.name])
	'''
	
	def visit_block(self,block):
		if isinstance(block,Block) and block is not None:
			for node in block.block_items:
				self.visit(node)


		
   

class FuncReachingDefsVisitor(NodeVisitor):
	def __init__(self):
		self.ReachingDef = {}
		#self.loopreachingdef = {}
		
		self.lrs = FuncWriteSetVisitor()
	


	def find_last_stmt(self,line,stlist):
		last = 0
		stmt = ''
		for i in stlist:
			if line > i[0] > last:
				last = i[0]
				stmt = i[1]
		return stmt


	def visit_FuncDef(self, funcdef):
		rd = ReachingDefs()
		self.lrs.visit(funcdef)
		rd.visit(funcdef)
		

		
		#print(wsv.defs)
		#print(wsv.loop_vars)
		#print(wsv.loops)
		
		self.ReachingDef[funcdef] = {}

		#print(self.ReachingDef)
		#print (self.lrs.writesets)


		#add reachingdef for each loop
		for fname in self.lrs.writesets:
			for loop in self.lrs.writesets[fname]:
				self.ReachingDef[funcdef][loop] = []

				loopline = loop.coord.line
				for wvariable in self.lrs.writesets[fname][loop]:
					
					#c[j]
					if '[' in wvariable:
						i = 0
						while wvariable[i] != '[':
							i = i + 1
						wvariable = wvariable[:i]

					
					try:
						stlist = rd.defs[wvariable]
						stmt = self.find_last_stmt(loop.coord.line,stlist)
						self.ReachingDef[funcdef][loop].append(stmt)
					except:
						pass
					
					



		#print(self.ReachingDef)

	'''
	def get_writesets(self,funcdef):
		self.lrs.visit(funcdef)
		print (self.lrs)
	'''
	   







###########################################






class LiveVariable(NodeVisitor):
	def __init__(self):
		#record the loop in function
		self.loop = {}
		#use each variable as key and its last statement nid as value
		self.livevar = {}
		

	def visit_ExprList(self,exprlist):
		if isinstance(exprlist,ExprList):
			#self.livevar[str(exprlist)] = exprlist.nid
			for e in exprlist.exprs:
				self.visit(e)

	#a[...]
	def visit_ArrayRef(self,arrayref):
		if isinstance(arrayref,ArrayRef):
			self.visit(arrayref.name)
			self.visit(arrayref.subscript)
	
	
	def visit_FuncCall(self,funccall):
		if isinstance(funccall,FuncCall):
			self.visit(funccall.args)
	

	def visit_For(self,fornode):
		if isinstance(fornode,For):
			
			#add For object to the dict
			if fornode not in self.loop:
				self.loop[fornode] = set()
				#print (fornode.nid)
			#get variable in For body,init and cond
			self.visit(fornode.init)
			self.visit(fornode.cond)
			self.visit(fornode.next)

		  
			for node in fornode.stmt.block_items:
				self.visit(node)
			
			
	def visit_FuncDecl(self,funcdecl):
		if isinstance(funcdecl,FuncDecl):
			self.visit(funcdecl.args)
	
	#visit declare
	def visit_Decl(self,decl):
		if isinstance(decl,Decl):
			self.livevar[decl.name] = decl.nid

	def visit_PtrDecl(self,ptrdecl):
		if isinstance(ptrdecl,PtrDecl):
			self.livevar[str(ptrdecl)] = decl.nid


	#visit assignment
	def visit_Assignment(self,assignment):
		if isinstance(assignment,Assignment):
			self.visit(assignment.lvalue)
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
			if idnode.name not in self.livevar:
				self.livevar[idnode.name] = idnode.nid
			else:
				self.livevar[idnode.name] = max(idnode.nid,self.livevar[idnode.name])
	
	def visit_block(self,block):
		if isinstance(block,Block) and block is not None:
			for node in block.block_items:
				self.visit(node)


class FuncLiveVariableVisitor(NodeVisitor):
	def __init__(self):
		# The dict associates function names to write sets:
		self.LiveVariable = {}

	def visit_FuncDef(self, funcdef):
		# Create a WriteSet visitor for the body of the function
		lvv = LiveVariable()
		# Execute it on the function's body
		lvv.visit(funcdef.body)

		for fornode in  lvv.loop.keys():
			nid = fornode.nid
			for var in lvv.livevar:
				if lvv.livevar[var] > nid:
					lvv.loop[fornode].add(var)
		
		# Now it contains the writeset of the function
		self.LiveVariable[funcdef] = lvv.loop

		#print("BOY\n")
		#print(lvv.livevar)
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
	file = "./p1_input6.c"
	#file = "./test.c"
	
	ast = parse_file(file)

	# convert to minic ast
	m_ast = transform(ast)
	

	flv = FuncReachingDefsVisitor()
	flv.visit(m_ast)
	print (flv.ReachingDef)

'''
# # Now print the write sets for each function:
	for fname in flv.LiveVariable:
#     # Print 'function string' writes in 'set representation'
		print ("\nIn function %s\n" % (fname))
		for loop in flv.LiveVariable[fname]:
			print ("After Loop at line %s\nLive Variable:" %(loop.coord.line))
			print(flv.LiveVariable[fname][loop])
		
'''   
	
			


	
