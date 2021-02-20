from abc import abstractmethod
from os.path import join

from lib2cubs.applevelcom.basic import Connection


class AppBase:

	# _is_running: bool = True

	# sock: socket = None
	# endpoint: str = None
	# port: int = None
	# _remote = None
	# sel: BaseSelector = None
	_connection: Connection = None

	def __init__(self, conn: Connection):
		self._connection = conn

	@classmethod
	@abstractmethod
	def create_connection(cls, host, port, client_crt=None, enc_key=None, server_crt=None, server_hostname=None) -> Connection:
		pass

	@classmethod
	def _common_prepare_connection(cls, t, host: str, port: int, client_crt=None, enc_key=None, server_crt=None, server_hostname=None) -> Connection:
		conn = Connection(t, host, port)
		if t in (Connection.TYPE_CLIENT, Connection.TYPE_SERVER):
			default_subdir = 'ssl'
			conn.ssl_client_cert = join(default_subdir, 'client.crt') if not client_crt else client_crt
			conn.ssl_server_cert = join(default_subdir, 'server.crt') if not server_crt else server_crt
			if t == Connection.TYPE_CLIENT:
				conn.ssl_client_key = join(default_subdir, 'client.key') if not enc_key else enc_key
			if t == Connection.TYPE_SERVER:
				conn.ssl_server_key = join(default_subdir, 'server.key') if not enc_key else enc_key
			conn.ssl_server_hostname = '2cubs-server' if not server_hostname else server_hostname
		return conn

	con_data: dict = None

	@classmethod
	def get_instance(cls, host: str = '127.0.0.1', port: int = 60009, client_crt=None, enc_key=None, server_crt=None, server_hostname=None):
		instance = cls(cls.create_connection(host, port, client_crt, enc_key, server_crt, server_hostname))
		instance.con_data = {
			'host': host,
			'port': port,
			'client_crt': client_crt,
			'enc_key': enc_key,
			'server_crt': server_crt,
			'server_hostname': server_hostname
		}
		return instance

	def start_app(self):
		pass
