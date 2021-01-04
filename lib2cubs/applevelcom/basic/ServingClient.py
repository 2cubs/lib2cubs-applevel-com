from lib2cubs.lowlevelcom.basic import SimpleFrame

from lib2cubs.applevelcom.basic import ClientBase


class ServingClient(ClientBase):

	def __init__(self):
		pass

	def run(self):
		self._exec_app()

	def app(self):
		print(f'ServClient connected on {self.sock}')
		data = {
			'data': f'Hello World! from {self.endpoint}:{self.port}. Happy year 2021!'
		}
		self.sock.send(bytes(SimpleFrame(data)))
