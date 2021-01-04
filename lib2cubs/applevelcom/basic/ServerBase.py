from lib2cubs.lowlevelcom import CommunicationEngine

from lib2cubs.applevelcom.basic import AppBase


class ServerBase(AppBase):

	def __init__(self, endpoint: str, port: int):
		self.endpoint = endpoint
		self.port = port

	def run(self):
		CommunicationEngine.secure_server(self._exec_app, self.endpoint, self.port)
