import asyncio
import logging
import uuid
import json
import uvloop
from .gmqtt.mqttclient import MQTTClient


logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class MsgClient:
    def __init__(self, cid=None, **kwargs):
        self._cid = cid or uuid.uuid4().hex
        self._queue = None

        self._mqtt_client_username = kwargs.get("username", "")
        self._mqtt_client_password = kwargs.get("password", "")
        self._mqtt_broker_host = kwargs.get("host", "127.0.0.1")
        self._mqtt_broker_port = kwargs.get("port", 1883)
        self._mqttclient = None
        self._on_msg_callback = None

    def on_connect(self, client, flags, rc, properties):
        logger.info("Connected: %s", self._cid)

    def on_disconnect(self, client, packet, exc=None):
        logger.info("Disconnected")

    async def _start_mqttclient(self):
        """
        start the mqtt client
        """
        self._mqttclient = MQTTClient(f"quantnet-msgclient-{self._cid}")

        self._mqttclient.on_connect = self.on_connect
        self._mqttclient.on_disconnect = self.on_disconnect
        self._mqttclient.set_auth_credentials(self._mqtt_client_username, self._mqtt_client_password)
        await self._mqttclient.connect(host=self._mqtt_broker_host, port=self._mqtt_broker_port)

    def _stop_mqttclient(self):
        pass

    async def start(self):
        await self._start_mqttclient()

    async def stop(self):
        self._stop_mqttclient()

    async def publish(self, topic, payload):
        self._mqttclient.publish(topic, json.dumps(payload), 1, False)
