import logging
from os.path import dirname, abspath
from time import sleep

from lib2cubs.lowlevelcom import Utils

from lib2cubs.applevelcom.examples.ClientExample import ClientExample


logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)


Utils.setup(dirname(abspath(__file__)))


host = 'localhost'
port = 60009
retry_waiting_time = 10

if __name__ == '__main__':
    try:
        # is_retry = True
        # while is_retry:
        #     try:
        app = ClientExample('cred-bundle-client.pem', host, port,
                            # )
                            disable_ssl=True, confirm_disabling_of_ssl=True)
        app.start()
        app.join()
        # is_retry = False
        # except ConnectionRefusedError:
        #     print("Can't connect to server-side, server-side is most likely unavailable")
        #     print(f"Waiting {retry_waiting_time} sec. before next retry")
        #     sleep(retry_waiting_time)

    except (KeyboardInterrupt, SystemExit):
        print('## [ctrl+c] pressed')
        print('## Out of the app.')
        app.is_running = False

        if app.connection:
            app.connection.disconnect()
            print('## Waiting for all sub-routines to finish up.')
