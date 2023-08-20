import Vote.Beacon as Beacon
import algorithm
import threading
import parameters
import random
import Vote.structure as structure
import time
from queue import Queue
USER_NUMBER = parameters.USER_NUMBER
MAX_OUTPUTIP = parameters.MAX_OUTPUTIP
MAX_INPUTIP = parameters.MAX_INPUTIP
R = parameters.EPOCH
CP_K = parameters.CP_K
j = 2
WAIT_TIME = parameters.WAIT_TIME

def start():
	u_list = algorithm.init()
	tx = Beacon.random_Tx()
	chain = []
	U = u_list[0]
	block_pre = structure.create_gensis_block(tx, U['sk']).put()
	chain.append(block_pre)
	return u_list, chain
def honest_leader(chain, q_input, q_output, u, pre_sl):
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
		block = block.put()
	chain.append(block)
	for q in q_output:
		if not q.empty():
			q.get()
		q.put(block)
	while True:
		# print("haha")
		time.sleep(0.1)
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		# for q in q_output:
		# 	if q.empty():
		# 		q.put(chain[-CP_K:])
				# k = q.get()
				# print(k)
				# if k == CP_K:
				# 	q.put(chain[-CP_K:])
				# else :
				# 	q.put(k)
def honest_notleader(chain, q_input, q_output, pre_sl):
	check = 0
	sl = Beacon.slot_num()
	block_new = chain[0]
	sl_leader = Beacon.select(sl)['pk']
	while True:
		# print(sl_leader)
		if check == 1:
			for q in q_output:
				if not q.empty():
					q.get()
				q.put(block_new)
			break
		sl = Beacon.slot_num()
		if sl > pre_sl:
			break
		for q in q_input:
			if not q.empty() :
				block_new = q.get()
				print(type(block_new))
				if algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'right':
					chain.append(block_new)
					check = 1
					break
				# elif algorithm.VerBlock(chain[-1], block_new,sl_leader) == 'fork':
				# 	# if not q.empty():
				# 	# 	q.get()
				# 	# q.put(CP_K)
				# 	while True:
				# 		sl = Beacon.slot_num()
				# 		if sl > pre_sl:
				# 			break
				# 		if not q.empty():
				# 			chain_b = q.get()
				# 			# if chain_b == CP_K:
				# 			# 	q.put(CP_K)
				# 			# 	continue
				# 		else:
				# 			continue
				# 	chain_l = chain[-CP_K:]
				# 	ans, block_fork = algorithm.Consensus(chain_l, chain_b)
				# 	if ans == 0:
				# 		break
				# 	else:
				# 		index = chain.index(block_fork)
				# 		del chain[index:]
				# 		index = chain_b.index(block_fork)
				# 		chain.extend(chain_b[index:])

	# while True:
	# 	pass

	return chain

def honost(chain_b ,pk_list, u, count, q_input, q_output, max_slot):
	if algorithm.ValidChain(chain_b) != 'right':
		return 0
	chain = []
	chain.extend(chain_b)



	pre_sl = Beacon.slot_num()
	while True:
		print("count:"+str(count))
		print(structure.Block.get(chain[-1]).sl)
		if structure.Block.get(chain[-1]).sl >= max_slot:
			break
		sl = Beacon.slot_num()
		# print(sl)
		if sl <= pre_sl:
			time.sleep(WAIT_TIME)
			continue
		else:
			pre_sl = sl
		sl_leader = Beacon.select(sl)['pk']
		if sl_leader ==  u['pk']:
			honest_leader(chain, q_input, q_output, u, pre_sl)
		else:
			honest_notleader(chain, q_input, q_output, pre_sl)
			
	print(chain)





def connect(u_list):
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
			q_list.append({'sender':i, 'receiver':a, 'queue':Queue(1)})
		i += 1
	return q_list

				




def main():
	u_list, chain = start()
	pk_list = [u['pk'] for u in u_list]
	q_list = connect(u_list)
	thread_list = []
	i = 0
	max_slot = 20
	while i < USER_NUMBER:
		q_input = []
		q_output = []
		for q in q_list:
			if q['sender'] == i:
				q_output.append(q['queue'])
			if q['receiver'] == i:
				q_input.append(q['queue'])
		t = threading.Thread(target = honost, args = (chain.copy(), pk_list, u_list[i], i, q_input, q_output,max_slot), name = i)
		thread_list.append(t)
		i += 1
	for t in thread_list:
		t.start()
	t.join()





if __name__ == '__main__':
	main()







