
import Vote.parameters as parameters
import Vote.structure as structure
import json
import matplotlib.pyplot as plt

CENTER = 100
NODESIZE = 100
# import numpy as np
USER_NUMBER = parameters.USER_NUMBER
MAX_OUTPUTIP = parameters.MAX_OUTPUTIP
MAX_INPUTIP = parameters.MAX_INPUTIP
R = parameters.EPOCH
CP_K = parameters.CP_K
MAX_SLOT = parameters.MAX_SLOT
class Tree(object):
	"""docstring for tree"""
	def __init__(self, block):
		super(Tree, self).__init__()
		self.block = block
		self.sl = structure.Block.get(block).sl

   
	def child_append(self, child):
		real_child = []
		used_block = []
		pre_block = structure.Block.get(self.block)
		pre_head = structure.Block_head.get(pre_block.head)
		old_list = [pre_head.old_state, pre_head.new_state, pre_head.d,pre_head.sigma_d, 
			pre_head.t, pre_head.sigma_t, pre_block.body]
		st = self.old_state = structure.get_hash256(old_list)
		for block in child:
			block = structure.Block.get(block)
			head = structure.Block_head.get(block.head)
			if head.old_state == st:
				# print("sl:"+str(self.sl)+str(block.sl))
				real_child.append(Tree(block.put()))
				used_block.append(block.put())
		self.child = real_child
		# print(len(real_child))
		return used_block
	def main_chain(self):
		if len(self.child) == 0:
			return []
		elif len(self.child) == 1:
			return self.child+self.child[0].main_chain()
		else:
			tem_list = []
			for node in self.child:
				this_chain = [node]+node.main_chain()
				if len(this_chain) > len(tem_list):
					tem_list = this_chain
			return  tem_list
	def paint(self):
		plt.figure(figsize=(10, 10), dpi=70)  # 设置图像大小
		center = 0
		# plt.scatter(0, center, s = 100)
		self.__paint(plt, center, 0)
		plt.show()
	def __paint(self, plt, parent, count):
		hight = parent+count
		index = 0
		plt.scatter(self.sl, hight, s = 100)
		for node in self.child:
			node.__paint(plt, hight, index)
			plt.plot([self.sl, node.sl], [hight, hight+index])
			index += node.length()+1
		# print(self.block)
	def length(self, mylength = 0):
		mylength += len(self.child)-1
		if len(self.child) == 0:
			return 0
		# mylength -= 1
		for node in self.child:
			mylength += node.length()
		return mylength

def getblockrow(chain_table):
	block_row = []
	for chain in chain_table:
		if len(chain) == 0:
			del chain
			continue
		block = chain[0]
		block = structure.Block.get(block)
		block_row.append(chain[0])
	i = 0
	while i<len(block_row):
		j = i+1
		while j<len(block_row):
			if structure.equal_block(block_row[i], block_row[j]):
				del block_row[j]
				j -= 1
			j += 1
		i += 1




	return block_row
def clear_chain(chain_table, used_block):
	for block_del in used_block:
		for chain in chain_table:
			if len(chain) == 0:
				del chain
				continue
			block = chain[0]
			# block = structure.Block.get(block)
			if structure.equal_block(block, block_del):
				del chain[0]

def create_tree(chain_table, tree, count = 0):
	block_row = getblockrow(chain_table)
	used_block = tree.child_append(block_row)
	clear_chain(chain_table, used_block)
	count += 1

	for node in tree.child:
		create_tree(chain_table, node, count)


def main():
	with open("block_chain_table", "r") as f:
		chain_table = f.read()
	chain_table = json.loads(chain_table)
	for chain in chain_table:
		for block in chain:
			block  = structure.Block.get(block)
			print("sl:"+str(block.sl))
	tree = Tree(chain_table[0][0])
	for chain in chain_table:
		del chain[0]
	create_tree(chain_table, tree)
	print(chain_table)
	tree.paint()


if __name__ == '__main__':
	main()