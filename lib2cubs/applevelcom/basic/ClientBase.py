from queue import Queue
from threading import Lock, Thread
from time import sleep

from lib2cubs.lowlevelcom.basic import SimpleFrame

from lib2cubs.applevelcom.basic import AppBase, Connection, Remote


class ClientBase(AppBase):

	_action_threads: list = list()
	_queue_sending_frames: Queue = None
	_thread: Thread = None

	_sent_unconfirmed_frames: dict = dict()
	_sent_unconfirmed_frame_lock: Lock = Lock()
	_is_app_started: bool = False
	_remote = None

	def __init__(self, *args, **kwargs):
		super(ClientBase, self).__init__(*args, **kwargs)
		self._thread = Thread(target=self._run_app, daemon=True)
		self._queue_sending_frames = Queue()
		self.init()

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
		# All the events must be prepared and subscribed before the internals will start the selectors non-blocking behaviour
		self._connection.ready_to_operate()
		# start_new_thread(self._check_delivery_status, (sock,))

	def app(self, remote):
		pass

	def _after_app(self):
		pass

	def _check_delivery_status(self, sock):
		while self._is_running:
			sleep(5)
			if self._sent_unconfirmed_frames:
				self._sent_unconfirmed_frame_lock.acquire()
				print('Undelivered frames:', self._sent_unconfirmed_frames.keys())
				for uid, frame in self._sent_unconfirmed_frames.items():
					print('Re-sending frames: ', uid)
					self.send(frame)
				self._sent_unconfirmed_frame_lock.release()

	def _sending_data(self):
		frame = self._queue_sending_frames.get()
		if 'msg_id' in frame.content:
			self._sent_unconfirmed_frame_lock.acquire()
			self._sent_unconfirmed_frames[frame.content['msg_id']] = frame
			self._sent_unconfirmed_frame_lock.release()
		self._connection.send_frame(frame)
		self._queue_sending_frames.task_done()

	def _receiving_data(self):
		frame = self._connection.collect_frame()
		# print(f'Frame is being collected: {frame}')
		if frame:
			t = Thread(target=self.frame_received, args=(frame, ))
			self._action_threads.append(t)
			t.start()

	def send(self, frame):
		self._queue_sending_frames.put(frame)

	# def reconnect_if_needed(self, sock, e = None):
	# 	print(f'Need to reconnect: {e}')
	# 	i = 5
	# 	while i and not self._is_socket_connected(sock):
	# 		print(f'Short sleep of 5 before reconnect attempt.')
	# 		sleep(5)
	# 		print(f'Reconnecting attempt: {i}')
	# 		sock.close()
	# 		sock.connect((self.endpoint, self.port))

	# def _is_socket_connected(self, sock):
	# 	try:
	# 		sock.send(0)
	# 	except:
	# 		return False
	# 	return True

	def frame_received(self, frame: SimpleFrame):
		self._sent_unconfirmed_frame_lock.acquire()

		data = frame.content

		if 'confirm_for' in data:
			uid = data["confirm_for"]

			if uid in self._sent_unconfirmed_frames:
				# print(f'Received confirmation for: {uid}')
				del self._sent_unconfirmed_frames[uid]
			else:
				print(f'Received ORPHANED confirmation for: {uid}. Skipping.')

		self._sent_unconfirmed_frame_lock.release()

		if 'action' in data:
			self.confirm_frame(data['msg_id'])
			self._remote.receive_action(frame)

		if 'return' in data:
			self.confirm_frame(data['msg_id'])
			self._remote.receive_response(frame)

	def confirm_frame(self, uid):
		self.send(SimpleFrame({'confirm_for': uid}))

	def _disconnected(self, sock):
		print(f'Connection is closed.')
		# self._is_running = False
		# self.sel.unregister(sock)
		# sock.close()

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
		if not self._is_app_started:
			# print('Connecting...')
			self._connection.connect()
			# print('Connected!')
			# self._remote = Remote(self)
			self._thread.start()
			self._is_app_started = True

	@property
	def remote(self) -> Remote:
		self.start_app()
		print('Getting remote')
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
