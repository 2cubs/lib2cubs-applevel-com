# Application Level communication library
The main purpose is to implement the normal RFC (RPC) calls over the lib2cubs low-level lib communication.
The current library should provide the way to do remote calls on the side (full-duplex).

Some additional abstractions would be added like events, but in fact it would be just remote calls from server to client.

The modular dividing is being considered, but currently only 1 socket/port/app is supported. At some point, the module/plugin/sub-apps
would be implemented.

Currently version is just a prototype and will be reworked (more than 50% of the code might be reorganized). The logic 
though persist.

**Important:** Until the first major version, all the methods might be renamed.

## How to try it
Keep in mind that the code is unfinished prototype. Some of the messages might be missing from run to run. This will be 
fixed later. For now consider re-run the apps to workaround the missing messages from any sides.

