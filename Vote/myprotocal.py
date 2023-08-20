import Vote.Beacon as Beacon
import algorithm
# from multiprocessing import Process,Queue
from threading import Thread
from queue import Queue
import parameters
import random
import Vote.structure as structure
import time
import json
import random
USER_NUMBER = parameters.USER_NUMBER
MAX_OUTPUTIP = parameters.MAX_OUTPUTIP
MAX_INPUTIP = parameters.MAX_INPUTIP
R = parameters.EPOCH
CP_K = parameters.CP_K
j = 2
WAIT_TIME = parameters.WAIT_TIME
MAX_SLOT = parameters.MAX_SLOT
def start():
	u_list = algorithm.init()
	tx = Beacon.random_Tx()
	chain = []
	U = u_list[0]
	block_pre = structure.create_gensis_block(tx, U['sk']).put()
	chain.append(block_pre)
	return u_list, chain
def honest_leader(chain, q_output, u, pre_sl):
	tx = Beacon.random_Tx()
	sl = Beacon.slot_num()
	if sl %R != 0:
		u_leader = Beacon.select(sl)['pk']
		block = algorithm.GenBlock(chain[-1], [tx], u['sk'], sl)
	else:
		# structure.dirter(chain[j])
		u_leader = Beacon.select(sl)
		u_changer = Beacon.select(j)
		(block, block_red) = algorithm.EditBlock(chain, j, u_leader['pk'], u_leader['sk'], u_leader['pk'], Beacon.slot_num(), u_changer['sk'])
		# chain[j] = block_red
		# block = block.put()
	# if sl == 6:
	# 	print(chain)
	chain.append(block)
	for q in q_output:
		if not q[0].empty():
			q[0].get()
		q[0].put(block)
	for q in q_output:
		if not q[1].empty():
			q[1].get()
		q[1].put(chain[-CP_K:])
def corrupt_leader(chain_table, q_output, u, pre_sl):
	print("start corrupt leader ")
	tx = Beacon.random_dirt_Tx()
	sl = Beacon.slot_num()
	length = 0
	append_chain = []
	for chain in chain_table:
		if length<len(chain):
			length = len(chain)

	# print( "append_chain"+str(append_chain))
	# if len(append_chain) == 0:
	for chain in chain_table:
		if len(chain) == length:
			append_chain.append(chain)
	if len(append_chain) == 1:
		chain1 = algorithm.distinguish(append_chain[-1], len(chain_table))
		del append_chain[-1]
		chain_table.append(chain1)
		append_chain.append(chain1)
	for chain in chain_table:
		if len(chain) < length:
			append_chain.append(chain)
	print("len(append_chain)"+str(len(append_chain)))
	q_output_table = []
	for i in range(0, len(append_chain)):
		q_output_table.append(q_output[int(i*len(q_output)/len(append_chain)):int((i+1)*len(q_output)/len(append_chain))])
	i = 0
	# if sl == 5:
	# 	# print(append_chain)
	for chain in append_chain:
		q_output = q_output_table[i]
		if sl %R != 0: 
			u_leader = Beacon.select(sl)['pk']
			block = algorithm.GenBlock(chain[-1], [tx], u['sk'], sl)
		else:
			u_leader = Beacon.select(sl)
			u_changer = Beacon.select(j)
			(block, block_red) = algorithm.EditBlock(chain, j, u_leader['pk'], u_leader['sk'], u_leader['pk'], Beacon.slot_num(), u_changer['sk'])
			# block = block.put()
		chain.append(block)
		for q in q_output:
			if not q[0].empty():
				q[0].get()
			q[0].put(block)
		for q in q_output:
			if not q[1].empty():
				q[1].get()
			q[1].put(chain[-CP_K:])
		i += 1


def honest_notleader_novote(chain, q_input, q_output, pre_sl):
	check = 0
	sl = Beacon.slot_num()
	block_new = chain[0]
	sl_leader = Beacon.select(sl)['pk']
	while True:
		if check == 1:
			print('get')
			for q in q_output:
				if not q[0].empty():
					q[0].get()
				q[0].put(block_new)
			for q in q_output:
				if not q[1].empty():
					q[1].get()
				q[1].put(chain[-CP_K:])

			break
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		for q in q_input:
			if check == 1:
				break
			if not q[0].empty() :
				block_new = q[0].get()
				# print(type(block_new))
				ans = algorithm.VerBlock(chain[-1], block_new,sl_leader)
				if ans == 'right':
					chain.append(block_new)
					check = 1
					break
				elif ans == 'fork':
					while True:
						sl = Beacon.slot_num()
						if sl > pre_sl:
							chain_b = 0
							break
						if not q[1].empty():
							chain_b = q[1].get()
							break
						else:
							continue
					if chain_b == 0:
						break
					chain_l = chain[-CP_K:]
					print("length")
					print(len(chain_l))
					print(len(chain_b))
					ans, block_fork = algorithm.Consensus(chain_l, chain_b)
					print("fork:"+str(ans))
					if ans == 0:
						break
					else:
						index = chain.index(block_fork[0])
						del chain[index:]
						index = chain_b.index(block_fork[1])
						chain.extend(chain_b[index:])
						check = 1
						break
