from lib2cubs.applevelcom.basic import RemoteBase


class RemoteForClient(RemoteBase):

	def get_time(self): ...

	def get_info(self): ...

	def calc_sum(self, *args): ...
