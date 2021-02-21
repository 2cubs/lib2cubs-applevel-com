import re
from copy import copy
from queue import Queue
from threading import Lock, Thread
from time import sleep

from lib2cubs.applevelcom.basic import AppBase, Connection, Remote
from lib2cubs.applevelcom.transport import SimpleFrame


class ClientBase(AppBase):

	EVENT_CONNECTION_DISCONNECTED: str = 'connection_disconnected'

	_action_threads: list = list()
	_queue_sending_frames: Queue = None
	_thread: Thread = None
	_t_unsent_frames_check: Thread = None

	_sent_unconfirmed_frames: dict = dict()
	_sent_unconfirmed_frame_lock: Lock = Lock()
	_is_app_started: bool = False
	_remote = None
	_event_subscriptions: dict = None

	def __init__(self, *args, **kwargs):
		super(ClientBase, self).__init__(*args, **kwargs)
		self._thread = Thread(target=self._run_app, daemon=True)
		self._queue_sending_frames = Queue()
		self.init()
		self._t_unsent_frames_check = Thread(target=self._check_delivery_status_loop, daemon=True)
		self._t_unsent_frames_check.start()

	def init(self):
		pass

	def _run_app(self):
		self._before_app()
		self.app(self._remote)
		self._after_app()

	def _before_app(self):
		self._remote = Remote(self)
		self._connection.subscribe_to_event(Connection.LL_EVENT_WRITE, self._sending_data)
		self._connection.subscribe_to_event(Connection.LL_EVENT_READ, self._receiving_data)
		self._connection.subscribe_to_event(Connection.LL_EVENT_DISCONNECTED, self._disconnecting)
		# All the events must be prepared and subscribed before the internals will start the selectors non-blocking behaviour
		self._connection.ready_to_operate()

	def app(self, remote):
		pass

	def _after_app(self):
		pass

	def _check_delivery_status(self):
		# print('sleep check 5')
		sleep(5)
		if self._sent_unconfirmed_frames:
			self._sent_unconfirmed_frame_lock.acquire()
			# print('Undelivered frames:', self._sent_unconfirmed_frames.keys())
			for uid, frame in self._sent_unconfirmed_frames.items():
				# print('Re-sending frames: ', uid)
				self.send(frame)
			self._sent_unconfirmed_frame_lock.release()

	def _check_delivery_status_loop(self):
		while True:
			self._check_delivery_status()

	_send_frame_lock: Lock = Lock()

	def _sending_data(self):
		# print(f'Getting something from a queue')
		frame = self._queue_sending_frames.get()
		# print(f'Sending now frame {frame}')
		if 'msg_id' in frame.content:
			self._sent_unconfirmed_frame_lock.acquire()
			self._sent_unconfirmed_frames[frame.content['msg_id']] = frame
			self._sent_unconfirmed_frame_lock.release()

		# print('Waiting for sending lock')
		# self._send_frame_lock.acquire()
		self._connection.send_frame(frame)
		# self._send_frame_lock.release()

		self._queue_sending_frames.task_done()

	def _receiving_data(self):
		frame = self._connection.collect_frame()
		# print(f'Frame is being collected: {frame}')
		if frame:
			t = Thread(target=self.frame_received, args=(frame, ))
			self._action_threads.append(t)
			t.start()

	auto_reconnect: bool = True

	def _disconnecting(self):
		self.trigger_event(self.EVENT_CONNECTION_DISCONNECTED)
		# self._send_frame_lock.acquire()
		# print('!! Disconnected !!')
		# if self.auto_reconnect and self._is_app_started:
		# 	print('Connection error. sleeping 5')
		# 	sleep(5)
		# 	self.start_app()
		# self._check_delivery_status()
		# print('Waiting 5')
		# sleep(5)
		# print('Checking delivery status')
		# self._check_delivery_status()

	def send(self, frame):
		self._queue_sending_frames.put(frame)

	def frame_received(self, frame: SimpleFrame):
		self._sent_unconfirmed_frame_lock.acquire()

		data = frame.content

		if 'confirm_for' in data:
			uid = data["confirm_for"]

			if uid in self._sent_unconfirmed_frames:
				# print(f'Received confirmation for: {uid}')
				del self._sent_unconfirmed_frames[uid]
			else:
				pass
				# print(f'Received ORPHANED confirmation for: {uid}. Skipping.')

		self._sent_unconfirmed_frame_lock.release()

		if 'action' in data:
			self.confirm_frame(data['msg_id'])
			self._remote.receive_action(frame)

		if 'return' in data:
			self.confirm_frame(data['msg_id'])
			self._remote.receive_response(frame)

	def confirm_frame(self, uid):
		self.send(SimpleFrame({'confirm_for': uid}))

	@classmethod
	def create_connection(cls, host: str, port: int, client_crt=None, client_key=None, server_crt=None, server_hostname=None) -> Connection:
		conn = cls._common_prepare_connection(Connection.TYPE_CLIENT, host, port,
			client_crt=client_crt,
			enc_key=client_key,
			server_crt=server_crt,
			server_hostname=server_hostname
		)
		return conn

	def start_app(self):
		if not self._is_app_started or not self._connection.is_connected:
			try:
				self._connection.connect(True)
				# self._connection.ready_to_operate()
				if not self._is_app_started:
					self._thread.start()
				else:
					# Must be invoked after every reconnection.
					self._connection.ready_to_operate()
					# if self._send_frame_lock.locked():
					# 	self._send_frame_lock.release()
				self._is_app_started = True
			except ConnectionRefusedError as e:
				self._is_app_started = False
				raise e

	@property
	def remote(self) -> Remote:
		self.start_app()
		# print('Getting remote')
		return self._remote

	@property
	def thread(self):
		return self._thread

	@property
	def id(self):
		if not self.endpoint:
			raise Exception('Endpoint is empty')
		return f'{self.endpoint[0]}:{self.endpoint[1]}'

	@property
	def endpoint(self):
		return self._connection.get_endpoint()

	@classmethod
	def action_wrap(cls, func: callable):
		def wrapper(s, *args, **kwargs):
			return func(s, *args, **kwargs)
		return wrapper

	def subscribe_to_event(self, name: str, cb: callable):
		if self._event_subscriptions is None:
			self._event_subscriptions = dict()
		if name not in self._event_subscriptions:
			self._event_subscriptions[name] = list()
		self._event_subscriptions[name].append(cb)

	def unsubscribe_from_event(self, name: str, cb: callable):
		if self._event_subscriptions is None:
			self._event_subscriptions = dict()
		if name not in self._event_subscriptions:
			self._event_subscriptions[name] = list()
		if cb in self._event_subscriptions[name]:
			self._event_subscriptions[name].remove(cb)

	def trigger_event(self, __name: str, *args, **kwargs):
		if __name in self._event_subscriptions:
			for cb in self._event_subscriptions[__name]:
				cb(*args, **kwargs)

	@classmethod
	def is_host_ip(cls, host: str) -> bool:
		"""
		Returns true if the string host is an IP address (only ipv4 for now)
		TODO Has to be relocated to another place
		:return:
		"""
		octet_re = r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]{1,2})'
		reg_exp_line = r"^(%s\.){3}%s$" % (octet_re, octet_re)
		return bool(re.match(reg_exp_line, host))

	@classmethod
	def get_instance(cls, host: str = '127.0.0.1', port: int = 60009, client_crt=None, client_key=None, server_crt=None, server_hostname=None, ssl_cred_bundle=None):
		kwargs = cls._prepare_connection_params(host, port, client_crt, client_key, server_crt, server_hostname, ssl_cred_bundle)

		if 'ssl_cred_bundle' in kwargs:
			del kwargs['ssl_cred_bundle']
		instance = super(ClientBase, cls).get_instance(**kwargs)
		return instance

	@classmethod
	def _prepare_connection_params(cls, host: str = '127.0.0.1', port: int = 60009, client_crt=None, client_key=None, server_crt=None, server_hostname=None, ssl_cred_bundle=None):

		if cls.is_host_ip(host) and not server_hostname:
			raise Exception('When the host is an IP address, server_hostname param is mandatory!')
		else:
			# If host - is a domain name, use it as server_hostname (SNI),
			# otherwise if the server_hostname is specified - it has priority over the host's hostname value.
			server_hostname = server_hostname if server_hostname else host

		if ssl_cred_bundle:
			client_crt = client_crt if client_crt else ssl_cred_bundle
			client_key = client_key if client_key else ssl_cred_bundle
			server_crt = server_crt if server_crt else ssl_cred_bundle

		return {
			'host': host, 'port': port,
			'client_crt': client_crt, 'enc_key': client_key, 'server_crt': server_crt,
			'server_hostname': server_hostname,
			# 'ssl_cred_bundle': ssl_cred_bundle
		}

	def connect(self, **kwargs):
		"""
		Important: if provided any argument - then the reconnection will be forced, and the connection data must be provided,
		if no argument is provided - then reconnecting to the existing connection data.
		:param kwargs:
		:return:
		"""
		forced = False
		if len(kwargs) > 0:
			self.con_data = self._prepare_connection_params(**kwargs)
			forced = True
		self.reconnect(forced)

	def reconnect(self, forced: bool = True):
		if not self._connection or not self._connection.is_connected or forced:
			self.disconnect()
			self.start_app()

	def _new_connection(self):
		kwargs = copy(self.con_data)
		kwargs['client_key'] = kwargs['enc_key'] if 'enc_key' in kwargs else kwargs['client_key']
		if 'enc_key' in kwargs:
			del kwargs['enc_key']
		return self.create_connection(**kwargs)

	def disconnect(self, prevent_event: bool = False):
		"""
		Method will trigger the "disconnect" event if the app is connected and param "prevent_event" is not True
		:param prevent_event:
		:return:
		"""
		if self.is_connected and not prevent_event:
			# TODO rename the method
			self._disconnecting()
		self._connection = self._new_connection()

	@property
	def is_connected(self) -> bool:
		return self._connection.is_connected
