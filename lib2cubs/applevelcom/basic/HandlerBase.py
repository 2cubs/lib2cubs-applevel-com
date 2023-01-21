import logging
from datetime import datetime
from threading import Thread
from time import sleep

from . import AppLevelSkeletonBase
from .internals import RemoteForServer


class HandlerBase(AppLevelSkeletonBase, Thread):

	_server_obj = None

	def set_server_obj(self, server_obj):
		from .ServerBase import ServerBase

		if not self._server_obj:
			self._server_obj: ServerBase = server_obj

	def run(self) -> None:
		if not self.connection:
			raise Exception('Connection object was not provided into handler. Failed')

		logging.debug('ServerHandler running pre-init')
		self._pre_init()

		logging.debug('ServerHandler running init')
		self.init()

		logging.debug('ServerHandler running main')
		res = self.main(self._remote)
		logging.debug('Main of client has finished')

		if res is None:
			# This default behaviour of server-handler differs from client-side
			# By default it should be in an infinite loop
			res = not self.is_finished

		if res:
			while not self.is_finished:
				sleep(5)
		self._server_obj.del_active_handler(self)
		self.stop_main()

		# connection.is_auto_reconnect_allowed = True
		self.connection.wait_for_subroutines()

	@property
	def who_am_i(self):
		return {
			'type': 'server',
			'description': 'Server Handler',
		}

	def notify_client_soft_shutdown(self, dt_at: datetime):
		logging.debug('Soft Shutdown notification sending..')
		remote: RemoteForServer = self._remote
		remote.asynced().soft_shutdown_initiated(str(dt_at))
		logging.debug('Soft Shutdown notification sent')
