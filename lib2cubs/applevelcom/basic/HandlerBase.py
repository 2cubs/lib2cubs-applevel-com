import logging
from threading import Thread
from time import sleep

from lib2cubs.applevelcom.basic.AppLevelSkeletonBase import AppLevelSkeletonBase


class HandlerBase(AppLevelSkeletonBase, Thread):

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
		self.stop_main()

		# connection.is_auto_reconnect_allowed = True
		self.connection.wait_for_subroutines()
