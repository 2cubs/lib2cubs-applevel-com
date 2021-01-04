from lib2cubs.lowlevelcom.basic import SimpleFrame

from lib2cubs.applevelcom.basic import ServingClient


class ExampleServingClient(ServingClient):

	def app(self):
		print(f'ServClient connected on {self.sock}')
		data = {
			'data': f'Hello World! from {self.endpoint}:{self.port}. Happy year 2021!'
		}
		self.sock.send(bytes(SimpleFrame(data)))
