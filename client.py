#!/bin/env python
from time import sleep

from lib2cubs.applevelcom.examples import ExampleClient

remote = ExampleClient.get_instance().remote

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
