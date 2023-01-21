from lib2cubs.applevelcom.basic.internals.Remote import Remote


class RemoteForClient(Remote):

	def get_time(self): ...

	def get_info(self): ...

	def calc_sum(self, *args): ...
