from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha384
import json

class My_point(point.Point):
	"""docsg for my_point"""
	def __init__(self, x, y,P=curve.P256):
		super(My_point, self).__init__(x, y, P)
		self.P = P
	def put(self):
		return {'x':self.x,'y':self.y}
	def get(dic,P):
		return My_point(dic['x'],dic['y'],P)
		 
def init():
	return curve.P256
def keygen(P):
	private_key = keys.gen_private_key(P)
	public_key = keys.get_public_key(private_key, P)
	public_key = My_point(public_key.x, public_key.y, P).put()
	return private_key,public_key
def sign(m, private_key):
	return ecdsa.sign(m, private_key)
def verify(sigma, m, public_key, P):
	if type(public_key) == type({}):
		public_key = My_point.get(public_key,P)
	return ecdsa.verify(sigma, m, public_key)
def main():
	m = "haha"
	P = init()
	sk,pk = keygen(P)
	sigma = sign(m,sk)
	print(verify(sigma, m, pk, P))

if __name__ == '__main__':
	main()