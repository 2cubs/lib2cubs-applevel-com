#!/bin/env python

from lib2cubs.applevelcom.examples import ExampleClient


def my_event_cb(service, status):
	print(f'Event of my event cb!!! service: {service}; status: {status}')


app = ExampleClient.get_instance()
app.subscribe_to_event(ExampleClient.EVENT_SERVICE_STATUS_CHANGED, my_event_cb)
remote = app.remote

print('Checking auth method.')
res = remote.auth('ivan', 'pppaaassswwwooorrrddd')
print(f'Is auth successful: {res}')
print('Sleeping 5 seconds')
# sleep(5)
print('Requesting uname.')
res = remote.uname()
print(f'Received uname: {res}')
print('Requesting hostname.')
res = remote.hostname()
print(f'Received hostname: {res}')
