from lib2cubs.applevelcom.basic import ClientBase, ServerBase


class HandlerBase(ClientBase):

	parent: ServerBase = None

	def start_app(self):
		if not self._is_app_started:
			self._thread.start()
			self._is_app_started = True

	def _disconnecting(self):
		pass
		# print('Client has disconnected')

	def _check_delivery_status_loop(self):
		while self._connection.is_connected:
			self._check_delivery_status()
