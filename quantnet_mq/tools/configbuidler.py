"""
Copyright ESnet 2023 - 

"""
import os
import shutil
import networkx as nx
import json
import matplotlib.pyplot as plt
import random
from quantnet_mq.schema.models import (
    QNode,
    MNode,
    BSMNode,
    OpticalSwitch)


class ConfigBuilder:
    def __init__(self, num_switches=1, num_nodes=5, out_dir="/tmp/quantnet_nodes"):
        self._num_switches = num_switches
        self._num_nodes = num_nodes
        self._outdir = out_dir

    @staticmethod
    def draw_and_save_graph(g, dirpath=None):

        pos = nx.spring_layout(g)
        color_map = {
            'type_QNode': 'red',
            'type_MNode': 'blue',
            'type_BSMNode': 'green',
            'type_OpticalSwitch': 'purple'
        }
        size_map = {
            'type_QNode': 500,
            'type_MNode': 500,
            'type_BSMNode': 500,
            'type_OpticalSwitch': 1000
        }

        node_colors = [color_map.get(g.nodes[node].get('node_type', 'default'), 'gray') for node in g.nodes()]
        node_sizes = [size_map.get(g.nodes[node].get('node_type', 'default'), 500) for node in g.nodes()]

        plt.figure(figsize=(10, 8))
        nx.draw(g, pos, with_labels=True, node_color=node_colors, node_size=node_sizes, edge_color='gray')
        plt.title("Topology with Additional Randomly Added Nodes")
        if dirpath:
            plt.savefig(f"{dirpath}/topo.png")
        plt.show()

    @staticmethod
    def delete_and_mkdir(dir_path):
        # Check if the directory exists
        if os.path.exists(dir_path):
            # If it exists, delete the contents
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove the file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove the directory and its contents
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        else:
            # If it doesn't exist, create a new directory
            os.makedirs(dir_path)

    @staticmethod
    def load_default_config(node_type: str) -> dict:
        if node_type == "QNode":
            f = "../schema/examples/q.json"
        elif node_type == "MNode":
            f = "../schema/examples/m.json"
        elif node_type == "BSMNode":
            f = "../schema/examples/bsm.json"
        elif node_type == "OpticalSwitch":
            f = "../schema/examples/switch.json"
        else:
            raise Exception(f"unknown configuration type {node_type}")

        with open(f, 'r') as nf:
            data = nf.read()
        try:
            conf = json.loads(data)
        except Exception as e:
            raise(e)

        return conf

    @staticmethod
    def get_type(text, prefix='type_'):
        # Split the string based on the prefix
        parts = text.split(prefix, 1)

        # Get the substring after the prefix
        if len(parts) > 1:
            result = parts[1]
        else:
            result = None

        return result

    def build(self):
        # Create the switch topology
        if self._num_switches > 0:
            g = switches = nx.erdos_renyi_graph(self._num_switches, 0.6)
            for node in g.nodes():
                g.nodes[node]['node_type'] = f'type_{random.choice(["OpticalSwitch"])}'

            # self.draw_and_save_graph(switches)

        # Add More Nodes Randomly
        if self._num_switches > 0:
            switch_nodes = list(switches.nodes())
            for i in range(len(switches), len(switches) + self._num_nodes):
                g.add_node(i, node_type=f'type_{random.choice(["QNode", "MNode", "BSMNode"])}')

                num_edges = random.randint(1, self._num_switches)
                # existing_nodes = list(switches.nodes())
                random.shuffle(switch_nodes)
                for j in range(num_edges):
                    g.add_edge(i, switch_nodes[j])
        else:
            g = nx.erdos_renyi_graph(self._num_nodes, 0.6)

            # Assign types to new nodes
            for node in g.nodes():
                g.nodes[node]['node_type'] = f'type_{random.choice(["QNode", "MNode", "BSMNode"])}'

        # TODO: mnode require at least two neighbors
        mnodes = [node for node in g.nodes() if g.nodes[node]['node_type'] == 'type_MNode']
        for node in mnodes:
            if len(list(g.neighbors(node))) < 2:
                g.nodes[node]['node_type'] = f'type_{random.choice(["QNode","BSMNode"])}'

        self.delete_and_mkdir(self._outdir)

        for node in g.nodes():
            class_name = self.get_type(g.nodes[node]['node_type'])
            nodeClass = globals().get(class_name)
            node_config = nodeClass()

            default_config = self.load_default_config(class_name)

            node_config.systemSettings = {'name': f"{class_name}_{node}",
                                          'ID': f'{class_name}_{node}',
                                          'type': f'{class_name}',
                                          'controlInterface': 'localhost'}

            neighbors = list(g.neighbors(node))
            channels = []
            for index, neighbor in enumerate(neighbors):
                channels.append(
                    {
                        "ID": f'{index}',
                        "name": f"channel_{index}",
                        "type": "quantumconnection",
                        "direction": "out",
                        "wavelength": {"value": 1550,  "unit": "nm"},
                        "power": 12.1,
                        "neighbor": {
                            "idRef": f"urn:quant-net:f{neighbor}:{index}",
                            "systemRef": f"{neighbor}",
                            "channelRef": f"{index}",
                            "loss": {"value": 5,  "unit": "dB"}
                        }
                    }
                )
            node_config.channels = channels

            if class_name == 'BSMNode' or class_name == 'MNode':
                detectors = []
                for index, neighbor in enumerate(neighbors):
                    detectors.append(
                        {
                            "name": f"detector_{index}",
                            "efficiency": "0.99",
                            "darkCount": "1",
                            "countRate": {"value": 1000,  "unit": "Hz"},
                            "timeResolution": {"value": 100,  "unit": "ns"}
                        }
                    )
                node_config.quantumSettings = default_config['quantumSettings']

            if class_name == "QNode":
                node_config.qubitSettings = default_config['qubitSettings']

                node_config.matterLightInterfaceSettings = default_config['matterLightInterfaceSettings']

            file_path = f'{self._outdir}/{class_name}_{node}.json'
            data = json.loads(node_config.serialize())
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

            print(json.dumps(node_config.serialize(), indent=4))

        # draw and save the topology graph
        self.draw_and_save_graph(g, self._outdir)

        return g


# This block will only execute if the script is run directly
if __name__ == "__main__":
    # Create an instance of ConfigBuilder
    builder = ConfigBuilder(num_switches=3, num_nodes=5, out_dir="/tmp/quantnet_nodes")
    # Call the build method
    builder.build()
    print("completed!")
