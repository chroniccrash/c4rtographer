import ipaddress
import neo4jloader, graph
import dpkt


class NetworkDataModel(object):
    def __init__(self):
        self.graphmodel = graph.GraphModel()

    def add_ipv4Node(self, ipaddress, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['ipv4Address'] = ipaddress
        v = graph.Vertex('IPv4_Node', properties=properties, unique_by=['ipv4Address'])
        return self.graphmodel.add_vertex(v)

    def add_ipv4Network(self, networkAddress, broadcastAddress, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['ipv4NetworkAddress'] = networkAddress
        properties['ipv4BroadcastAddress'] = broadcastAddress
        v = graph.Vertex('IPv4_Network', properties=properties, unique_by=['ipv4Network'])
        return self.graphmodel.add_vertex(v)

    def add_port(self, port, protocol, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['port'] = port
        properties['protocol'] = protocol
        v = graph.Vertex('Port', properties=properties, unique_by=['port', 'protocol'])
        return self.graphmodel.add_vertex(v)

    def add_mac(self, mac_address, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['mac_address'] = mac_address
        v = graph.Vertex('MAC', properties=properties, unique_by=['mac_address'])
        return self.graphmodel.add_vertex(v)

    def add_connection_linkLayer(self, srcMac, dstMac, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        e = graph.Edge(srcMac, 'LinkLayer', dstMac, properties=properties)
        return self.graphmodel.add_edge(e)

    def add_connection_internet(self, srcIP, dstIP, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        e = graph.Edge(srcIP, 'InternetLayer', dstIP, properties=properties)
        return self.graphmodel.add_edge(e)

    '''
    def add_connection_initialSyn(self, srcIP, srcPort, dstIP, dstPort, protocol, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)

        e = graph.Edge(srcIP, '%s_%s_TO_%s'%(protocol), dstIP, properties=properties)
        return self.graphmodel.add_edge(e)
    '''
    def add_connection_mac_ip_port(self, srcMac, srcIP, srcPort, dstMac, dstIP, dstPort, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)


class PcapInterface(object):
    def build_model(self, filename=None):
        dm = NetworkDataModel()
        pcapData = dpkt.pcap.Reader(filename)
        for ts, buf in pcapData:
            print(dpkt.ethernet.Ethernet(buf))
        return dm.graphmodel

pcap = PcapInterface()
dm = pcap.build_model(filename='../challenge.pcap')
#dm = pcap.build_model(filename='../deadly_arthropod.pcap')
loader = neo4jloader.Neo4jLoader("http://192.168.183.129:7474/db/data/",username="neo4j",password="password")
loader.load_from_model(dm)
