import uuid
from threading import Lock

from lib2cubs.applevelcom.transport import SimpleFrame


class RemoteBase:

	_app = None

	_calls_locks = dict()
	_resp_data = dict()

	def __init__(self, app):
		self._app = app

	def rfc(self, name: str, *args, **kwargs):
		# print(f'Making Action request: {name}')
		data = {
			'action': name,
			'args': [*args],
			'kwargs': {**kwargs},
			'msg_id': str(uuid.uuid1())
		}

		self._calls_locks[data['msg_id']] = lck = Lock()
		self._resp_data[data['msg_id']] = None
		self._app.send(SimpleFrame(data))
		lck.acquire()
		lck.acquire()
		res = self._resp_data[data['msg_id']]
		lck.release()

		del self._calls_locks[data['msg_id']]
		del self._resp_data[data['msg_id']]
		# print(f'Finishing Action request: {name}')

		return res

	def resp(self, frame: SimpleFrame, res: any):
		# print(f'Making Action resp: {frame}')
		data = {
			'return': res,
			'for_id': frame.content['msg_id'],
			'msg_id': str(uuid.uuid1())
		}
		self._app.send(SimpleFrame(data))
		# print(f'Finishing Action resp: {frame}')

	def receive_response(self, frame):
		# print(f'Received response {frame}')
		data = frame.content
		if data['for_id'] not in self._resp_data:
			print(f'Orphaned response {data}')
			return
		self._resp_data[data['for_id']] = data['return']
		if self._calls_locks[data['for_id']].locked():
			self._calls_locks[data['for_id']].release()

	def receive_action(self, frame):
		# print(f'Received action {frame}')
		data = frame.content
		args = data['args']
		kwargs = data['kwargs']
		res = getattr(self._app, data['action'])(*args, **kwargs)
		self.resp(frame, res)

	def __getattr__(self, item):
		def wrapper(*args, **kwargs):
			return self.rfc(item, *args, **kwargs)
		return wrapper
