from datetime import datetime
from time import sleep

from lib2cubs.applevelcom.basic import ClientBase, action, Remote
from lib2cubs.applevelcom.basic.Promise import Promise
from lib2cubs.applevelcom.basic.RemoteForClient import RemoteForClient


class ClientExample(ClientBase):

	_actions = None

	@action
	def get_time(self, remote: Remote):
		res = str(datetime.now())
		return res

	def main(self, remote: RemoteForClient):
		print('Running main')
		a: Promise = remote.asynced().get_info()
		b: Promise = remote.asynced().calc_sum(200, 203, 33, 33, 33)
		c: Promise = remote.asynced().get_time()

		i = 0
		while i < 10:
			i += 1
			remote.asynced().get_info()

		print('Sleeping 1')
		sleep(1)

		print(f'Server info: {a.get_result()}')
		print(f'Server sum op: {b.get_result()}')
		print(f'Server time: {c.get_result()}')
		#
		# print(f'Server info: {remote.get_info()}')
		# print(f'Server sum op: {remote.calc_sum(200, 203, 33, 33, 33)}')
		# print(f'Server time: {remote.get_time()}')

		# TODO  Replace lock with the queue!!!

		# print('Sleeping 10')
		# sleep(10)
		print('Done!')
		sleep(5)
