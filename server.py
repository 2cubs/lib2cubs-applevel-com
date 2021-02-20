#!/bin/env python
from os.path import join, dirname, abspath

from lib2cubs.applevelcom.basic import ServerBase
from lib2cubs.applevelcom.examples import ExampleHandler

ssl_path = join(dirname(abspath(__file__)), 'ssl_d')

instance_params = {
	'client_crt': join(ssl_path, 'client.crt'),
	'server_key': join(ssl_path, 'server.key'),
	'server_crt': join(ssl_path, 'server.crt'),
	'server_hostname': '2cubs-server',
	'handler_class': ExampleHandler
}

ServerBase.get_instance(**instance_params).start_app()
