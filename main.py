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

	def add_service(self, service_name, properties={}):
		properties['name'] = service_name
		v = graph.Vertex('Service', properties=properties, unique_by=['name'])
		return self.graphmodel.add_vertex(v)

	def add_port(self, port, protocol, properties={}):
		properties['port'] = port
		properties['protocol'] = protocol
		v = graph.Vertex('Port', properties=properties, unique_by=['port','protocol'])
		return self.graphmodel.add_vertex(v)

	def add_mac(self, macAddress, properties={}):
		properties['mac_address'] = macAddress
		v = graph.Vertex('MAC', properties=properties, unique_by=['mac_address'])
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
					mac_properties = {}
					mac_properties['vendor'] = address.get('vendor')
					result['address_mac'] = address.get('addr')
					macNode = dm.add_mac(result['address_mac'],properties=mac_properties)
				elif(addrType=='ipv4'):
					result['address_ipv4'] = address.get('addr')
					ipNode = dm.add_ipv4(result['address_ipv4'],properties={})

			dm.add_connection(macNode, 'BOUND_TO', ipNode, properties={})
			hostnames = host.findall('hostnames')
			for hostname in hostnames:
				pass#not sure how to handle this yet

			#Handle Ports
			portNodes = list()
			serviceNodes = list()
			for port in host.find('ports').findall('port'):
				port_properties = {}
				port_protocol = port.get('protocol')
				port_id = int(port.get('portid'))

				port_info = port.find('state')
				if(port_info):
					port_state = port_info.get('state')
					port_reason = port_info.get('syn-ack')
					port_reason_ttl = port_info.get('reason_ttl')
					port_properties.update({'port_state':port_state, 'port_reason':port_reason, 'port_reason_ttl':port_reason_ttl})
				portNode = dm.add_port(port_id,port_protocol,properties=port_properties)
				dm.add_connection(portNode, 'BOUND_TO', ipNode, properties={})
				#Handle Services
				service = port.find('service')
				service_properties = {}
				service_name = service.get('name')
				service_properties['method'] = service.get('method','None')
				service_properties['product'] = service.get('product','None')
				service_properties['ostype'] = service.get('ostype','None')
				service_properties['version'] = service.get('version','None')
				service_properties['extrainfo'] = service.get('extrainfo','None')
				service_properties['tunnel'] = service.get('tunnel','None')
				service_properties['confidence'] = int(service.get('conf',0))
				serviceNode = dm.add_service(service_name,properties=service_properties)
				dm.add_connection(serviceNode, 'HAS_SERVICE', portNode, properties={})
				#dm.add_connection(ipNode, 'HAS_PORT', portNode)
		return dm.graphmodel


filename = 'data/tcpConnect_10.11.1.0-254.xml'
nmap = NmapInterface()
dm = nmap.build_model(filename=filename)
loader = neo4jloader.Neo4jLoader("http://10.0.1.2:7474/db/data/",username="neo4j")
loader.load_from_model(dm)
