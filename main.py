#!/bin/env python
from argparse import ArgumentParser, Namespace

from lib2cubs.lowlevelcom import CommunicationEngine

from lib2cubs.applevelcom.examples.ExampleClient import ExampleClient
from lib2cubs.applevelcom.examples.ExampleServer import ExampleServer


def setup_ssl_params(args):
	CommunicationEngine.ssl_client_key = args.client_key
	CommunicationEngine.ssl_client_cert = args.client_cert
	CommunicationEngine.ssl_server_key = args.server_key
	CommunicationEngine.ssl_server_cert = args.server_cert
	CommunicationEngine.ssl_server_hostname = args.verification_hostname


def do_server(args: Namespace):
	print(':: Server ::')
	# For server needed both certificates, but only server key
	setup_ssl_params(args)
	obj = ExampleServer(args.endpoint, args.port)
	obj.run()


def do_client(args: Namespace):
	print(':: Client ::')
	# For client needed both certificates, but only client key
	setup_ssl_params(args)
	obj = ExampleClient(args.endpoint, args.port)
	obj.run()


def do_help(args: Namespace):
	parser.print_help()


parser = ArgumentParser()
parser.set_defaults(func=do_help)

parent = ArgumentParser(add_help=False)

# To generate sample ssl keys/certs:
# openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
# openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
# Server generation common name (cn) should match, in the case of defaults to: 2cubs-server

parent.add_argument('--endpoint', default='127.0.0.1')
parent.add_argument('--port', default=60009)

parent.add_argument('--client-key', default='ssl/client.key')
parent.add_argument('--client-cert', default='ssl/client.crt')
parent.add_argument('--server-key', default='ssl/server.key')
parent.add_argument('--server-cert', default='ssl/server.crt')
parent.add_argument('--verification-hostname', default='2cubs-server')

sps = parser.add_subparsers(title='actions')

p = sps.add_parser('server', parents=[parent])
p.set_defaults(func=do_server)

p = sps.add_parser('client', parents=[parent])
p.set_defaults(func=do_client)

args = parser.parse_args()

args.func(args)
