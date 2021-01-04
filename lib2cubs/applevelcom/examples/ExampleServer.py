from lib2cubs.applevelcom.basic import ServerBase
from lib2cubs.applevelcom.examples import ExampleServingClient


class ExampleServer(ServerBase):

	# TODO multiprocessing improvement
	def app(self):
		while True:
			conn, addr = self.sock.accept()
			cc = ExampleServingClient()
			cc.sock = conn
			cc.run()
			conn.close()
