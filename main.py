#from neo4jrestclient.client import GraphDatabase
import sqlite3
import getpass
#Ping sweep

import xml.etree.ElementTree as ET
import neo4jloader
import graph

#register attack/scan
#record keeper
#record every action taken
#oracle ... analyze shit.
#the soldier...(he does the knockin')
#the commander...requests action
#register file created

class NmapDataModel(object):
	def __init__(self):
		self.gm = graph.GraphModel()

	def add_ipv4(self, ipAddress, properties={}):
		properties['ipv4'] = ipAddress
		v = graph.Vertex('IP', properties=properties, unique_by=['ipv4'])
		return self.gm.add_vertex(v)

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
				pass#not sure how to handle this
			dm.add_ipv4(result['address_ipv4'])
		return dm

filename = 'C:\\Users\\bostw\\Desktop\\projects\\oscp_course\\scans\\10.11.1.0-254\\tcpConnect_10.11.1.0-254.xml'


nmap = NmapInterface()
dm = nmap.build_model(filename=filename)
loader = neo4jloader.Neo4jLoader("http://10.0.1.2:7474/db/data/",username="neo4j")
loader.load_from_model(dm.gm)


'''
filename = "data/pingSweep_10.11.1.0-254.xml"


scanner = gdb.nodes.create(mac='00:0c:29:ff:32:0e', ipv4Addr='10.11.0.1', vendor='VMWare', status='up')
scanner.labels.add("Me")

tree = ET.parse(filename)
root = tree.getroot()
for host in root.findall('host'):
	result = {}
	status = host.find('status').get('state')
	if(status):
		result['status']=status
		print(status)
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
		pass#not sure how to handle this



	hostNode = gdb.nodes.create(name=addr, mac=mac, ipv4Addr=addr, vendor=vendor, status=status)
	hostNode.labels.add("Host")
	gdb.relationships.create(scanner, "SCANNED", hostNode)
'''
