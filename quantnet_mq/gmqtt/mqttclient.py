from gmqtt import Client
from gmqtt.mqtt.constants import PubRecReasonCode
from quantnet_mq import MQTTClientInterface

# used in rpcserver.py
PubRecReasonCode


class MQTTClient(MQTTClientInterface, Client):
    def __init__(self, client_id, clean_session=True, optimistic_acknowledgement=True,
                 will_message=None, **kwargs):
        super(MQTTClient, self).__init__(client_id, clean_session, optimistic_acknowledgement, will_message, **kwargs)

    def topic_match(self, sub, topic):
        """ check if topic start with sub """
        return True if sub in topic else False

    def topic_tokenise(self, topic):
        """ TODO: break the topic into token array """
        return topic.split('/')

    def topic_wildcard(self, topic):
        """ """
        return topic.split('/')[0]+'/+'

    def set_will(self, topic, msg, qos, ratain):
        """ TODO: set the will message """
        pass

    def set_tls_psk(self, id, psk):
        """ TODO: set the psk """
        pass

    def set_ca(self, capath):
        """ TODO setup the ca """
        pass
