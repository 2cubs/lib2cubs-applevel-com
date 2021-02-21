from datetime import datetime
from os import uname
from platform import node
from time import sleep

from lib2cubs.applevelcom.basic import HandlerBase, action, Remote


class ExampleHandler(HandlerBase):

	_user_name: str = None
	_user_roles: list = None

	def init(self):
		self._user_roles = list()

	def is_authorized(self):
		return bool(self._user_name)

	def app(self, remote: Remote):
		print('The Handler has started. Infinite loop is running')
		while True:
			# Waiting for events
			sleep(10)
			# remote.event_service_status_changed('SeRvIcE+NaMe', f'BooBooBoo {datetime.now()}')

	# All of the bellow actions are dummies.

	@action
	def auth(self, user: str, password: str):
		"""
		It's not done. It's just a dummy action right now.
		:param user:
		:param password:
		:return:
		"""
		print(f'Authorization is requested for {user}')
		# sleep(5)
		fake_creds = {'dan': 'hhhh', 'stan': 'VvVv', 'ivan': 'pppaaassswwwooorrrddd', 'bogdan': 'KkKKk'}
		if user in fake_creds and password == fake_creds[user]:
			self._user_name = user
			self._user_roles.append('user')

		res = self.is_authorized()
		if res:
			print(f'The authorization was successful. The roles: {self._user_roles}')
		return res

	@action
	def uname(self):
		print('Server\'s uname action is requested. Waiting 5 sec and returning result.')
		# sleep(5)
		return uname()

	@action
	def hostname(self):
		print('Server\'s hostname action is requested. Waiting 5 sec and returning result.')
		# sleep(5)
		return node()

	@action
	def server_time(self):
		print('Server\'s time action is requested.')
		return str(datetime.now())
