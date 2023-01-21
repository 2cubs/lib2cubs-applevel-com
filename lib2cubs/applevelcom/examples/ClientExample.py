from datetime import datetime
from time import sleep

from lib2cubs.applevelcom.basic import ClientBase
from lib2cubs.applevelcom.basic.internals import action, RemoteForClient


class ClientExample(ClientBase):

	_actions = None

	@action
	def get_time(self, remote: RemoteForClient):
		res = str(datetime.now())
		return res

	def main(self, remote: RemoteForClient):
		print('Running main')

		print('Sleeping 5')
		sleep(5)

		server_iam = remote.i_am()

		print(f"Server is: {server_iam}")

		print('Sleeping 5')
		sleep(5)
