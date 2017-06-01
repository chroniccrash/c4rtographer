from neo4jrestclient.client import GraphDatabase
import sqlite3
import getpass
#Ping sweep

import xml.etree.ElementTree as ET


#register attack/scan
#record keeper
#record every action taken
#oracle ... analyze shit.
#the soldier...(he does the knockin')
#the commander...requests action
#register file created




gdb = GraphDatabase("http://10.0.1.2:7474/db/data/", username="neo4j", password=getpass.getpass())


filename = "/root/Desktop/scans/pingSweep_10.11.1.0-254.xml"


scanner = gdb.nodes.create(mac='00:0c:29:ff:32:0e', ipv4Addr='10.11.0.1', vendor='VMWare', status='up')
scanner.labels.add("Me")

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



	hostNode = gdb.nodes.create(name=addr, mac=mac, ipv4Addr=addr, vendor=vendor, status=status)
	hostNode.labels.add("Host")
	gdb.relationships.create(scanner, "SCANNED", hostNode)
