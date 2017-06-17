from neo4jrestclient.client import GraphDatabase
import getpass

def flatten_dict(dictToFlatten):
    #Pass through for now.  Will flatten later (because neo4j doesn't like embedded dictionaries)
    return dictToFlatten


class Neo4jLoader(object):
    def __init__(self, url, username='neo4j', password=None):
        if(not password):
            password=getpass.getpass()
        self.gdb = GraphDatabase(url, username=username, password=password)

    def add_vertex(self, vertex):
        properties = flatten_dict(vertex.properties)
        jprops = str(properties).replace("{'","{").replace("':",":").replace(", '",", ")
        queryString = "MERGE (a:%s {hashcode:'%s'}) ON CREATE SET a=%s ON MATCH SET a+=%s"%(vertex.label, vertex.properties['hashcode'], jprops, jprops)
        return self.gdb.query(queryString)

    def add_edge(self, edge):
        properties = flatten_dict(edge.properties)
        jprops = str(properties).replace("{'","{").replace("':",":").replace(", '",", ")
        queryString = "MATCH (src:%s {hashcode:'%s'}), (dst:%s {hashcode:'%s'}) MERGE (src)-[:%s %s]->(dst)"%(edge.srcVertex.label, edge.srcVertex.id, edge.dstVertex.label, edge.dstVertex.id, edge.relationship, jprops)
        return self.gdb.query(queryString)

    def load_from_model(self, model):
        for vid in model.vertices:
            self.add_vertex(model.vertices[vid])
        for eid in model.edges:
            self.add_edge(model.edges[eid])
