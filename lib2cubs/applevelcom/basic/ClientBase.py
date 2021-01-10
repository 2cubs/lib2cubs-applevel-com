from _thread import start_new_thread
from datetime import datetime
from queue import Queue
from selectors import EVENT_READ, EVENT_WRITE
from socket import socket
from ssl import SSLWantReadError
from threading import Lock
from time import sleep

from lib2cubs.lowlevelcom import CommunicationEngine
from lib2cubs.lowlevelcom.basic import SimpleFrame

from lib2cubs.applevelcom.basic import AppBase


class ClientBase(AppBase):

	_frame_form: SimpleFrame = None
	_action_threads: list = list()
	_queue_write: Queue = None

	def __init__(self, endpoint: str, port: int):
		self.endpoint = endpoint
		self.port = port

	def run(self):
		CommunicationEngine.secure_client(self._setup_app, self.endpoint, self.port)

	def before_app(self, sock: socket = None):
		super(ClientBase, self).before_app(sock)
		self._queue_write = Queue()
		self.sel.register(self.sock, EVENT_READ, self._event_socket_read)
		# TODO Change the threads invocation
		start_new_thread(self._t_sel_events_loop, ('selectors event loop thread', ))
		start_new_thread(self._event_socket_write, (sock, EVENT_WRITE))
		start_new_thread(self._check_delivery_status, (sock,))

	_sent_unconfirmed_frames: dict = dict()
	_sent_unconfirmed_frame_lock: Lock = Lock()

	def _check_delivery_status(self, sock):
		while self._is_running:
			sleep(5)
			if self._sent_unconfirmed_frames:
				self._sent_unconfirmed_frame_lock.acquire()
				print('Undelivered frames:', self._sent_unconfirmed_frames.keys())
				for uid, frame in self._sent_unconfirmed_frames.items():
					print('Re-sending frames: ', uid)
					self.send_frame(frame)
				self._sent_unconfirmed_frame_lock.release()

	def _event_socket_write(self, sock, mask):
		q = self._queue_write
		while self._is_running:
			frame = q.get()
			if 'msg_id' in frame.content:
				self._sent_unconfirmed_frame_lock.acquire()
				self._sent_unconfirmed_frames[frame.content['msg_id']] = frame
				self._sent_unconfirmed_frame_lock.release()
			try:
				self.sock.send(bytes(frame))
			except OSError as e:
				pass
			q.task_done()

	def send_frame(self, frame):
		self._queue_write.put(frame)

	def reconnect_if_needed(self, sock, e = None):
		print(f'Need to reconnect: {e}')
		i = 5
		while i and not self._is_socket_connected(sock):
			print(f'Short sleep of 5 before reconnect attempt.')
			sleep(5)
			print(f'Reconnecting attempt: {i}')
			sock.close()
			sock.connect((self.endpoint, self.port))

	def _is_socket_connected(self, sock):
		try:
			sock.send(0)
		except:
			return False
		return True

	def _event_socket_read(self, sock, mask):
		try:
			self._frame_form = self._frame_form if self._frame_form and not self._frame_form.is_construction_completed() else SimpleFrame()
			if self._frame_form.reconnect_cb is None:
				self._frame_form.reconnect_cb = self.reconnect_if_needed

			if self._frame_form.from_socket(sock) is None:
				self._disconnected(sock)
		except SSLWantReadError as e:
			pass
		except ConnectionResetError as e:
			self._disconnected(sock)

		if self._frame_form.is_construction_completed():
			frame = self._frame_form
			self._frame_form = None
			self._action_threads.append(
				start_new_thread(self.frame_received, (frame, ))
			)

	def frame_received(self, frame: SimpleFrame):
		self._sent_unconfirmed_frame_lock.acquire()

		data = frame.content

		if 'confirm_for' in data:
			uid = data["confirm_for"]

			if uid in self._sent_unconfirmed_frames:
				print(f'Received confirmation for: {uid}')
				del self._sent_unconfirmed_frames[uid]
			else:
				print(f'Received ORPHANED confirmation for: {uid}. Skipping.')

		self._sent_unconfirmed_frame_lock.release()

		if 'action' in data:
			self.confirm_frame(data['msg_id'])
			self.remote.receive_action(frame)

		if 'return' in data:
			self.confirm_frame(data['msg_id'])
			self.remote.receive_response(frame)

	def confirm_frame(self, uid):
		self.send_frame(SimpleFrame({'confirm_for': uid}))

	def _disconnected(self, sock):
		print(f'Connection is closed.')
		self._is_running = False
		self.sel.unregister(sock)
		sock.close()
