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

	_connection_threads = None
	_connection_class = None
	_handler_class = None

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
		self._connection_threads = []
		self._connection_class = connection_class
		self._handler_class = handler_class

	def run(self) -> None:

		self._connection_class.prepare_server(
			self._server_callback,
			self._pem_bundle_name,
			self._host, self._port,
			self._is_ssl_disabled
		)

		print('## ExampleServer: waiting for sub-threads to finish')
		for t in self._connection_threads:
			t.join()

	def _server_callback(self, sock):
		while self.is_running:
			handler = self._handler_class()

			gen = self._connection_class.gen_new_server_connection(sock, handler.events_subscription())

			for connection in gen:
				if connection:
					handler.connection = connection
					self._connection_threads.append(handler)
					handler.start()
