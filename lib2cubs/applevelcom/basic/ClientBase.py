import logging
from datetime import datetime
from time import sleep

from lib2cubs.lowlevelcom import GenericConnection

from . import AppLevelSkeletonBase
from lib2cubs.applevelcom.basic import AppBase
from .internals import action, RemoteForClient


class ClientBase(AppLevelSkeletonBase, AppBase):

	name: str = 'Client Base (l2c-al)'
	_host: str = None
	_port: int = None
	_pem_bundle_name: str = None
	is_running: bool = True

	_is_ssl_disabled: bool = False

	@property
	def is_ssl_disabled(self):
		return self._is_ssl_disabled

	def __init__(self, pem_bundle_name: str, host: str = 'localhost', port: int = 60009,
				disable_ssl: bool = False,
				confirm_disabling_of_ssl: bool = False):
		super(ClientBase, self).__init__()
		self._host = host
		self._port = port
		self._pem_bundle_name = pem_bundle_name
		self._is_ssl_disabled = disable_ssl and confirm_disabling_of_ssl

	def init(self):
		pass

	def run(self) -> None:
		logging.debug('Preparing GenericConnection')
		GenericConnection.prepare_client(
			self._client_callback,
			self._pem_bundle_name,
			self._host, self._port,
			self._is_ssl_disabled
		)

	def _client_callback(self, cib):
		self.connection = GenericConnection.gen_new_client_connection(cib, self.events_subscription())

		logging.debug('Client running pre-init')
		self._pre_init()

		logging.debug('Client running init')
		self.init()

		logging.debug('Client running main')
		res = self.main(self._remote)
		logging.debug('Main of client has finished')

		if res:
			while not self.is_finished:
				sleep(5)
		self.stop_main()

		# connection.is_auto_reconnect_allowed = True
		self.connection.wait_for_subroutines()

	@property
	def who_am_i(self):
		return {
			'type': 'client',
			'description': 'Client Application',
		}

	@action
	def soft_shutdown_initiated(self, remote: RemoteForClient, dt: datetime):
		logging.debug('Soft Shutdown has been initiated by the server side %s', dt)
