from _thread import start_new_thread
from datetime import datetime
from queue import Queue
from selectors import EVENT_READ, EVENT_WRITE
from socket import socket
from ssl import SSLWantReadError

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
		CommunicationEngine.secure_client(self._exec_app, self.endpoint, self.port)

	def before_app(self, sock: socket = None):
		super(ClientBase, self).before_app(sock)
		self._queue_write = Queue()
		self.sel.register(self.sock, EVENT_READ, self._event_socket_read)
		# TODO Change the threads invocation
		start_new_thread(self._t_sel_events_loop, ('selectors event loop thread', ))
		start_new_thread(self._event_socket_write, (sock, EVENT_WRITE))

	def _event_socket_write(self, sock, mask):
		q = self._queue_write
		while self._is_running:
			frame = q.get()
			# print(f'WRITE: Got a frame to write')
			try:
				self.sock.send(bytes(frame))
				# print(f'Frame is sent:', frame)
			except OSError as e:
				pass
			q.task_done()
			# print('Task is done')

	def send_frame(self, frame):
		self._queue_write.put(frame)

	def _event_socket_read(self, sock, mask):
		n = datetime.now()
		# print(f'data read {n}')
		try:
			self._frame_form = self._frame_form if self._frame_form and not self._frame_form.is_construction_completed() else SimpleFrame()

			if self._frame_form.from_socket(sock) is None:
				self._disconnected(sock)
			# print(f'TEST: {self._frame_form}')
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
		data = frame.content
		# print(f'Frame received with data: {data}')
		if 'action' in data:
			self.remote.receive_action(frame)

		if 'return' in data:
			self.remote.receive_response(frame)

	def _disconnected(self, sock):
		print(f'Connection is closed.')
		self._is_running = False
		self.sel.unregister(sock)
		sock.close()
