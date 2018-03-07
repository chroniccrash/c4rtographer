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

    def add_connection_transport_tcp_initialSyn(self, srcIP, srcPort, dstIP, dstPort, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['protocol'] = srcPort.properties['protocol']
        properties['src'] = srcPort.properties['port']
        properties['dst'] = dstPort.properties['port']
        properties['initialsyn'] = True
        e = graph.Edge(srcIP, 'InitialSYN', dstIP, properties=properties, unique_by=['protocol','src','dst','initialsyn'])
        return self.graphmodel.add_edge(e)

    def add_connection_transport_tcp_synack(self, srcIP, srcPort, dstIP, dstPort, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['protocol'] = srcPort.properties['protocol']
        properties['src'] = srcPort.properties['port']
        properties['dst'] = dstPort.properties['port']
        properties['synack'] = True
        e = graph.Edge(srcIP, 'SYNACK', dstIP, properties=properties, unique_by=['protocol','src','dst','synack'])
        return self.graphmodel.add_edge(e)

    def add_connection_transport_tcp_reset(self, srcIP, srcPort, dstIP, dstPort, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['protocol'] = srcPort.properties['protocol']
        properties['src'] = srcPort.properties['port']
        properties['dst'] = dstPort.properties['port']
        properties['reset'] = True
        e = graph.Edge(srcIP, 'RESET', dstIP, properties=properties, unique_by=['protocol','src','dst','reset'])
        return self.graphmodel.add_edge(e)

    def add_connection_transport_udp(self, srcIP, srcPort, dstIP, dstPort, **kwargs):
        properties = dict()
        for key in kwargs:
            properties[key] = kwargs.get(key)
        properties['protocol'] = srcPort.properties['protocol']
        properties['src'] = srcPort.properties['port']
        properties['dst'] = dstPort.properties['port']
        e = graph.Edge(srcIP, 'UDP', dstIP, properties=properties, unique_by=['protocol','src','dst'])
        return self.graphmodel.add_edge(e)

class PcapInterface(object):
    def build_model(self, filename=None):
        dm = PcapDataModel()
        pcapData = PcapReader(filename)
        for pkt in pcapData:
            if(pkt.haslayer(Ether)):
                eth = pkt[Ether]
                if(pkt.haslayer(IP)):
                    if(pkt.haslayer(TCP)):

                        ipv4 = pkt[IP]
                        ipv4Src = dm.add_ipv4(ipv4.src)
                        ipv4Dst = dm.add_ipv4(ipv4.dst)

                        tcp = pkt[TCP]
                        tcpSrc = dm.add_port(tcp.sport,'TCP')
                        tcpDst = dm.add_port(tcp.dport,'TCP')
                        if((SYN & tcp.flags) and not (ACK & tcp.flags)):
                            dm.add_connection_transport_tcp_initialSyn(ipv4Src, tcpSrc, ipv4Dst, tcpDst)
                        if((RST & tcp.flags) and not (ACK & tcp.flags)):
                            dm.add_connection_transport_tcp_reset(ipv4Src, tcpSrc, ipv4Dst, tcpDst)
                        if((FIN & tcp.flags) and not (ACK & tcp.flags)):
                            dm.add_connection_transport_tcp_reset(ipv4Src, tcpSrc, ipv4Dst, tcpDst)
                        if(pkt.haslayer(Raw)):
                            if(pkt.haslayer(Padding)):
                                pass
                        elif(pkt.haslayer(Padding)):
                            pass
                        else:
                            pass
                    elif(pkt.haslayer(UDP)):
                        ipv4 = pkt[IP]
                        ipv4Src = dm.add_ipv4(ipv4.src)
                        ipv4Dst = dm.add_ipv4(ipv4.dst)
                        udp = pkt[UDP]
                        udpSrc = dm.add_port(udp.sport,'UDP')
                        udpDst = dm.add_port(udp.dport,'UDP')
                        dm.add_connection_transport_udp(ipv4Src, udpSrc, ipv4Dst, udpDst)

                        if(pkt.haslayer(DNS)):
                            pass
                        else:
                            pass #Nothing hit
                    else:
                        pass #Nothing hit
                elif(pkt.haslayer(IPv6)):
                    if(pkt.haslayer(TCP)):
                        pass
                    elif(pkt.haslayer(UDP)):
                        if(pkt.haslayer(DHCP6)):
                            pass
                        elif(pkt.haslayer(DHCP6_Solicit)):
                            pass #Nothing deeper
                        else:
                            pass #Nothing hit
                    else:
                        pass #Nothing hit
                elif(pkt.haslayer(ARP)):
                    arp = pkt[ARP]
                    if(arp.op==1): #who-has
                        pass
                    elif(arp.op==2): #is-at
                        pass

                else:
                    pass #Nothing hit
        return dm.graphmodel

pcap = PcapInterface()
dm = pcap.build_model(filename='../chalcap.pcapng')
#dm = pcap.build_model(filename='../deadly_arthropod.pcap')
loader = neo4jloader.Neo4jLoader("http://192.168.183.129:7474/db/data/",username="neo4j",password="password")
loader.load_from_model(dm)
