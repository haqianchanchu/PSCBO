import Vote.sign as sign
import json
import hashlib
from copy import deepcopy

P = sign.init()

def get_hash256(*data):
		data_st = ""
		for data_i in data:
			data_st += str(data_i)
		hash256 = hashlib.sha256()
		hash256.update(data_st.encode('utf-8'))
		return hash256.hexdigest()
class Tx(object):
	"""docstring for Tx"""
	def __init__(self, sender, receiver, value, data):
		self.sender = sender
		self.receiver = receiver
		self.value = value
		self.data = data
	def sign(self, sk):
		ls = [self.sender,self.receiver,self.value,self.data]
		self.signature = sign.sign(str(ls),sk)
	def put(self):
		ls = {'sender':self.sender,'receiver':self.receiver,'value':self.value,'data':self.data,'signature':self.signature}
		return json.dumps(ls)
	def get(ls):
		ls = json.loads(ls)
		tx = Tx(ls['sender'],ls['receiver'],ls['value'],ls['data'])
		tx.signature = ls['signature']
		return tx

	def verify(tx):
		tx = json.loads(tx)
		m = [tx['sender'],tx['receiver'],tx['value'],tx['data']]
		return sign.verify(tx['signature'], str(m), tx['sender'], P)

class Merktree(object):
	"""docstring for merktree"""
	def __init__(self, Tx):
		self.Tx = Tx
	def create(self):
		Tx = self.Tx
		self.d = self.get_root(Tx)
		self.Tx_nd = self._clear_data(Tx.copy())
		self.t = self.get_root(self.Tx_nd)
	def get_root(self, Tx):
		if type(Tx[0]) == type('123'):
			tem_group = [tx for tx in Tx]
		else:
			tem_group = [tx.put() for tx in Tx]
		if len(tem_group) == 1:
			tem_group.append("")
			tem_group = [get_hash256(tem_group[0],tem_group[1])]
		while len(tem_group) != 1:
			if len(tem_group)%2 == 1:
				tem_group.append("")
			node_list = []
			count = 0
			while count<len(tem_group):
				node_list.append(get_hash256(tem_group[count],tem_group[count+1]))
				count += 2
			tem_group = node_list.copy()
		return tem_group[0]
	def _clear_data(self,Tx):
		Tx_copy = [deepcopy(tx) for tx in Tx]
		Tx_nd = []
		for Tx_i in Tx_copy:
			Tx_i.data = ""
			Tx_nd.append(Tx_i)
		return Tx_nd

class Block(object):
	"""docstring for Block"""
	def __init__(self):
		pass
	def create(self, pre_block, Tx, sk, sl):
		head = Block_head()
		head.create(pre_block, Tx, sk)
		self.head = head.put()
		self.body = [tx.put() for tx in Tx]
		self.sl = sl
		pre_block = Block.get(pre_block)
		self.depth = pre_block.depth+1
		self.count = pre_block.count
	def put(self):
		# print(self.body)
		return json.dumps({'head':self.head,'body':self.body,'sl':self.sl, 'depth':self.depth, 'count':self.count})
	def get(ls):
		ls = json.loads(ls)
		block = Block()
		block.head = ls['head']
		block.body = ls['body']
		block.sl = ls['sl']
		block.depth = ls['depth']
		block.count = ls['count']
		return block
		
class Block_head(object):
	"""docstring for block_head"""
	def __init__(self):
		pass
	def create(self, pre_block, tx, sk):
		pre_block = Block.get(pre_block)
		pre_head = Block_head.get(pre_block.head)
		old_list = [pre_head.old_state, pre_head.new_state, pre_head.d,pre_head.sigma_d, 
			pre_head.t, pre_head.sigma_t, pre_block.body]
		new_list = [pre_head.old_state, pre_head.new_state, pre_head.t,pre_head.sigma_t]
		self.old_state = get_hash256(old_list)
		self.new_state = get_hash256(new_list)
		merktree = Merktree(tx)
		merktree.create()
		self.d = merktree.d
		self.t = merktree.t
		self.sigma_d = sign.sign(merktree.d, sk)
		self.sigma_t = sign.sign(merktree.t, sk)
	def put(self):
		ls = {'old_state':self.old_state, 'new_state':self.new_state, 'd':self.d,
			't':self.t, 'sigma_d':self.sigma_d, 'sigma_t':self.sigma_t}
		return json.dumps(ls)
	def get(ls):
		ls = json.loads(ls)
		block_head = Block_head()
		block_head.old_state = ls['old_state']
		block_head.new_state = ls['new_state']
		block_head.d = ls['d']
		block_head.t = ls['t']
		block_head.sigma_d = ls['sigma_d']
		block_head.sigma_t = ls['sigma_t']
		return block_head
