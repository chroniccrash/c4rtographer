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
			hostnames = host.findall('hostnames')
			for hostname in hostnames:
				pass#not sure how to handle this yet
			dm.add_ipv4(result['address_ipv4'])
		for item in dm.graphmodel.vertices.keys():
			print(item, dm.graphmodel.vertices[item])
		return dm.graphmodel


filename = 'data/tcpConnect_10.11.1.0-254.xml'
nmap = NmapInterface()
dm = nmap.build_model(filename=filename)
loader = neo4jloader.Neo4jLoader("http://10.0.1.2:7474/db/data/",username="neo4j")
loader.load_from_model(dm)
