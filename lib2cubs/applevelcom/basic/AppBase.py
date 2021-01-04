from abc import abstractmethod
from socket import socket


class AppBase:

	sock: socket = None
	endpoint: str = None
	port: int = None

	@abstractmethod
	def run(self):
		pass

	def before_app(self, sock: socket = None):
		if sock is not None:
			self.sock = sock

	def after_app(self):
		pass

	def _exec_app(self, sock: socket = None):
		self.before_app(sock)
		self.app()
		self.after_app()

	@abstractmethod
	def app(self):
		pass
