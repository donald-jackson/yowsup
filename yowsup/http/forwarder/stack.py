from yowsup.stacks import  YowStackBuilder
from .layer import ForwarderLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer

class YowsupForwarderStack(object):
    def __init__(self, credentials, encryptionEnabled = True, url = ''):
        stackBuilder = YowStackBuilder()

        ForwarderLayer.url = url
        ForwarderLayer.our_number = credentials[0]

        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(ForwarderLayer)\
            .build()

        self.stack.setCredentials(credentials)

    def start(self):
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            self.stack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)
