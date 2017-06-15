from neo4jrestclient.client import GraphDatabase
import getpass

def flatten_dict(dictToFlatten):
    return dictToFlatten


class Neo4jLoader(object):
    def __init__(self, url, username='neo4j', password=getpass.getpass()):
        self.gdb = GraphDatabase(url, username=username, password=password)

    def add_vertex(self, vertex):
        properties = flatten_dict(vertex.properties)
        jprops = str(properties).replace("{'","{").replace("':",":").replace(", '",", ")
        queryString = "MERGE (a:%s {hashcode:'%s'}) ON CREATE SET a=%s ON MATCH SET a+=%s"%(vertex.label, properties['hashcode'], jprops, jprops)
        print(queryString)
        self.gdb.query(queryString)

    def add_edge(self, edge):
        properties = flatten_dict(edge.properties)
        jprops = str(properties).replace("{'","{").replace("':",":").replace(", '",", ")
        queryString = "MATCH (src:%s {hashcode:'%s'}), (dst:%s {hashcode:'%s'}) MERGE (src)-[:%s %s]->(dst)"%(edge.srcVertex.label, edge.srcVertex.id, edge.dstVertex.label, edge.dstVertex.id, edge.relationship, jprops)
        self.gdb.query(queryString)

    def load_from_model(self, model):
        #print(model.vertices.keys())
        for vid in model.vertices:
            #print(model.vertices[vid])
            #print(vid, model.vertices[vid])
            self.add_vertex(model.vertices[vid])
        for eid in model.edges:
            self.add_edge(model.edges[eid])
