import logging
from threading import Lock, Condition

from lib2cubs.applevelcom.transport import SimpleFrame


class Promise:

	_ref_obj = None
	_frame: SimpleFrame = None
	_is_result_set: bool = False
	_result: any = None
	_is_sent: bool = False
	_t_condition: Condition = None

	def release_lock(self):
		try:
			self._t_condition.release()
		except RuntimeError:
			pass

	def __init__(self, ref_obj, frame: SimpleFrame):
		from lib2cubs.applevelcom.basic.AppLevelSkeletonBase import AppLevelSkeletonBase
		self._ref_obj: AppLevelSkeletonBase = ref_obj
		self._frame = frame
		self._t_condition = Condition()

	def send(self):
		if not self._is_sent:
			self._ref_obj.connection.send(self._frame)
		else:
			logging.warning('Promise sending method can be ran just once! Additional attempt is ignored')

	def set_result(self, result: any):
		logging.debug('set_result %s', self._frame.uid)
		if not self._is_result_set:
			logging.debug('set_result. not set yet %s', self._frame.uid)

			with self._t_condition:
				logging.debug('set_result. condition passed %s', self._frame.uid)

				self._result = result
				# print(f'set_result. result set {self._frame.uid}')

				self._is_result_set = True
				# print(f'set_result. result marked {self._frame.uid}')

				self._t_condition.notify_all()
				# print(f'set_result. condition notified {self._frame.uid}')

		else:
			logging.warning("Promise's result could be set only once! Additional attempt is ignored")

	def get_result(self):
		if not self._is_result_set:
			self.send()

			if self._ref_obj.connection.is_connected:
				# print(f'Waiting for result for {self._frame.uid}')
				with self._t_condition:
					# print(f'with {self._frame.uid}')

					while not self._is_result_set:
						# print(f'whiling {self._frame.uid}')
						self._t_condition.wait()

		return self._result

