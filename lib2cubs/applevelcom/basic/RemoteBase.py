import uuid
from copy import copy
from socket import socket
from threading import Lock
from time import sleep

from lib2cubs.lowlevelcom.basic import SimpleFrame

# from lib2cubs.applevelcom.basic import ClientBase


class RemoteBase:

	sock: socket = None
	app = None

	_calls_locks = dict()
	_resp_data = dict()

	def __init__(self, sock, app):
		self.sock = sock
		self.app = app

	def rfc(self, name: str, *args, **kwargs):
		data = {
			'action': name,
			'args': [*args],
			'kwargs': {**kwargs},
			'msg_id': str(uuid.uuid1())
		}

		self._calls_locks[data['msg_id']] = lck = Lock()
		self._resp_data[data['msg_id']] = None
		self.app.send_frame(SimpleFrame(data))
		lck.acquire()
		lck.acquire()
		res = self._resp_data[data['msg_id']]
		lck.release()

		del self._calls_locks[data['msg_id']]
		del self._resp_data[data['msg_id']]

		return res

	def resp(self, frame: SimpleFrame, res: any):
		data = {
			'return': res,
			'for_id': frame.content['msg_id'],
			'msg_id': str(uuid.uuid1())
		}
		self.app.send_frame(SimpleFrame(data))

	def receive_response(self, frame):
		# print(f'Received response {frame}')
		data = frame.content
		if data['for_id'] not in self._resp_data:
			print(f'Orphaned response {data}')
			return
		self._resp_data[data['for_id']] = data['return']
		self._calls_locks[data['for_id']].release()

	def receive_action(self, frame):
		# print(f'Received action {frame}')
		data = frame.content
		args = data['args']
		kwargs = data['kwargs']
		res = getattr(self.app, data['action'])(*args, **kwargs)
		self.resp(frame, res)

	def __getattr__(self, item):
		def wrapper(*args, **kwargs):
			return self.rfc(item, *args, **kwargs)
		return wrapper
