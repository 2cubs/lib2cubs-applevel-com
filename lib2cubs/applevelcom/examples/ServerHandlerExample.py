from datetime import datetime

from lib2cubs.applevelcom.basic import HandlerBase
from lib2cubs.applevelcom.basic.internals import action, RemoteForServer


class ServerHandlerExample(HandlerBase):

	@action
	def get_time(self, remote: RemoteForServer):
		res = str(datetime.now())
		print(f'Time request received, res: {res}')
		return res

	@action
	def get_info(self, remote: RemoteForServer):
		res = "I'm a server handler"
		# print(f'Info request received, res: {res}')
		return res

	@action
	def calc_sum(self, remote: RemoteForServer, *args):
		res = sum(args)
		# print(f'Sum op received for : {args} res: {res}')
		return res

	def main(self, remote: RemoteForServer):
		print(f'>> Client ? has just connected')

		client_iam = remote.i_am()

		print(f"Client is: {client_iam}")
