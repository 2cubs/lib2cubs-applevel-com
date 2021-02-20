#!/bin/env python
from os.path import join, dirname, abspath
from time import sleep

from lib2cubs.applevelcom.examples import ExampleClient


def my_event_cb(service, status):
	print(f'Event of my event cb!!! service: {service}; status: {status}')


ssl_path = join(dirname(abspath(__file__)), 'ssl_d')

# Building a cred-bundle is just concatenating keys and certs to one .pem file
# cat client.crt client.key server.crt > cred-bundle-client.pem
instance_params = {
	'host': '2cubs-server',
	'ssl_cred_bundle': join(ssl_path, 'cred-bundle-client.pem'),
}

app: ExampleClient = ExampleClient.get_instance(**instance_params)
app.subscribe_to_event(ExampleClient.EVENT_SERVICE_STATUS_CHANGED, my_event_cb)

print(f'IS CONNECTED?: {app.is_connected}')
sleep(2)

remote = app.remote

print(f'IS CONNECTED?: {app.is_connected}')
sleep(2)

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

# print(f'Disconnecting now')

# app.disconnect()

print(f'Sleeping 5 sec')
print(f'Reconnecting again')

app.disconnect()

print(f'IS CONNECTED?: {app.is_connected}')
sleep(2)

app.connect()
# remote = app.remote

print(f'IS CONNECTED?: {app.is_connected}')

res = remote.auth('ivan', 'pppaaassswwwooorrrddd')
print(f'Is auth successful: {res}')
print('Requesting uname again.')
res = remote.uname()
print(f'Received uname again: {res}')
