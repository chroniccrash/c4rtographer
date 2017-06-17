#public modules
import xml.etree.ElementTree as ET
#private modules
import neo4jloader, graph

class NmapDataModel(object):
	def __init__(self):
		self.graphmodel = graph.GraphModel()

	def add_ipv4(self, ipAddress, properties={}):
		properties['ipv4'] = ipAddress
		v = graph.Vertex('IP', properties=properties, unique_by=['ipv4'])
		return self.graphmodel.add_vertex(v)

	def add_port(self, port, protocol, properties={}):
		properties['port'] = port
		properties['protocol'] = protocol
		v = graph.Vertex('Port', properties=properties, unique_by=['port','protocol'])
		return self.graphmodel.add_vertex(v)

	def add_connection(self, srcVertex, rel, dstVertex, properties={}):
		if(not properties):
			properties = {}
		e = graph.Edge(srcVertex, rel, dstVertex, properties=properties)
		return self.graphmodel.add_edge(e)

class NmapInterface(object):
	def build_model(self, filename=None):
		dm = NmapDataModel()
		tree = ET.parse(filename)
		root = tree.getroot()
		for host in root.findall('host'):
			result = {}
			status = host.find('status').get('state')
			if(status):
				result['status']=status
			addresses = host.findall('address')
			for address in addresses:
				addrType = address.get('addrtype')
				if(addrType=='mac'):
					result['vendor'] = address.get('vendor')
					result['address_mac'] = address.get('addr')
				elif(addrType=='ipv4'):
					result['address_ipv4'] = address.get('addr')
					ipNode = dm.add_ipv4(result['address_ipv4'],properties={})
			hostnames = host.findall('hostnames')
			for hostname in hostnames:
				pass#not sure how to handle this yet

			for port in host.find('ports').findall('port'):
				data = {}
				port_protocol = port.get('protocol')
				port_id = int(port.get('portid'))

				port_info = port.find('state')
				if(port_info):
					port_state = port_info.get('state')
					port_reason = port_info.get('syn-ack')
					port_reason_ttl = port_info.get('reason_ttl')
					data.update({'port_state':port_state, 'port_reason':port_reason, 'port_reason_ttl':port_reason_ttl})
				service = port.find('service')
				if(service):
					service_name = service.get('name')
					service_method = service.get('method')
					service_confidence = int(service.get('conf'))
					data.update({'service_name':service_name, 'service_method':service_method, 'service_confidence':service_confidence})
				portNode = dm.add_port(port_id,port_protocol,properties=data)
				dm.add_connection(ipNode, 'HAS_PORT', portNode)

		return dm.graphmodel


filename = 'data/tcpConnect_10.11.1.0-254.xml'
nmap = NmapInterface()
dm = nmap.build_model(filename=filename)
loader = neo4jloader.Neo4jLoader("http://10.0.1.2:7474/db/data/",username="neo4j")
loader.load_from_model(dm)
