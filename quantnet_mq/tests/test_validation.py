import os
import json
from quantnet_mq.schema.models import agentRegister, agentRegisterResponse
from quantnet_mq.schema.models import QNode, MNode, BSMNode, OpticalSwitch

TEST_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                          "../schema/examples"))

QNODES = ["q.json",
          "topology/conf_lbnl-q.json",
          "topology/conf_ucb-q.json"]

BSMNODES = ["bsm.json",
            "topology/conf_lbnl-bsm.json"]

MNODES = ["m.json",
          "topology/conf_lbnl-m.json",
          "topology/conf_ucb-m.json"]

SWITCHES = ["switch.json",
            "topology/conf_lbnl-switch.json",
            "topology/conf_ucb-switch.json"]


class TestValidation:

    def get_file_json(self, f):
        with open(f, "r") as file:
            data = json.load(file)
        return data

    def test_qnodes(self):
        for ex in QNODES:
            print(f"\n--- {ex} ---")
            fname = os.path.join(TEST_PATH, ex)
            node = self.get_file_json(fname)
            obj = QNode(**node)
            print(obj.serialize())

    def test_bsmnodes(self):
        for ex in BSMNODES:
            print(f"\n--- {ex} ---")
            fname = os.path.join(TEST_PATH, ex)
            node = self.get_file_json(fname)
            obj = BSMNode(**node)
            print(obj.serialize())

    def test_mnodes(self):
        for ex in MNODES:
            print(f"\n--- {ex} ---")
            fname = os.path.join(TEST_PATH, ex)
            node = self.get_file_json(fname)
            obj = MNode(**node)
            print(obj.serialize())

    def test_switches(self):
        for ex in SWITCHES:
            print(f"\n--- {ex} ---")
            fname = os.path.join(TEST_PATH, ex)
            node = self.get_file_json(fname)
            obj = OpticalSwitch(**node)
            print(obj.serialize())

    def test_register(self):
        fname = os.path.join(TEST_PATH, QNODES[0])
        node = self.get_file_json(fname)
        instance = {
            "cmd": "register",
            "agentId": "test",
            "payload": node
        }
        r = agentRegister(**instance)
        print(r.serialize())

    def test_response(self):
        instance = {
            "status": {
                "code": 200,
                "value": "OK"
            }
        }
        r = agentRegisterResponse(**instance)
        print(r.serialize())
