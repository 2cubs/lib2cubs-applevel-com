

class RemoteBase:

	_is_async: bool = False
	_proxied_obj = None

	def __init__(self, proxied_obj, is_async: bool = False):
		from lib2cubs.applevelcom.basic.AppLevelSkeletonBase import AppLevelSkeletonBase

		self._proxied_obj: AppLevelSkeletonBase = proxied_obj
		self._is_async = is_async

	def __getattr__(self, item):
		def wrapper(*args, **kwargs):
			return self._proxied_obj.call_action(item, args, kwargs, self._is_async)

		return wrapper

	def asynced(self) -> 'RemoteBase':
		if self._is_async:
			return self
		return self.__class__(self._proxied_obj, True)
