from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from ssl import SSLWantReadError
from threading import Thread, Lock
from time import sleep

from lib2cubs.lowlevelcom.Connection import Connection as LibConnection

from lib2cubs.applevelcom.transport import SimpleFrame


class Connection(LibConnection):

	# Reference to the handling app on the side of the server
	TYPE_HANDLER = 'client-handler'

	LL_EVENT_ACCEPT = 'accept'
	LL_EVENT_READ = 'read'
	LL_EVENT_WRITE = 'write'
	LL_EVENT_DISCONNECTED = 'disconnected'

	_sel: DefaultSelector = None

	_perform_select: bool = True
	_subscribed_events: dict = None

	_t_selecting_events: Thread = None

	def __init__(self, *args, **kwargs):
		super(Connection, self).__init__(*args, **kwargs)
		self._subscribed_events = {
			self.LL_EVENT_ACCEPT: list(),
			self.LL_EVENT_READ: list(),
			self.LL_EVENT_WRITE: list(),
			self.LL_EVENT_DISCONNECTED: list(),
		}

	def unsubscribe_from_event(self, event_name: str, cb: callable) -> bool:
		if event_name not in self._subscribed_events:
			return False
		if cb in self._subscribed_events[event_name]:
			self._subscribed_events[event_name].remove(cb)
		return True

	def subscribe_to_event(self, event_name: str, cb: callable) -> bool:
		"""
		Subscribing to low-level communication events (accept, read, write).
		:param event_name: One of: 'accept', 'read' or 'write'
		:param cb: Callback that should be used for the subscription
		:return: Returns True in case of successful subscription or False otherwise (Basically indication if subscribed)
		"""
		if event_name not in self._subscribed_events:
			return False

		if cb not in self._subscribed_events[event_name]:
			self._subscribed_events[event_name].append(cb)

		# Already subscribed
		return True

	def _after_open_connection(self):
		super(Connection, self)._after_open_connection()
		self._register_events()
		self._t_selecting_events = Thread(target=self._selecting_events, daemon=True)

	def ready_to_operate(self):
		self._t_selecting_events.start()

	_t_read: Thread = None
	_t_write: Thread = None

	def _reading(self):
		self._read_lock.acquire()
		while True:
			self._read_lock.acquire()
			self._invoke_events_callbacks(self.LL_EVENT_READ)
		self._read_lock.release()

	def _writing(self):
		self._write_lock.acquire()
		while True:
			self._write_lock.acquire()
			self._invoke_events_callbacks(self.LL_EVENT_WRITE)
		self._write_lock.release()

	def _register_events(self):
		self._sel = DefaultSelector()
		if self._type == self.TYPE_SERVER:
			self._sel.register(self._socket, EVENT_READ, self._event_accept)
		if self._type in (self.TYPE_HANDLER, self.TYPE_CLIENT):
			self._sel.register(self._socket, EVENT_READ | EVENT_WRITE, self._event_communicate)
			self._read_lock = Lock()
			self._write_lock = Lock()

			self._t_read = Thread(target=self._reading, daemon=True)
			self._t_read.start()

			self._t_write = Thread(target=self._writing, daemon=True)
			self._t_write.start()

	def _selecting_events(self):
		while self._perform_select:
			for key, mask in self._sel.select():
				key.data(mask)

	def _invoke_events_callbacks(self, event_name, *args, **kwargs):
		# print(f'LL EVENT Invoked: {event_name}')
		if self._subscribed_events[event_name]:
			for cb in self._subscribed_events[event_name]:
				cb(*args, **kwargs)
		else:
			if event_name == self.LL_EVENT_WRITE:
				# If there is no write subscriptions, this code
				# would decrease unnecessary CPU usage by just a simple timeout.
				# Should not be considered as a hack, though if you have
				# a better solution - please propose.
				print('No write subscription')
				sleep(10)

	def _event_accept(self, mask):
		if mask & EVENT_READ:
			new_connection = self.accept(self.TYPE_HANDLER)
			self._invoke_events_callbacks(self.LL_EVENT_ACCEPT, new_connection)

	_read_lock: Lock = None
	_write_lock: Lock = None

	def _event_communicate(self, mask):
		if mask & EVENT_READ:
			if self._read_lock is not None and self._read_lock.locked():
				self._read_lock.release()
			# Thread(target=self._invoke_events_callbacks, args=(self.LL_EVENT_READ, ), daemon=True).start()
		if mask & EVENT_WRITE:
			if self._write_lock is not None and self._write_lock.locked():
				self._write_lock.release()
			# self._invoke_events_callbacks(self.LL_EVENT_WRITE)

	def send_frame(self, frame):
		# print('Sending DATA')
		self._socket.send(bytes(frame))

	def collect_frame(self):
		frame = None
		try:
			frame = self._gather_frame_from_socket(SimpleFrame)
			if frame is None:
				self._invoke_events_callbacks(self.LL_EVENT_DISCONNECTED)
		except ConnectionResetError as e:
			self._invoke_events_callbacks(self.LL_EVENT_DISCONNECTED)
		except SSLWantReadError as e:
			pass

		if isinstance(frame, SimpleFrame):
			return frame

		return False
