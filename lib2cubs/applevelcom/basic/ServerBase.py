import logging
from datetime import datetime
from threading import Lock

from lib2cubs.lowlevelcom import GenericConnection

from lib2cubs.applevelcom.basic import AppBase
from lib2cubs.applevelcom.basic.HandlerBase import HandlerBase


class ServerBase(AppBase):
	name: str = 'Server Base (l2c-al)'

	is_running = True

	_host: str = None
	_port: int = None
	_pem_bundle_name: str = None

	_is_ssl_disabled: bool = False

	# _connection_threads = None
	_connection_class = None
	_handler_class = None
	_active_handlers: list = None
	_active_handlers_lock: Lock = None

	@property
	def is_ssl_disabled(self):
		return self._is_ssl_disabled

	def __init__(self, pem_bundle_name: str, host: str = 'localhost', port: int = 60009,
				connection_class=GenericConnection,
				handler_class=HandlerBase,
				disable_ssl: bool = False,
				confirm_disabling_of_ssl: bool = False):
		super(ServerBase, self).__init__()
		self._host = host
		self._port = port
		self._pem_bundle_name = pem_bundle_name
		self._is_ssl_disabled = disable_ssl and confirm_disabling_of_ssl
		# self._connection_threads = []
		self._connection_class = connection_class
		self._handler_class = handler_class
		self._active_handlers = []
		self._active_handlers_lock = Lock()

	def run(self) -> None:

		self._connection_class.prepare_server(
			self._server_callback,
			self._pem_bundle_name,
			self._host, self._port,
			self._is_ssl_disabled
		)

		logging.debug('## ExampleServer: waiting for sub-threads to finish')
		# for t in self._connection_threads:
		# 	t.join()

	def _server_callback(self, sock):
		while self.is_running:
			handler = self._handler_class()
			handler.set_server_obj(self)

			gen = self._connection_class.gen_new_server_connection(sock, handler.events_subscription())

			for connection in gen:
				if connection:
					handler.connection = connection
					handler.start()
					self.add_active_handler(handler)

	def soft_shutdown(self):
		dt_at = datetime.now()
		for handler in self._active_handlers:
			handler: HandlerBase
			handler.notify_client_soft_shutdown(dt_at)
		logging.debug('Soft Shutdown has been triggered for %s', self._active_handlers)
		self.is_running = False

	def get_active_handlers(self) -> tuple:
		with self._active_handlers_lock:
			res = tuple(self._active_handlers)
		return res

	def del_active_handler(self, handler):
		with self._active_handlers_lock:
			self._active_handlers.remove(handler)
			logging.debug('Active handler %s was removed from the list', handler)

	def add_active_handler(self, handler):
		with self._active_handlers_lock:
			self._active_handlers.append(handler)
			logging.debug('Active handler %s was added to the list', handler)
