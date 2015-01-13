import csv
import json
import os
import pickle
import random


def write_schema(graph, filename):
    s = NX2SylvaSchemaConverter(graph)
    s.build_schemas(filename)


def write_csvs(graph, node_dir, edge_dir, dest_dir, node_type_attr="type"):
    nodefiles = os.listdir(node_dir)
    edgefiles = os.listdir(edge_dir)
    for nodefile in nodefiles:
        node_type = nodefile.split("-")[0]
        full_nodefile = node_dir + '/' + nodefile
        rows = []
        with open(full_nodefile, 'r') as f:
            reader = csv.reader(f)
            write_attrs = reader.next()
            rows.append(write_attrs)
            for node, attrs in graph.nodes(data=True):
                if attrs[node_type_attr].lower() == node_type:
                    row = []
                    for wa in write_attrs:
                        row.append(attrs.get(wa, "").encode('utf-8'))
                    rows.append(row)
        dest = dest_dir + "/nodes/" + nodefile
        with open(dest, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    for edgefile in edgefiles:
        node_type = edgefile.split("-")[0]
        full_edgefile = edge_dir + '/' + edgefile
        rows = []
        with open(full_edgefile, 'r') as f:
            reader = csv.reader(f)
            write_hdr = reader.next()
            rows.append(write_hdr)
            write_attrs = write_hdr[-2:]
            for s, t, attrs in graph.edges(data=True):
                if attrs[node_type_attr].lower() == node_type:
                    row = [s, t]
                    for wa in write_attrs:
                        row.append(attrs.get(wa, "").encode('utf-8'))
                    rows.append(row)
        dest = dest_dir + "/relationships/" + edgefile
        with open(dest, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(rows)




 
class NX2SylvaSchemaConverter(object):
    """
    Generates JSON data compatible with SylvaDB schemast
    by passing an Networkx graph with the following characterists:
    GraphType = networkx.DiGraph or networkx.MultiDiGraph
    Nodes must have attributes: id, NodeType, NodeTypeId, Name
    Edges must have attributes: RelationshipType, RelationshipTypeId
    """
 
    def __init__(self, graph):
        self.graph = graph
        self.schemas = {'allowedEdges': [], 'nodeTypes': {}}

    def build_schemas(self, filename):
        self.get_node_types()
        self.get_allowed_edges()
        self.jsonify(filename)


    def get_node_types(self):
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs['NodeType']
            self.schemas['nodeTypes'].update({node_type: {}})
            attr_dict = {}
            for key, value in attrs.iteritems():
                if key not in ['NodeType', 'NodeTypeId', 'id']:
                    attr_dict.update({
                        key: {
                            'dataype': type(value),
                            'validation': None,
                            'description': '',
                            'default': '',
                            'required': False,
                            'slug': str(node_type) + str(random.random()),
                            'value': '',
                            'display': False
                        }
                    })
            self.schemas['nodeTypes'][node_type].update(attr_dict)
        return self.schemas

    def get_allowed_edges(self):
        types = []
        for edge in self.graph.edges(data=True):
            source = edge[0]
            target = edge[1]
            source_type = self.graph.node[source]['NodeType']
            target_type = self.graph.node[target]['NodeType']
            label = edge[2]['RelationshipType']
            if label not in types:
                types.append(label)
                allowed_edge = {
                    'source': source_type,
                    'properties': {},
                    'target': target_type,
                    'label': label
                }
                for key, value in edge[2].iteritems():
                    if key not in ['RelationshipType', 'RelationshipTypeId', 'id']:
                        allowed_edge['properties'].update({
                            key: {
                                'dataype': type(value),
                                'validation': None,
                                'description': '',
                                'default': '',
                                'required': False,
                                'slug': str(label) + str(random.random()),
                                'value': '',
                                'display': False
                            }
                        })
                self.schemas['allowedEdges'].append(allowed_edge)
        return self.schemas

    def jsonify(self, filename):
        output = json.dumps(self.schemas, cls=PythonObjectEncoder)
        with open(filename, 'w') as f:
            f.write(output)
 
 
class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(
            obj, (list, dict, str, unicode, int, float, bool, type(None))
        ):
            return json.JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}
 
 
def write_gexf(graph, filename):
    g = NX2SylvaConverter(graph)
    g.write_gexf(filename)
 
 
class NX2SylvaConverter(object):
    """
    Makes gexf that Sylva can import by passing an Networkx graph
    with the following characterists.
    GraphType = networkx.DiGraph or networkx.MultiDiGraph
    Nodes must have attributes: id, NodeType, NodeTypeId, Name
    Edges must have attributes: RelationshipType, RelationshipTypeId
    """
 
    def __init__(self, graph):
        self.graph = graph
        self.xml_version = u'<?xml version="1.0" encoding="UTF-8"?>'
        self.gexf = u'<gexf xmlns="http://www.gexf.net/1.2draft"'
        self.viz = u'xmlns:viz="http://www.gexf.net/1.2draft/viz"'
        self.xsi = u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        self.schemas = (u'xsi:schemaLocation="http://www.gexf.net/1.2draft '
                        'http://www.gexf.net/1.2draft/gexf.xsd"')
        self.version = u'version="1.2">'
        self.gexf_graph = u'<graph mode="static" defaultedgetype="directed">'
        self.node_attributes_xml = u"""
            <attribute id="NodeType" title="[Schema] Type" type="string" />
            <attribute id="NodeTypeId" title="[Schema] Type Id" type="string"/>"""
 
        self.edge_attributes_xml = u"""
            <attribute id="RelationshipType" title="[Schema] Allowed Relationship" type="string" />
            <attribute id="RelationshipTypeId" title="[Schema] Allowed Relationship Id" type="string" />"""
        self.structure = \
u"""{0}
{1}
    {2}
        <attributes class="node">{3}
        </attributes>
        <attributes class="edge">{4}
        </attributes>
        <nodes>{5}
        </nodes>
        <edges>{6}
        </edges>
    </graph>
</gexf>"""
 
    def build_gexf(self):
        header = ' '.join([
            self.gexf,
            self.viz,
            self.xsi,
            self.schemas,
            self.version,
        ])
        node_types = self.divide_node_types()
        edge_types = self.divide_edge_types()
        node_attributes_xml, node_attributes = self.build_node_attr(node_types)
        edge_attributes_xml, edge_attributes = self.build_edge_attr(edge_types)
        nodes = self.build_nodes(node_attributes)
        edges = self.build_edges(edge_attributes)
        sylva_format = self.structure.format(
            self.xml_version,
            header,
            self.gexf_graph,
            node_attributes_xml,
            edge_attributes_xml,
            nodes,
            edges,
        )
        return sylva_format
 
    def build_nodes(self, node_attributes):
        nodes = ''
        for node, attrs in self.graph.nodes(data=True):
            nodes += u"""
            <node id="%s" label="%s" type="%s">
            <attvalues>""" % (
                str(attrs['id']),
                attrs['Name'],
                attrs['NodeType']
                )
            for key, value in attrs.iteritems():
                if key == 'id':
                    pass
                else:
                    nodes += u"""
                <attvalue for="%s" value="%s"/>""" % (
                        node_attributes[key],
                        value
                    )
            nodes += u"""
            </attvalues>
            </node>"""
        return nodes
 
    def build_node_attr(self, node_types):
        attribute_counter = 0
        node_attributes = {}
        for node_type, attrs in node_types.iteritems():
            for key, value in attrs.iteritems():
                if key not in node_attributes and key == 'NodeType':
                        node_attributes[key] = key
                elif key not in node_attributes and key == 'NodeTypeId':
                        node_attributes[key] = key
                elif key not in node_attributes:
                    node_attributes[key] = 'n' + str(attribute_counter)
                if key not in ['NodeType', 'NodeTypeId', 'id']:
                    self.node_attributes_xml += u"""
                <attribute id="%s" title="(%s) %s" type="string"/>""" % (
                        ('n' + str(attribute_counter).decode('utf-8')),
                        node_type,
                        key
                    )
                    attribute_counter += 1
        return self.node_attributes_xml, node_attributes
 
    def build_edges(self, edge_attributes):
        edges = ''
        edge_id = 0
        for edge in self.graph.edges(data=True):
            edges += u"""
            <edge id="%s" source="%s" target="%s" label="%s">
            <attvalues>""" % (
                str(edge_id),
                edge[0],
                edge[1],
                edge[2]['RelationshipType']
            )
            edge_id += 1
            for key, value in edge[2].iteritems():
                if key == 'id':
                    pass
                else:
                    edges += u"""
                <attvalue for="%s" value="%s"/>""" % (
                        edge_attributes[key],
                        value
                    )
            edges += u"""
            </attvalues>
            </edge>"""
        return edges
 
    def build_edge_attr(self, edge_types):
        attribute_counter = 0
        edge_attributes = {}
        for name, attrs in edge_types.iteritems():
            for key, value in attrs.iteritems():
                if key not in edge_attributes and key == 'RelationshipType':
                    edge_attributes[key] = key
                elif key not in edge_attributes and \
                        key == 'RelationshipTypeId':
                    edge_attributes[key] = key
                elif key not in edge_attributes:
                    edge_attributes[key] = 'r' + str(attribute_counter)
                if key not in ['RelationshipType', 'RelationshipTypeId', 'id']:
                    edge_attributes['key'] = 'r' + str(attribute_counter)
                    self.edge_attributes_xml += u"""
                <attribute id="%s" title="(%s) %s" type="string"/>""" % (
                        'r' + str(attribute_counter),
                        name,
                        key,
                    )
            attribute_counter += 1
        return self.edge_attributes_xml, edge_attributes
 
    def divide_node_types(self):
        node_types = {}
        for node, attrs in self.graph.nodes(data=True):
            if attrs['NodeType'] not in node_types:
                node_types[attrs['NodeType']] = attrs
            else:
                node_types[attrs['NodeType']].update(attrs)
        return node_types
 
    def divide_edge_types(self):
        edge_types = {}
        for s, t, attrs in self.graph.edges(data=True):
            if attrs['RelationshipType'] not in edge_types:
                edge_types[attrs['RelationshipType']] = attrs
            else:
                edge_types[attrs['RelationshipType']].update(attrs)
        return edge_types
 
    def write_gexf(self, filename):
        gexf = self.build_gexf().encode('utf-8')
        with open(filename, 'w') as f:
            f.write(gexf)