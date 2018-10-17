from __future__ import print_function
from pycparser import parse_file
from minic.c_ast_to_minic import *
from minic.minic_ast import *
from minic.mutils import *
import copy
import sys


class WriteSetVisitor(NodeVisitor):
	def __init__(self):
		self.collection = {}
		self.nestloop = {}
		self.loop_conditions = {}


	def handle_If(self, ifnode, sets):
		if ifnode.iftrue is not None and isinstance(ifnode.iftrue,Block):
			for node in ifnode.iftrue.block_items:
				try:

					if isinstance(node,Assignment):
						sets.add(str(node.lvalue))
					return self.handle_If(node)
				except:
					pass
		

		if ifnode.iffalse is not None and isinstance(ifnode.iftrue,Block):
			for node in ifnode.iffalse.block_items:
				try:

					if isinstance(node,Assignment):
						sets.add(str(node.lvalue))
					return self.handle_If(node)
				except:
					pass








	def visit_For(self, fornode):
                # store index, guard condition and update operation of the loop
                if fornode not in self.collection.keys():
                        self.loop_conditions[fornode] = []
                        self.loop_conditions[fornode].append(fornode.init)
                        self.loop_conditions[fornode].append(fornode.cond)
                        self.loop_conditions[fornode].append(fornode.next)   
                else:
                    pass

		if fornode.init is not None and isinstance(fornode.init, Assignment):
			if fornode in self.collection.keys():
				self.collection[fornode].add(fornode.init.lvalue.name)
			else:
				self.collection[fornode] = set()
				self.collection[fornode].add(fornode.init.lvalue.name)
		if fornode.next is not None and isinstance(fornode.next, Assignment):
			if fornode in self.collection.keys():
				self.collection[fornode].add(fornode.next.lvalue.name)
			else:
				self.collection[fornode] = set()
				self.collection[fornode].add(fornode.next.lvalue.name)
		if fornode.stmt is not None and isinstance(fornode.stmt, Block):

			
			for node in fornode.stmt.block_items:
				#node.show()


				try:
					if isinstance(node,For):
						if fornode in self.nestloop.keys():
							self.nestloop.add(node)
						else:
							self.nestloop[fornode] = set()
							self.nestloop[fornode].add(node)
					if isinstance(node,If):
						self.handle_If(node,self.collection[fornode])
					if isinstance(node,Assignment):
						if fornode in self.collection.keys():
							self.collection[fornode].add(str(node.lvalue))
						else:
							self.collection[fornode] = set()
							self.collection[fornode].add(str(node.lvalue))
					return self.visit_For(node)

				except:
					pass
				#if node is not None and isinstance(node, Assignment):
					#self.writeset.add(node.lvalue.name)




class FuncWriteSetVisitor(NodeVisitor):
	def __init__(self):
		# The dict associates function names to write sets:
		self.writesets = {}
		self.loop_conds = {}

	def visit_FuncDef(self, funcdef):
		# Create a WriteSet visitor for the body of the function
		wsv = WriteSetVisitor()
		# Execute it on the function's body
		wsv.visit(funcdef.body)
		

		for key in wsv.collection:
			if key in wsv.nestloop:
				for loop in wsv.nestloop[key]:
					wsv.collection[key] = wsv.collection[key].union(wsv.collection[loop])
					#wsv.collection[loop]
		# Now it contains the writeset of the function
		self.writesets[funcdef] = wsv.collection
		self.loop_conds[funcdef] = wsv.loop_conditions   


if __name__ == "__main__":
	ast = minic_parse_file('./p1_input5.c')
	fws = FuncWriteSetVisitor()
	fws.visit(ast)
	#print(fws.writesets)
	for fname in fws.writesets:
		print("Function: %s" % (fname))
		for loop in fws.writesets[fname]:
			print("     Loop at line %s" % (loop.coord.line))
			for write in fws.writesets[fname][loop]:
				print("         Written Set:" + write)
				#print(fws.writesets[fname])
				pass

