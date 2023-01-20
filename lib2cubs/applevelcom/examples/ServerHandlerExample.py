from datetime import datetime
from time import sleep

from lib2cubs.applevelcom.basic import action
from lib2cubs.applevelcom.basic.HandlerBase import HandlerBase
from lib2cubs.applevelcom.basic.RemoteForServer import RemoteForServer


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
		while 1000:
			sleep(1)
		# i = 0
		# while i < 10000:
		# 	i += 1
		# 	remote.get_time()
	# 	sleep(5)
	# 	print(f"Requesting client's time: {remote.get_time()}")
	# 	sleep(5)
	# 	print(f"Requesting client's time: {remote.get_time()}")
	#
	# 	sleep(5)
	# 	print(f"Requesting client's time: {remote.get_time()}")
	#
	# 	print('TEST')
	# 	# Be careful returning "False" here, this will terminate connection before client might send something!
	# 	# return False
	# 	while not self.is_finished
