from lib2cubs.lowlevelcom.basic import SimpleFrame

from lib2cubs.applevelcom.basic import ClientBase


class ExampleClient(ClientBase):

	def app(self):
		print(f'Client app is connected to: {self.endpoint}:{self.port}')
		frame = self.sock.recv(1024)
		data = SimpleFrame.parse(frame)
		print(data.content)
