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
    print("GraphModel.add_vertex(%s): Node %i"%(vertex,id(vertex)))
    return self.vertices[vertex.id]

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

  def __str__(self):
    return "%s:%s:%s"%(self.label, self.id, str(self.properties))

class NmapDataModel(object):
  def __init__(self):
    self.graphmodel = GraphModel()

  def add_ipv4(self, ipAddress, properties={}):
    '''
    if(properties == None):
        properties = {}
    '''
    properties['ipv4'] = ipAddress
    v = Vertex('IP', properties=properties, unique_by=['ipv4'])
    print("NmapDataModel.add_ipv4(%s,properteries=\{%s\}): Node %i"%(ipAddress,str(properties),id(v)))
    return self.graphmodel.add_vertex(v)

class NmapInterface(object):
  def build_model_test_02(self, filename=None):
    dm = NmapDataModel()
    addresses = ['192.168.0.1','192.168.0.2','192.168.0.3','192.168.0.4']
    for address in addresses:

      dm.add_ipv4(address,properties={})
    for item in dm.graphmodel.vertices:
      print("NmapInterface.build_model_test_02(): %s - Node %i"%(dm.graphmodel.vertices[item],id(dm.graphmodel.vertices[item])))
    return dm.graphmodel

if __name__ == '__main__':
  interface = NmapInterface()
  interface.build_model_test_02()
