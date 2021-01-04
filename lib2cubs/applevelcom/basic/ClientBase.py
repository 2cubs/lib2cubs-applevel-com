from lib2cubs.lowlevelcom import CommunicationEngine

from lib2cubs.applevelcom.basic import AppBase


class ClientBase(AppBase):

	def __init__(self, endpoint: str, port: int):
		self.endpoint = endpoint
		self.port = port

	def run(self):
		CommunicationEngine.secure_client(self._exec_app, self.endpoint, self.port)
