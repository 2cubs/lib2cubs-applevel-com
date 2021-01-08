from lib2cubs.applevelcom.basic import ServerBase
from lib2cubs.applevelcom.examples import ExampleServingClient


class ExampleServer(ServerBase):

	@classmethod
	def get_serving_client_class(cls):
		return ExampleServingClient