def create_gensis_block(data, sk):
	block = Block()
	block_head = Block_head()
	block_head.old_state = "gensis"
	block_head.new_state = "Gensis"
	merktree = Merktree([data])
	merktree.create()
	block_head.d = merktree.d
	block_head.t = merktree.t
	block_head.sigma_d = sign.sign(merktree.d, sk)
	block_head.sigma_t = sign.sign(merktree.t, sk)
	block.head = block_head.put()
	block.body = [data.put()]
	block.count = 0
	block.sl = 0
	block.depth = 0
	return block
def verify_block(pre_block, block, pk):
	if type(pre_block) == type(''):
		pre_block = Block.get(pre_block)
	if type(block) == type(''):
		block = Block.get(block)
	
	head = Block_head.get(block.head)
	if not sign.verify(head.sigma_t, head.t, pk, P) or not sign.verify(head.sigma_d, head.d, pk, P):
		return 'error'

	merktree = Merktree([Tx.get(tx) for tx in block.body])
	merktree.create()
	d = merktree.d
	t = merktree.t
	if d != head.d or t != head.t:
		return 'error'
	# if block.depth != pre_block.depth+1:
	# 	print("................................................")
	# 	print("depth:"+str(block.depth))
	# 	print("depth:"+str(pre_block.depth))
	# 	return 'error'
	pre_head = Block_head.get(pre_block.head)
	old_list = [pre_head.old_state, pre_head.new_state, pre_head.d,pre_head.sigma_d, 
		pre_head.t, pre_head.sigma_t, pre_block.body]
	new_list = [pre_head.old_state, pre_head.new_state, pre_head.t,pre_head.sigma_t]
	old_state = get_hash256(old_list)
	new_state = get_hash256(new_list)

	if head.new_state != new_state :
		return 'fork'
	if head.old_state != old_state :
		return 'redact'
	# for tx in block.body:
	# 	ans = Tx.verify(tx)
	# 	if not ans:
	# 		print("haha")
	# 		return 'error'
	return 'right'
def equal_block(block1, block2):
	block1 = Block.get(block1)
	block2 = Block.get(block2)
	# block1.depth = 0
	# block2.depth = 0
	block1.count = 0
	block2.count = 0
	# print(block1.put())
	# print(block2.put())
	if block1.put() == block2.put():
		return 1
	return 0
def Valid(block):
	block = Block.get(block)
	for tx in block.body:
		tx = Tx.get(tx)
		if tx.data == 'dirt':
			return 0;
	return 1
def cleaner(block, sk):
	block = Block.get(block)
	# block.dirt = 1
	tx_list = []
	for tx in block.body:
		tx = Tx.get(tx)
		tx.data = 'clean'
		tx_list.append(tx.put())
	block.body = tx_list


	merktree = Merktree([Tx.get(tx) for tx in block.body])
	merktree.create()
	head = Block_head.get(block.head)
	head.d = merktree.d
	head.sigma_d = sign.sign(merktree.d, sk)
	block.head  = head.put()

	return block.put()
def vote_error(block):
	block = Block.get(block)
	block.dirt = 0
	return block.put()



def main():
	sk1,pk1 = sign.keygen(P)
	sk2,pk2 = sign.keygen(P)
	tx1 = Tx(pk1, pk2, 10, "haha")
	tx1.sign(sk1)
	tx0 = Tx(pk1, pk2, 10, str([pk1,pk2]))
	tx0.sign(sk1)
	block_pre = create_gensis_block(tx0,sk1)
	block_new = Block()
	block_new.create(block_pre.put(), [tx0, tx1], sk2, sl='1')
	# print(block_new.put())
	ans = verify_block(block_pre.put(), block_new.put(), pk2)
	print(equal_block(block_new.put(), block_new.put()))
if __name__ == '__main__':
	main()

		