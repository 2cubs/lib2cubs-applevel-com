from abc import abstractmethod
from selectors import DefaultSelector, BaseSelector
from socket import socket

from lib2cubs.applevelcom.basic import Remote


class AppBase:

	_is_running: bool = True

	sock: socket = None
	endpoint: str = None
	port: int = None
	remote: Remote = None
	sel: BaseSelector = None

	@classmethod
	def _action(cls, func: callable):
		def wrapper(s, *args, **kwargs):
			return func(s, *args, **kwargs)
		return wrapper

	@abstractmethod
	def run(self):
		pass

	def before_app(self, sock: socket = None):
		if sock is not None:
			self.sock = sock
		self.sock.setblocking(False)
		self.remote = Remote(self.sock, self)
		self.sel = DefaultSelector()

	def after_app(self):
		pass

	def _exec_app(self, sock: socket = None):
		self.before_app(sock)
		self.app(self.remote)
		self.after_app()

	@abstractmethod
	def app(self, remote: Remote):
		pass

	def _t_sel_events_loop(self, name):
		while self._is_running:
			events = self.sel.select()
			for key, mask in events:
				key.data(key.fileobj, mask)
