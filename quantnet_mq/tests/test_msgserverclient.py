#!/usr/bin/env python3

import os
import logging
import unittest
import asyncio
import json

from quantnet_mq.msgserver import MsgServer
from quantnet_mq.msgclient import MsgClient


class TestMsgServer(unittest.IsolatedAsyncioTestCase):

    async def test_msgsrv_cb(self):

        message_rcvd = False
        message = "testingmessages"

        topic = "mytopic"

        msg_server = MsgServer(host=os.getenv("MQ_HOST", "localhost"))

        async def print_on_msg(data):
            if data == json.dumps(message):
                nonlocal message_rcvd
                message_rcvd = True
            else:
                print(f"recv:{data}")

        msg_server.subscribe(topic, print_on_msg)
        await msg_server.start()

        msg_client = MsgClient(host=os.getenv("MQ_HOST", "localhost"))
        await msg_client.start()
        await msg_client.publish(topic, message)

        timeout = 3
        await asyncio.sleep(timeout)
        if message_rcvd:
            print("Success")
        else:
            print(f"Failed after {timeout} seconds")

        await msg_client.stop()
        await msg_server.stop()

    async def test_msgsrv_null_cb(self):

        message_rcvd = False
        message = "testingmessages"

        topic = "mytopic"

        msg_server = MsgServer(host=os.getenv("MQ_HOST", "localhost"))

        msg_server.subscribe(topic, None)
        await msg_server.start()
        # msg_server.stop()

        msg_client = MsgClient(host=os.getenv("MQ_HOST", "localhost"))
        await msg_client.start()
        await msg_client.publish(topic, message)

        timeout = 3
        await asyncio.sleep(timeout)
        if not message_rcvd:
            print(f"Succeed after {timeout} seconds")

        await msg_client.stop()
        await msg_server.stop()
