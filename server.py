import logging
from os.path import dirname, abspath

from lib2cubs.lowlevelcom import Utils

from lib2cubs.applevelcom.basic.ServerBase import ServerBase
from lib2cubs.applevelcom.examples.ServerHandlerExample import ServerHandlerExample


# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


Utils.setup(dirname(abspath(__file__)))


host = 'localhost'
port = 60009


if __name__ == '__main__':
    try:
        server = ServerBase('cred-bundle-client.pem', host, port, handler_class=ServerHandlerExample,
                            # )
                            disable_ssl=True, confirm_disabling_of_ssl=True)
        server.start()
        server.join()
    except (KeyboardInterrupt, SystemExit):
        print('## [ctrl+c] pressed')
        print('## Out of the app.')
        server.is_running = False
