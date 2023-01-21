import logging
from threading import Thread

from lib2cubs.lowlevelcom import GenericConnection

from lib2cubs.applevelcom.transport import SimpleFrame
from .internals import Remote, Promise, action, pre


class AppLevelSkeletonBase:

	connection: GenericConnection = None
	_actions: dict = None
	_preprocessors: dict = None
	_promises = None
	_invoked_action_threads: list = None
	_remote = None

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
		logging.debug(f'<< Received frame {frame.uid} with content {frame.content}')

		if frame.content["type"] == 'action-call':
			action_to_call = frame.content['action'] if 'action' in frame.content else None
			if not action_to_call or action_to_call not in self._actions:
				logging.error(f'ERROR: No such action: {action_to_call}')
			else:
				args = frame.content['args']
				kwargs = frame.content['kwargs']

				action_callable = self._actions.get(action_to_call)

				is_async = bool(frame.content.get('is_async', False))

				t = Thread(target=self._invoked_action, args=(action_callable, action_to_call, args, kwargs, frame.uid, is_async))
				self._invoked_action_threads.append(t)
				t.start()

		if frame.content['type'] == 'action-return':
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
		self._preprocessors = {}
		self._promises = {}
		self._invoked_action_threads = []
		self._remote = Remote(self)

		for item in dir(self):
			func = getattr(self, item)
			if hasattr(func, 'is_action') and func.is_action:
				action_name = getattr(func, 'action_name')
				self._actions[action_name] = getattr(func, 'callback_ref') or func
			if hasattr(func, 'is_preprocessor') and func.is_preprocessor:
				action_name = getattr(func, 'action_name')
				self._preprocessors[action_name] = getattr(func, 'callback_ref') or func

	def init(self):
		pass

	def _send_back_return_data(self, for_uid, data: any, action_name: str):
		self.connection.send(SimpleFrame({
			'type': 'action-return',
			'action': action_name,
			'for_uid': for_uid,
			'data': data,
		}))

	def _invoked_action(self, act: callable, action_name: str, args, kwargs, for_uid, is_async, is_no_return: bool = False):
		res = act(self, self._remote, *args, **kwargs)
		if not is_no_return:
			self._send_back_return_data(for_uid, res, action_name)

	def _call_return(self, frame: SimpleFrame):
		content = frame.content
		if 'for_uid' in content:
			for_uid = content['for_uid']
			data = content['data']
			if content['action'] in self._preprocessors:
				# NOTE  Pre-processing of received data happens here
				act = self._preprocessors[content['action']]
				data = act(self, data)
			if for_uid in self._promises:
				promise: Promise = self._promises[for_uid]
				promise.set_result(data)
				del self._promises[for_uid]

	def call_action(self, action_name, args=(), kwargs=None, is_async: bool = False) -> Promise or any:
		if kwargs is None:
			kwargs = {}
		message = {
			'type': 'action-call',
			'action': action_name,
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
		self.connection.disconnect()

	@pre('i_am')
	def pre_i_am(self, data: dict):
		data['_ip'] = self.connection.host
		data['_port'] = self.connection.port
		logging.debug('Preprocessing of i_am() action result of remote, final data: %s', data)
		return data

	@property
	def who_am_i(self):
		return {

		}

	@action
	def i_am(self, remote: Remote):
		return self.who_am_i
