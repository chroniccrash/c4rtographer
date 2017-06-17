import hashlib

class GraphModel(object):
    def __init__(self, graphDict=None):
        self.vertices = dict()
        self.edges = dict()

    def add_vertex(self, vertex):
        if(not vertex.id in self.vertices):
            self.vertices[vertex.id] = vertex
        else:
            self.vertices[vertex.id].properties.update(vertex.properties)
        return self.vertices[vertex.id]

    def add_edge(self, edge):
        if(edge.id not in self.edges):
            self.edges[edge.id] = edge
        else:
            self.edges[edge.id].properties.update(edge.properties)
        return self.edges[edge.id]

    def to_dict(self):
        raise NotImplementedError

class Vertex(object):
    def __init__(self, label, properties={}, unique_by=[]):
        self.label = label
        objID = label
        if(unique_by):
            for item in unique_by:
                objID += ':' + str(properties.get(item,'None'))
        else:
            for item in properties.keys():
                objID += ':' + str(properties.get(item,'None'))
        objID = hashlib.md5(objID.encode('utf-8')).hexdigest()[0:10]
        properties['hashcode'] = objID
        self.id = objID
        self.properties = properties

    def update(self, vertex):
        self.properties.update(vertex.properties)
        #self.properties = flatten_properties(self.properties)

    def __str__(self):
        return "%s:%s:%s"%(self.label, self.id, str(self.properties))

class Edge(object):
    def __init__(self, srcVertex, relationship, dstVertex, properties={}):
        self.srcVertex = srcVertex
        self.dstVertex = dstVertex
        self.relationship = relationship
        self.properties = properties
        self.id = "%s:%s:%s"%(srcVertex.id, relationship, dstVertex.id)
        if(unique_by):
            for item in unique_by:
                self.id += ':' + str(properties.get(item,'None'))
        else:
            for item in properties.keys():
                self.id += ':' + str(properties.get(item,'None'))
        self.id = hashlib.md5(self.id.encode('utf-8')).hexdigest()[0:10]
        self.properties['hashcode'] = self.id

    def update(self, edge):
        self.properties.update(edge.properties)
        #self.properties = flatten_properties(self.properties)