def honest_notleader_vote(chain, q_input, q_output, pre_sl):
	# print("hahaha")
	check = 0
	sl = Beacon.slot_num()
	block_new = chain[0]
	sl_leader = Beacon.select(sl)['pk']
	while True:
		if check == 2:
			break
		if check == 1:
			print('get')
			for q in q_output:
				if not q[0].empty():
					q[0].get_nowait()
				q[0].put_nowait(block_new)
			for q in q_output:
				if not q[1].empty():
					q[1].get_nowait()
				q[1].put_nowait(chain[-CP_K:])
			break
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		for q in q_input:
			if check > 0:
				break
			if not q[0].empty() :
				block_new = q[0].get_nowait()
				# print(type(block_new))
				ans = algorithm.VerBlock(chain[-1], block_new,sl_leader)
				# print(ans)
				if ans == 'right':
					chain.append(block_new)
					check = 1
					break
				elif ans == 'fork':
					chain_b = 0
					while True:
						sl = Beacon.slot_num()
						if sl > pre_sl:
							break
						if not q[1].empty():
							chain_b = q[1].get_nowait()
							break
						else:
							continue
					# chain_b = q[1].get_nowait()
					if chain_b == 0:
						check = 2
						break
					chain_l = chain[-CP_K:]
					ans, block_fork = algorithm.VoteCon(chain_l, chain_b)
					if ans == 0:
						break
					else:
						i = 0
						while not structure.equal_block(chain[i], block_fork[0]) :
							i += 1
						del chain[i:]
						i = 0
						while not structure.equal_block(chain_b[i], block_fork[1]) :
							i += 1
						del chain_b[:i]
						chain.extend(chain_b)
						check = 1
						break

	# while True:
	# 	pass

	return chain
def corrupt_notleader_novote(chain_table, q_input, q_output, pre_sl):
	check = 0
	sl = Beacon.slot_num()
	block_new = chain_table[0][0]
	sl_leader = Beacon.select(sl)['pk']
	while True:
		if check == 1:
			print('get')
			for q in q_output:
				if not q[0].empty():
					q[0].get()
				q[0].put(block_new)
			for q in q_output:
				if not q[1].empty():
					q[1].get()
				q[1].put(chain[-CP_K:])

			break
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		for q in q_input:
			if check == 1:
				break
			if not q[0].empty() :
				block_new = q[0].get()
				# print(type(block_new))
				count = structure.Block.get(block_new).count
				chain = chain_table[count]
				print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
				print(algorithm.VerBlock(chain[-1], block_new,sl_leader))
				print(count)
				if algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'right':
					chain.append(block_new)
					check = 1
					break
				elif algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'fork':
					chain_b = 0
					while True:
						print("wait")
						sl = Beacon.slot_num()
						if sl > pre_sl:
							break
						if not q[1].empty():
							chain_b = q[1].get()
							break
						else:
							continue
					if chain_b == 0:
						break
					chain_l = chain[-CP_K:]
					ans, block_fork = algorithm.Consensus(chain_l, chain_b)
					if ans == 0:
						break
					else:
						index = chain.index(block_fork[0])
						del chain[index:]
						index = chain_b.index(block_fork[1])
						chain.extend(chain_b[index:])
						check = 1
						break
def corrupt_notleader_vote(chain_table, q_input, q_output, pre_sl):
	check = 0
	sl = Beacon.slot_num()
	block_new = chain_table[0][0]
	sl_leader = Beacon.select(sl)['pk']
	while True:
		if check == 2:
			break
		if check == 1:
			print('get')
			for q in q_output:
				if not q[0].empty():
					q[0].get()
				q[0].put(block_new)
			for q in q_output:
				if not q[1].empty():
					q[1].get()
				q[1].put(chain[-CP_K:])

			break
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		for q in q_input:
			if check == 1:
				break
			if not q[0].empty() :
				block_new = q[0].get()
				# print(type(block_new))
				count = structure.Block.get(block_new).count
				chain = chain_table[count]
				if algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'right':
					chain.append(block_new)
					check = 1
					break
				elif algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'fork':
					chain_b = 0
					while True:
						sl = Beacon.slot_num()
						if sl > pre_sl:
							break
						if not q[1].empty():
							chain_b = q[1].get()
							break
						else:
							continue
					if chain_b == 0:
						check == 2
						break
					chain_l = chain[-CP_K:]
					ans, block_fork = algorithm.VoteCon(chain_l, chain_b)
					if ans == 0:
						break
					else:
						index = chain.index(block_fork[0])
						del chain[index:]
						index = chain_b.index(block_fork[1])
						chain.extend(chain_b[index:])
						check = 1
						break

	# while True:
	# 	pass

	return chain_table

