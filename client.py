import socket

class Client:
	'''
	args client 연결 옵션
	'''
	def __init__(self, host, port):
		self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		
	def connect(self, host, port):
		try:
			self.client_socket.connect((host,port))
		except:
			print("Error: cannot connect to server")
			return 
	def disconnect(self):
		self.client_socket.close()
		
	def send(self, filename, data):
		self.client_socket.sendall(filename.encode())
		reSize = self.client_socket.recv(1024)

	def receive(self):
		self.rbuff = self.client_socket.recv(1024)
		return str(self.rbuff, encoding='utf-8')