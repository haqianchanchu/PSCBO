import Beacon
import structure
import parameters
import random
import time
R = parameters.EPOCH
epislon = parameters.EPISLON
def init():
	u_list = Beacon.init_U(epislon)
	return u_list
def GenBlock(pre_block, Tx, sk, sl):
	block_new = structure.Block()
	# print(pre_block)
	block_new.create(pre_block, Tx, sk, sl)
	return block_new.put()
def VerBlock(pre_block, block, pk):
	return structure.verify_block(pre_block, block, pk)
def Consensus(chain1,chain2):
	block1 = chain1[-1]
	block2 = chain2[-1]
	block1 = structure.Block.get(block1)
	block2 = structure.Block.get(block2)

	if block1.depth >= block2.depth:
		print("fork error 1")
		return (0,block1.put())
	for block_b in chain2:
		for block_l in chain1:
			if structure.equal_block(block_b, block_l):
				return(1,(block_l, block_b))
	print("fork error 1")
	return (0,block1.put()) 
def EditBlock(chain1, j, pk, sk, receiver, sl, sk_j):
	for block in chain1:
		block = structure.Block.get(block)
		if block.sl == j:
			break
	if block.put() == chain1[-1]:
		return (GenBlock(chain1[-1], [Beacon.random_Tx()], sk, sl), 0)
	block = block.put()
	block = structure.cleaner(block, sk_j)
	tx = structure.Tx(pk, receiver, 0, structure.get_hash256(block))
	tx.sign(sk)
	tx2 = structure.Tx(pk, receiver, 0, str(j))
	tx2.sign(sk)
	block_new = structure.Block()
	block_new.create(chain1[-1], [tx, tx2], sk, sl=sl)
	return (block_new.put(), block)
def EditBlockCorrupt(chain1, j, pk, sk, receiver, sl, sk_j):
	for block in chain1:
		block = structure.Block.get(block)
		if block.sl == j:
			break
	if block.put() == chain1[-1]:
		return (GenBlock(chain1[-1], [Beacon.random_Tx()], sk, sl), 0)
	block = block.put()
	block = structure.cleaner(block, sk_j)
	tx = structure.Tx(pk, receiver, 0, "")
	tx.sign(sk)
	tx2 = structure.Tx(pk, receiver, 0, str(j))
	tx2.sign(sk)
	block_new = structure.Block()
	block_new.create(chain1[-1], [tx, tx2], sk, sl=sl)
	return (block_new.put(), block)
def check_vote(block):
	block = structure.Block.get(block)
	tx = block.body[0]
	tx = structure.Tx.get(tx)
	if tx.data == "":
		return 0
	else:
		return 1
def VoteCon(chain1,chain2):
	block1 = chain1[-1]
	block2 = chain2[-1]
	print(block2)
	block1 = structure.Block.get(block1)
	block2 = structure.Block.get(block2)
	print(block2)
	print("depth:"+str(block1.depth)+str(block2.depth))
	if block1.depth >= block2.depth:
		print("fork error 1")
		return (0,block1.put())
	check = 0
	for block_b in chain2:
		if check == 1:
			break
		for block_l in chain1:
			if structure.equal_block(block_b, block_l):
				check = 1
				break
	if check == 0:
		print("fork error 2")
		return (0,0) 
	i = 0
	data = ''
	while i<len(chain1):
		block = structure.Block.get(chain1[i])
		if block.sl%R == 0:
			data = block.body
		i += 1
	while i<len(chain2):
		block = structure.Block.get(chain2[i])
		if block.sl%R == 0 and block.body != data:
			print("fork error 3")
			return (0,0) 
		i += 1
	return(1,(block_l, block_b))
def ValidChain(C):
	E = []
	pre_block = C[0]
	pre_block = structure.Block.get(pre_block)
	for block in C[1:]:
		# print(E)
		block = structure.Block.get(block)
		if block.sl %R != 0:
			pk = Beacon.select(block.sl)['pk']
			ans = VerBlock(pre_block, block, pk)
			# print(block.sl)
			# print(ans)
			if ans == 'error' or ans == 'fork':
				return 'error'
			elif ans == 'redact':
				E.append(pre_block)
				pre_block = block
			elif ans == 'right':
				pre_block = block
				continue
			else:
				raise(Exception("algorithm ValidChain error"))
		else :
			pk = Beacon.select(block.sl)['pk']
			ans = VerBlock(pre_block, block, pk)
			if ans != 'right':
				return 'error'
			pre_block = block
			tx = block.body
			tx1 = structure.Tx.get(tx[0])
			tx2 = structure.Tx.get(tx[1])
			data = tx1.data
			j = int(tx2.data)
			for block_d in E:
				if block_d.sl == j and data == structure.get_hash256(block_d.put()):
					E.remove(block_d)
	if len(E) == 0:
		return 'right'
	else:
		return 'error'


	return 'right'
def viable(chain_table, pk):
	pass
def distinguish(chain, count):
	chain1 = [block for block in chain]
	del chain1[-1]
	i = 0
	for i in range(len(chain1)):
		block = chain1[i]
		block = structure.Block.get(block)
		block.count = count
		block = block
		chain1[i] = block.put()
	return chain1



def main():
	j = 2
	u_list = init()
	# print(u_list[0])
	pk_list = [u['pk'] for u in u_list]
	tx = Beacon.random_Tx()
	chain = []
	U = u_list[0]
	block_pre = structure.create_gensis_block(tx, U['sk']).put()
	chain.append(block_pre)
	i = 0
	pre_sl = Beacon.slot_num()
	while True:
		tx = Beacon.random_Tx()
		sl = Beacon.slot_num()
		# print(sl)
		if sl <= pre_sl:
			time.sleep(0.5)
			continue
		else:
			pre_sl = sl
		if sl %R != 0:
			u_leader = Beacon.select(sl)
			block = GenBlock(chain[-1], [tx], u_leader['sk'], sl)
		else:
			# structure.dirter(chain[j])
			u_leader = Beacon.select(sl)
			u_changer = Beacon.select(j)
			(block, block_red) = EditBlock(chain, j, u_leader['pk'], u_leader['sk'], u_leader['pk'], Beacon.slot_num(), u_changer['sk'])
			chain[j] = block_red
			block = block.put()
		chain.append(block)
		i += 1
		if sl > 5:
			break

	# chain.append(block_new)
	# ValidChain(chain)
	print(ValidChain(chain))



if __name__ == '__main__':
	main()

