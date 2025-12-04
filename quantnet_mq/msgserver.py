import asyncio
import logging
import uuid
import json
import uvloop
from typing import Callable
from .gmqtt.mqttclient import MQTTClient


logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TopicHandler:
    def __init__(self, topic, cb):
        self._topic = topic
        self._cb = cb

    @property
    def topic(self):
        return self._topic

    @property
    def cb(self):
        return self._cb


class MsgServer:
    def __init__(self, cid=None, **kwargs):
        self._cid = cid or uuid.uuid4().hex
        self._topic_handlers = {}

        self._mqtt_client_username = kwargs.get("username", "")
        self._mqtt_client_password = kwargs.get("password", "")
        self._mqtt_broker_host = kwargs.get("host", "127.0.0.1")
        self._mqtt_broker_port = kwargs.get("port", 1883)
        self._mqttclient = None

    def on_connect(self, client, flags, rc, properties):
        logger.info("Connected: %s", self._cid)

    async def on_message(self, client, topic, payload, qos, properties):
        jsonString = json.dumps(json.loads(payload), indent=4, sort_keys=False)
        logger.debug("RECV MSG: %s", jsonString)

        if topic in self._topic_handlers.keys():
            handler = self._topic_handlers[topic]
            """ TODO: use this code when broacast class is ready """
            # instance = None
            # try:
            #     module_name, class_name = handler.classpath.rsplit(".", 1)
            #     MyClass = getattr(importlib.import_module(module_name), class_name)
            #     instance = MyClass.from_json(payload)
            # except:
            #     reason = f'invalid format: {cmd_name}'
            #     logger.warn(reason)
            # if instance and handler:
            #     handler.handle(self, topic, instance, properties)
            jsonString = payload.decode("utf-8")
            cb_func = handler.cb
            if cb_func:
                await cb_func(jsonString)
        elif client.topic_wildcard(topic) in self._topic_handlers.keys():
            handler = self._topic_handlers[client.topic_wildcard(topic)]
            """ TODO: use this code when broacast class is ready """
            # instance = None
            # try:
            #     module_name, class_name = handler.classpath.rsplit(".", 1)
            #     MyClass = getattr(importlib.import_module(module_name), class_name)
            #     instance = MyClass.from_json(payload)
            # except:
            #     reason = f'invalid format: {cmd_name}'
            #     logger.warn(reason)
            # if instance and handler:
            #     handler.handle(self, topic, instance, properties)
            jsonString = payload.decode("utf-8")
            cb_func = handler.cb
            if cb_func:
                await cb_func(jsonString)
        else:
            logger.warning("unknown topic: %s", topic)

    def on_disconnect(self, client, packet, exc=None):
        logger.info("Disconnected")

    def on_subscribe(self, client, mid, qos, properties):
        subs = next((sub for sub in client.subscriptions if sub.mid == mid), None)
        logger.info("Subscribed: %s", subs.topic)

    async def _start_mqttclient(self):
        """
        start the mqtt client
        """
        self._mqttclient = MQTTClient(self._cid)

        self._mqttclient.on_connect = self.on_connect
        self._mqttclient.on_message = self.on_message
        self._mqttclient.on_disconnect = self.on_disconnect
        self._mqttclient.on_subscribe = self.on_subscribe
        self._mqttclient.set_auth_credentials(self._mqtt_client_username, self._mqtt_client_password)
        await self._mqttclient.connect(host=self._mqtt_broker_host, port=self._mqtt_broker_port)

        for h in self._topic_handlers.values():
            self._mqttclient.subscribe(h.topic, 2)

    def _stop_mqttclient(self):
        pass

    async def start(self):
        await self._start_mqttclient()

    async def stop(self):
        self._stop_mqttclient()

    def subscribe(self, topic: str, cb: Callable):
        if not isinstance(topic, str) or not topic.strip():
            raise TypeError("topic must be a non-empty string")

        if cb and not callable(cb):
            raise TypeError("The cb must be callable")

        self._topic_handlers[topic] = TopicHandler(topic, cb)
