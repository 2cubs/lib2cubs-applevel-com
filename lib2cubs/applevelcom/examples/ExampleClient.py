from time import sleep

from lib2cubs.applevelcom.basic import ClientBase, Remote


class ExampleClient(ClientBase):

	def app(self, remote: Remote):
		# TODO Possibly some problems with delays at startup (SSL). Investigate if needed
		# TODO Inconsistencies between runs. Sometimes server is missing frames (Investigate)
		print('Checking auth method.')
		res = remote.auth('ivan', 'pppaaassswwwooorrrddd')
		print(f'Is auth successful: {res}')
		print('Sleeping 5 seconds')
		sleep(5)
		print('Requesting uname.')
		res = remote.uname()
		print(f'Received uname: {res}')
		print('Requesting hostname.')
		res = remote.hostname()
		print(f'Received hostname: {res}')
