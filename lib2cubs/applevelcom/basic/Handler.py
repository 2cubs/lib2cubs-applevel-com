from lib2cubs.applevelcom.basic import ClientBase, ServerBase


class Handler(ClientBase):

	parent: ServerBase = None

	def start_app(self):
		if not self._is_app_started:
			self._thread.start()
			self._is_app_started = True
