from datetime import datetime

from lib2cubs.applevelcom.basic.internals.Remote import Remote


class RemoteForServer(Remote):

	def soft_shutdown_initiated(self, dt: datetime): ...
	def get_time(self): ...
