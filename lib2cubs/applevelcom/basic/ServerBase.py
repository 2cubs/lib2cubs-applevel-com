from _thread import start_new_thread
from abc import abstractmethod
from selectors import EVENT_READ, EVENT_WRITE
from socket import socket
from time import sleep

from lib2cubs.lowlevelcom import CommunicationEngine

from lib2cubs.applevelcom.basic import AppBase


class ServerBase(AppBase):

	@classmethod
	@abstractmethod
	def get_serving_client_class(cls):
		pass

	def __init__(self, endpoint: str, port: int):
		self.endpoint = endpoint
		self.port = port

	def run(self):
		CommunicationEngine.secure_server(self._setup_app, self.endpoint, self.port)

	def before_app(self, sock: socket = None):
		super(ServerBase, self).before_app(sock)
		self.sel.register(self.sock, EVENT_READ, self._sel_accept)
		self._t_sel_events_loop('selectors event loop thread')

	def _sel_accept(self, conn, mask):
		print(f'Connection {conn} is accepted')
		sock, addr = conn.accept()
		start_new_thread(self._new_conn, (sock,))

	def _new_conn(self, sock):
		cc = self.get_serving_client_class()(sock, self)
		cc.run()