def honost(chain_b ,pk_list, u, count, q_input, q_output, max_slot):
	if algorithm.ValidChain(chain_b) != 'right':
		return 0
	chain = []
	chain.extend(chain_b)
	pre_sl = Beacon.slot_num()
	while True:
		if structure.Block.get(chain[-1]).sl >= max_slot:
			break
		sl = Beacon.slot_num()
		# print(sl)
		if sl <= pre_sl:
			time.sleep(WAIT_TIME)
			continue
		else:
			pre_sl = sl
		for q in q_output:
			if not q[0].empty() :
				q[0].get()
			if not q[1].empty():
				q[1].get()
		sl_leader = Beacon.select(sl)['pk']
		print("count:"+str(count))
		# print("the honest chain table as"+str(chain))
		print(structure.Block.get(chain[-1]).sl)
		# print(sl_leader)
		if sl_leader ==  u['pk']:
			honest_leader(chain, q_output, u, pre_sl)
		else:
			if sl % R > CP_K:
				honest_notleader_novote(chain, q_input, q_output, pre_sl)
			else:
				honest_notleader_vote(chain, q_input, q_output, pre_sl)
	print("The thread %d has finished", count)
	i = 0
	print("(-------------------------------------------------)")
	for block in chain:
		print(str(i)+str(":")+str(structure.Block.get(block).sl))
		i += 1
	print("(-------------------------------------------------)")

def corrupt(chain_b ,pk_list, u, count, q_input, q_output, max_slot):

	if algorithm.ValidChain(chain_b) != 'right':
		return 0
	chain_table = []
	chain_table.append(chain_b.copy())
	pre_sl = Beacon.slot_num()
	check = 0
	while True:
		for chain in chain_table:
			if structure.Block.get(chain[-1]).sl >= max_slot+10:
				check = 1
				break
		if check == 1:
			break
		sl = Beacon.slot_num()
		# print(sl)

		if sl <= pre_sl:
			time.sleep(WAIT_TIME)
			continue
		else:
			pre_sl = sl
		# if sl == 8:
		# 	for chain in chain_table:
		# 		print()
		for q in q_output:
			if not q[0].empty() :
				q[0].get()
			if not q[1].empty():
				q[1].get()
		sl_leader = Beacon.select(sl)['pk']
		print("count:"+str(count))
		# print("the honest chain table as"+str(chain))
		print(structure.Block.get(chain[-1]).sl)
		# print(sl_leader)
		if sl_leader ==  u['pk']:
			corrupt_leader(chain_table, q_output, u, pre_sl)
		else:
			if sl % R > CP_K:
				corrupt_notleader_novote(chain_table, q_input, q_output, pre_sl)
			else:
				corrupt_notleader_vote(chain_table, q_input, q_output, pre_sl)
			
	for block in chain:
		print(json.loads(block))
	with open("block_chain_table", "w") as f:
		f.write(json.dumps(chain_table))



def connect(u_list, corrupt_u):
	i = 0
	q_list = []
	while i<USER_NUMBER:
		count = 0
		rand_list = []
		while len(rand_list)<MAX_OUTPUTIP:
			a = random.randint(0, USER_NUMBER-1)
			if a in rand_list or a == i:
				continue
			else:
				rand_list.append(a)
		for a in rand_list:
			q_list.append({'sender':i, 'receiver':a, 'queue':[Queue(1),Queue(1)]})
		q_list.append({'sender':i, 'receiver':corrupt_u, 'queue':[Queue(1),Queue(1)]})
		q_list.append({'sender':corrupt_u, 'receiver':i, 'queue':[Queue(1),Queue(1)]})
		i += 1

	return q_list

				




def main():
	u_list, chain = start()
	corrupt_u = Beacon.corrupt
	pk_list = [u['pk'] for u in u_list]
	q_list = connect(u_list, corrupt_u)
	thread_list = []
	i = 0
	max_slot = MAX_SLOT
	while i < USER_NUMBER:
		q_input = []
		q_output = []
		for q in q_list:
			if q['sender'] == i:
				q_output.append(q['queue'])
			if q['receiver'] == i:
				q_input.append(q['queue'])
		t = Thread(target = honost, args = (chain.copy(), pk_list, u_list[i], i, q_input, q_output,max_slot), name = i)

		# t = Process(target = honost, args = (chain.copy(), pk_list, u_list[i], i, q_input, q_output,max_slot), name = i)
		thread_list.append(t)
		i += 1
	q_input = []
	q_output = []
	for q in q_list:
		if q['sender'] == corrupt_u:
			q_output.append(q['queue'])
		if q['receiver'] == corrupt_u:
			q_input.append(q['queue'])
	t = Thread(target = corrupt, args = (chain.copy(), pk_list, corrupt_u, i, q_input, q_output,max_slot), name = corrupt)
	t.start()
	for t in thread_list:
		t.start()
	t.join()





if __name__ == '__main__':
	main()







