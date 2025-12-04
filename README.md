The QUANT-NET Message Queue Module (quantnet_mq)
================================================

The QUANT-NET Message Queue module provide RPC and Publish/Subscribe capabilities for the control plane, and the package is a common dependency for the QNCP Controller, Agent, and API packages. The module includes:

* Remote procedure call (RPC) client and server implementations
* Publish/Subscribe (pub/sub) client and server implementations
* Core schemas for the QUANT-NET Control Plane network data model
* Auto-generated Python objects for all defined schema


Installing
----------

```
pip3 install .   # or pip3 install -e .
```


Building
--------

```
python3 -m build
```

Testing
-------

```
MQ_HOST=<broker_host> pytest -v
```

Example Usage
-------------

* RPC client

```
import asyncio
from quantnet_mq.rpcclient import RPCClient

async def main():
    client = RPCClient("example_client")
    client.set_handler("myRequest", None,
        "quantnet_mq.schema.models.myns.myRequest")
    await client.start()

    # send a message and wait up to for a response 5s
    msg = {"arg1": "value1", "arg2": 999.99}
    req = await client.call("myRequest, msg, timeout=5.0)
    print (req)

if __name__ == "__main__":
    asyncio.run(main())
```

* Pub/Sub receiver

```
import asyncio
from quantnet_mq.rpcclient import MsgServer

async def handle_msg(data):
    print (data)

async def main():
    client = MsgServer()
    mclient.subscribe("mytopic", self.handle_msg)
    await mclient.start()
    # wait as long as needed here ...

if __name__ == "__main__":
    asyncio.run(main())
```