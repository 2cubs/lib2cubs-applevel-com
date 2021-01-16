from time import sleep

from lib2cubs.applevelcom.basic import AppBase, Connection


class ServerBase(AppBase):

	handler_class = None
	_active_handlers: dict = None

	def __init__(self, *args, **kwargs):
		super(ServerBase, self).__init__(*args, **kwargs)
		self._active_handlers = dict()
		self._connection.subscribe_to_event('accept', self._handler_connection_ready)

	def _handler_connection_ready(self, connection: Connection):
		handler = self.handler_class(connection)
		print('Incoming connection. Accepting. Deploying handler')
		print(f'Handler: {handler.id}')
		handler.start_app()
		self._active_handlers[handler.id] = handler

	@classmethod
	def get_instance(cls, handler_class=None, *args, **kwargs):
		instance = super(ServerBase, cls).get_instance(*args, **kwargs)
		instance.handler_class = handler_class if handler_class is not None else instance.handler_class
		return instance

	@classmethod
	def create_connection(cls, host: str, port: int, client_crt=None, server_key=None, server_crt=None, server_hostname=None) -> Connection:
		conn = cls._common_prepare_connection(Connection.TYPE_SERVER, host, port,
			client_crt=client_crt,
			enc_key=server_key,
			server_crt=server_crt,
			server_hostname=server_hostname
		)
		return conn

	def start_app(self):
		self._connection.listen()
		self._connection.ready_to_operate()
		while True:
			sleep(10)
