

class Action:

	_name = None

	def __call__(self, *args, **kwargs):
		name = None

		def wrapper(func, *sargs, **skwargs):
			return func

		if not args or isinstance(args[0], str):
			name = args[0] if args else None
			def prepare(func, *sargs, **skwargs):
				func.action_name = name or func.__name__
				func.callback_ref = func
				func.is_action = True
				return func
			return prepare

		wrapper.action_name = args[0].__name__
		wrapper.callback_ref = args[0]
		wrapper.is_action = True

		return wrapper
