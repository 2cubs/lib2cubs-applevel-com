#!/bin/env python
from lib2cubs.applevelcom.basic import ServerBase
from lib2cubs.applevelcom.examples import ExampleHandler

ServerBase.get_instance(handler_class=ExampleHandler).start_app()
