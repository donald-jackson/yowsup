

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity

import urllib
import urllib2
import threading
import logging
logger = logging.getLogger(__name__)


class ForwarderLayer(YowInterfaceLayer):

    url = ''
    our_number = ''

    def __init__(self):
        super(ForwarderLayer, self).__init__()
        self.ackQueue = []
        self.lock = threading.Condition()

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        text = ''
        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
            text = messageProtocolEntity.getBody()
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)
            text = 'Rich media'
        else:
            text = messageProtocolEntity.getType()

        print("Our url is %s" % self.url)

        self.lock.acquire()

        fullUrl = self.url

        params = urllib.urlencode({'to': self.our_number, 'from': messageProtocolEntity.getFrom(), 'message': text, 'mcc': '', 'mnc': ''})

        response = urllib2.urlopen(fullUrl + "&%s" % params)
        html = response.read()
        messageEntity = TextMessageProtocolEntity(html, to=messageProtocolEntity.getFrom())


        self.ackQueue.append(messageEntity.getId())
        self.toLower(messageEntity)

        # self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))

        self.lock.release()


    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        # just print info
        print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))


    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        self.lock.acquire()
        #if the id match the id in ackQueue, then pop the id of the message out
        if entity.getId() in self.ackQueue:
            self.ackQueue.pop(self.ackQueue.index(entity.getId()))

        self.lock.release()