from lib2cubs.applevelcom.basic import ClientBase, ServerBase


class ServingClient(ClientBase):

	parent: ServerBase = None

	@property
	def is_running(self):
		return self.parent._is_running

	def __init__(self, sock, parent):
		self.sock = sock
		self.parent = parent

	def run(self):
		self._exec_app()
