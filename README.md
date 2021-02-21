# Application Level communication library

## Quick usage example

This is the sample code form [client.py](client.py)

**Important**: Keep in mind, that the code bellow dependent on the server side, and must be adjusted for your
server side functionality. But it shows the general usage.

```python
from datetime import datetime
from os.path import join, dirname, abspath

from lib2cubs.applevelcom.examples import ExampleClient


# Method that is attached to the event EVENT_SERVICE_STATUS_CHANGED
def my_event_cb(service, status):
	print(f'Event of my event cb!!! service: {service}; status: {status}')


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

```


## Description

The main purpose is to implement the normal RFC (RPC) calls over the lib2cubs low-level lib communication.
The current library should provide the way to do remote calls on the side (full-duplex).

Some additional abstractions would be added like events, but in fact it would be just remote calls from server to client.

The modular dividing is being considered, but currently only 1 socket/port/app is supported. At some point, the module/plugin/sub-apps
would be implemented.

Currently version is just a prototype and will be reworked (more than 50% of the code might be reorganized). The logic 
though persist.

**Important:** Until the first major version, all the methods might be renamed.
**Important:** None of the libraries code is adapted for windows yet. So please don't expect it running under win.

## How to try it
Keep in mind that the code is unfinished prototype. Some of the messages might be missing from run to run. This will be 
fixed later. For now consider re-run the apps to workaround the missing messages from any sides.

The script to get the code and relevant pip packages
```shell script
mkdir try-l2c-code;
cd try-l2c-code;
git clone -b development https://github.com/2cubs/lib2cubs-applevel-com.git;
python3 -m venv ./venv;
source venv/bin/activate;
cd lib2cubs-applevel-com;
pip install wheel;
pip install --upgrade git+https://github.com/2cubs/lib2cubs-lowlevel-com.git@development;
mkdir ssl;
```

Generating the Server key/cert pair
```shell script
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout ssl/server.key -out ssl/server.crt;
# use common name: 2cubs-server
```

Generating the Client key/cert pair
```shell script
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout ssl/client.key -out ssl/client.crt;
# use common name: 2cubs-server
```

Starting the server
```shell script
./server.py;
# In one tab
```

Starting the client
```shell script
./client.py;
# In another tab
```