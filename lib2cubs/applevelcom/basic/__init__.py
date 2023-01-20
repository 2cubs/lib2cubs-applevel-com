from .Action import Action
from .RemoteBase import RemoteBase
from .Remote import Remote
from .AppBase import AppBase
from .ClientBase import ClientBase
# from .ServerBase import ServerBase
# from .HandlerBase import HandlerBase
#
# action = ClientBase.action_wrap

action = Action()

# def action(func):
# 	print(f'WRAPPED FUNC: {func} or {func.__name__} of {func.__class__.__name__}')
# 	print(f'              {func.__class__.__self__}')
# 	exit(3)
