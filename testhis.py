from scapy.all import *
import neo4jloader, graph

FIN=0x01
SYN=0x02
RST=0x04
PSH=0x08
ACK=0x10
URG=0x20
ECE=0x40
CWR=0x80


class PcapDataModel(object):
    def __init__(self):
        self.graphmodel = graph.GraphModel()

    def add_ipv4(self, ipaddress, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['ipv4'] = ipaddress
        v = graph.Vertex('IPv4', properties=properties, unique_by=['ipv4'])
        return self.graphmodel.add_vertex(v)

    def add_vulnerability(self, cveNumber, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['cve'] = cveNumber
        v = graph.Vertex('CVE', properties=properties, unique_by=['cve'])
        return self.graphmodel.add_vertex(v)

    def add_connection(self, srcNode, rel, dstNode, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)

        e = graph.Edge(srcNode, rel, dstNode, properties=properties, unique_by=['srcNode','dstNode'])
        return self.graphmodel.add_edge(e)


class PcapInterface(object):
    def build_model(self, filename1, filename2):
        dm = PcapDataModel()
        fp1 = open(filename,'r')
        fp2 = open(filename2, 'r')
        data1 = json.load(fp1)
        data2 = json.load(fp2)
        for entry1 in data1:
            srcIP = dm.add_ipv4(entry1['srcIP'])
            dstIP = dm.add_ipv4(entry1['dstIP'])
            for entry2 in data2:
                if(entry1['srcIP'] == entry2['srcIP']) or (entry1['srcIP'] == entry2['dstIP']):
                    vuln = dm.add_vulnerability(entry2['cveNumber'])
                    severity = entry2['severity']
                    vulnerabilityName = entry2['vulnerability']
                    dm.add_connection(srcIP, vuln, severity=severity, vulnerability=vulnerabilityName)


        return dm.graphmodel

pcap = PcapInterface()
dm = pcap.build_model(filename='../chalcap.pcapng')
#dm = pcap.build_model(filename='../deadly_arthropod.pcap')
loader = neo4jloader.Neo4jLoader("http://192.168.183.129:7474/db/data/",username="neo4j",password="password")
loader.load_from_model(dm)
