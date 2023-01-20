import logging
from threading import Thread

from lib2cubs.lowlevelcom import GenericConnection

from lib2cubs.applevelcom.basic.Promise import Promise
from lib2cubs.applevelcom.basic.Remote import Remote
from lib2cubs.applevelcom.transport import SimpleFrame


class AppLevelSkeletonBase:

	connection: GenericConnection = None
	_actions: dict = None
	_promises = None

	def events_subscription(self):
		return {
			GenericConnection.EVENT_CONNECTED: self.event_connected,
			GenericConnection.EVENT_DISCONNECTED: self.event_disconnected,
			GenericConnection.EVENT_READING: self.event_reading,
			GenericConnection.EVENT_BEFORE_RECONNECT: self.event_before_reconnect,
			GenericConnection.EVENT_AFTER_RECONNECT: self.event_after_reconnect,
			GenericConnection.EVENT_WRITING: self.event_writing,
		}

	def event_before_reconnect(self, event, connection):
		pass

	def event_after_reconnect(self, event, connection):
		pass

	def event_writing(self, event, data, connection):
		logging.debug(f'>> Sending frame {data.uid} with payload {data.content}')

	def event_reading(self, event, frame, connection):
		# frame = SimpleFrame.parse(data)

		logging.debug(f'<< Received frame {frame.uid} with content {frame.content}')

		if frame.content["type"] == 'action-call':
			action_to_call = frame.content['action'] if 'action' in frame.content else None
			if not action_to_call or action_to_call not in self._actions:
				# raise Exception(f'No such action: {action_to_call}')
				print(f'ERROR: No such action: {action_to_call}')
			else:
				args = frame.content['args']
				kwargs = frame.content['kwargs']

				action_callable = self._actions[action_to_call]

				is_async = bool(frame.content.get('is_async', False))

				t = Thread(target=self._invoked_action, args=(action_callable, args, kwargs, frame.uid, is_async))
				self._invoked_action_threads.append(t)
				t.start()

		if frame.content['type'] == 'action-return':
			# print(f'AR: {frame.content}')
			self._call_return(frame)

	def event_connected(self, event, connection):
		pass

	def event_disconnected(self, event, connection):
		logging.debug('Remote side has disconnected')
		for uid, promise in self._promises.items():
			promise: Promise
			promise.release_lock()
			# TODO  In case of reconnect will be a problem!!!

	def main(self, remote: Remote):
		return True

	@property
	def is_finished(self):
		return not self.connection.is_connected

	def _pre_init(self):
		self._actions = {}
		# self._calls_locks = {}
		# self._return_data = {}
		self._promises = {}
		self._invoked_action_threads = []
		self._remote = Remote(self)

		for item in dir(self):
			func = getattr(self, item)
			if hasattr(func, 'is_action'):
				action_name = getattr(func, 'action_name')
				self._actions[action_name] = getattr(func, 'callback_ref') or func

	def init(self):
		pass

	_invoked_action_threads: list = None

	def _send_back_return_data(self, for_uid, data: any):
		self.connection.send(SimpleFrame({
			'type': 'action-return',
			'for_uid': for_uid,
			'data': data,
		}))

	def _invoked_action(self, action: callable, args, kwargs, for_uid, is_async, is_no_return: bool = False):
		res = action(self, self._remote, *args, **kwargs)
		if not is_no_return:
			self._send_back_return_data(for_uid, res)

	def _call_return(self, frame: SimpleFrame):
		# self._promises[frame.uid]
		if 'for_uid' in frame.content:
			for_uid = frame.content['for_uid']
			r = for_uid in self._promises
			# print(f'received frame for {for_uid}, is available: {r}')
			if for_uid in self._promises:
				promise: Promise = self._promises[for_uid]
				# print(f'setting result... for {for_uid}')
				promise.set_result(frame.content['data'])
				# print(f'result set for {for_uid}')
				del self._promises[for_uid]

	def call_action(self, action, args=(), kwargs=None, is_async: bool = False) -> Promise or any:
		if kwargs is None:
			kwargs = {}
		message = {
			'type': 'action-call',
			'action': action,
			'args': args,
			'kwargs': kwargs,
			'is_async': is_async,
		}
		frame = SimpleFrame(message)

		self._promises[frame.uid] = promise = Promise(self, frame)

		if is_async:
			promise.send()
			# print('Promise sent...')
			return promise

		# Sending frame in synced way is happening inside of get_result()
		return promise.get_result()

	def stop_main(self):
		logging.debug('StopMain is running')

		self.connection.disconnect()
		logging.debug('StopMain is finished')
