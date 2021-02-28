#!/bin/env python
from datetime import datetime
from os.path import join, dirname, abspath

from lib2cubs.applevelcom.examples import ExampleClient


# Method that is attached to the event EVENT_SERVICE_STATUS_CHANGED
def my_event_cb(service, config):
	print(f'Event of my event cb!!! service: {service}; config: {config}')


# Method that invoked on EVENT_CONNECTION_DISCONNECTED (when disconnection is happening)
def oh_my_i_am_disconnected():
	print(f'I\'ve got disconnected just now! {datetime.now()}')


# Building a cred-bundle is just concatenating keys and certs to one .pem file
# cat client.crt client.key server.crt > cred-bundle-client.pem
connection_params = {
	'ssl_cred_bundle': join(dirname(abspath(__file__)), 'ssl_d', 'cred-bundle-client.pem'),
	'server_hostname': '2cubs-server'
}

# Creating app
app: ExampleClient = ExampleClient.get_instance(**connection_params)

# Subscribing to events of the app
app.subscribe_to_event(ExampleClient.EVENT_SERVICE_STATUS_CHANGED, my_event_cb)
app.subscribe_to_event(ExampleClient.EVENT_CONNECTION_DISCONNECTED, oh_my_i_am_disconnected)

# Running remote method "auth". It does logging in and returns result of it as True or False
print(f'Doing auth. Getting auth status: {app.remote.auth("ivan", "pppaaassswwwooorrrddd")}')

# Getting result from the remote "uname" method
print(f'Getting uname: {app.remote.uname()}')

# Getting result from the remote "hostname" method
print(f'Getting hostname: {app.remote.hostname()}')

# Disconnecting
app.disconnect()

# Checking the connection flag/status
print(f'Is connected: {app.is_connected}. Sleeping 5 sec after disconnect() invocation')


print(f'Connecting with other connection data...')

# Here you can use different connection data, or omit any params to connect with previous connection data
app.connect(host='2cubs-server', ssl_cred_bundle=connection_params['ssl_cred_bundle'])

# Checking the connection flag/status
print(f'Is connected: {app.is_connected}')

# As usually checking the authentication (this method perform auth, and if successful, then returns True)
if app.remote.auth('ivan', 'pppaaassswwwooorrrddd'):
	# Here we are being authenticated, so we can perform something
	print('## We got authenticated successfully.')

	# Checking the server time
	print(f'Checking current server time: {app.remote.server_time()}')
else:
	# Authentication failed
	print('## Authentication failed.')
	exit(1)
