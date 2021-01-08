# Application Level communication library
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
./main.py server;
# In one tab
```

Starting the client
```shell script
./main.py client;
# In another tab
```