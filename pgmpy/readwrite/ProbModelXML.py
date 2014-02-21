"""
ProbModelXML: http://leo.ugr.es/pgm2012/submissions/pgm2012_submission_43.pdf

For the student example the ProbModelXML file should be:

<?xml version=“1.0” encoding=“UTF-8”?>
<ProbModelXML formatVersion=“1.0”>
    <ProbNet type=BayesianNetwork >
        <AdditionalConstraints />
        <Comment>
            Student example model from Probabilistic Graphical Models: Principles and Techniques by Daphne Koller
        </Comment>
        <Language>
            English
        </Language>
        <AdditionalProperties />
        <Variables>
            <Variable name="intelligence" type="FiniteState" role="Chance">
                <Comment />
                <Coordinates />
                <AdditionalProperties />
                <States>
                    <State name="smart"><AdditionalProperties /></State>
                    <State name="dumb"><AdditionalProperties /></State>
                </States>
            </Variable>
            <Variable name="difficulty" type="FiniteState" role="Chance">
                <Comment />
                <Coordinates />
                <AdditionalProperties />
                <States>
                    <State name="difficult"><AdditionalProperties /></State>
                    <State name="easy"><AdditionalProperties /></State>
                </States>
            </Variable>
            <Variable name="grade" type="FiniteState" role="Chance">
                <Comment />
                <Coordinates />
                <AdditionalProperties />
                <States>
                    <State name="grade_A"><AdditionalProperties /></State>
                    <State name="grade_B"><AdditionalProperties /></State>
                    <State name="grade_C"><AdditionalProperties /></State>
                </States>
            </Variable>
            <Variable name="recommendation_letter" type="FiniteState" role="Chance">
                <Comment />
                <Coordinates />
                <AdditionalProperties />
                <States>
                    <State name="good"><AdditionalProperties /></State>
                    <State name="bad"><AdditionalProperties /></State>
                </States>
            </Variable>
            <Variable name="SAT" type="FiniteState" role="Chance">
                <Comment />
                <Coordinates />
                <AdditionalProperties />
                <States>
                    <State name="high"><AdditionalProperties /></State>
                    <State name="low"><AdditionalProperties /></State>
                </States>
            </Variable>
        </Variables>
        <Links>
            <Link var1="difficulty" var2="grade" directed=1>
                <Comment>Directed Edge from difficulty to grade</Comment>
                <Label>diff_to_grad</Label>
                <AdditionalProperties />
            </Link>
            <Link var1="intelligence" var2="grade" directed=1>
                <Comment>Directed Edge from intelligence to grade</Comment>
                <Label>intel_to_grad</Label>
                <AdditionalProperties />
            </Link>
            <Link var1="intelligence" var2="SAT" directed=1>
                <Comment>Directed Edge from intelligence to SAT</Comment>
                <Label>intel_to_sat</Label>
                <AdditionalProperties />
            </Link>
            <Link var1="grade" var2="recommendation_letter" directed=1>
                <Comment>Directed Edge from grade to recommendation_letter</Comment>
                <Label>grad_to_reco</Label>
                <AdditionalProperties />
            </Link>
        </Links>
        <Potential type="Table" role="ConditionalProbability" label=string>
            <Comment>CPDs in the form of table</Comment>
            <AdditionalProperties />
            <!--
                There is no specification in the paper about how the tables should be represented.
            -->
        </Potential>
    </ProbNet>
    <Policies />
    <InferenceOptions />
    <Evidence>
        <EvidenceCase>
            <Finding variable=string state=string stateIndex=integer numericValue=number/>
        </EvidenceCase>
    </Evidence>
</ProbModelXML>
"""
import warnings
import networkx as nx
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            print("Failed to import ElementTree from any known place")

warnings.warn("Not Complete. Please use only for reading and writing Bayesian Models.")


def generate_probmodelxml(G, encoding='utf-8', prettyprint=True,
                          language='English', comment=None):
    writer = ProbModelXMLWriter(G, encoding=encoding, prettyprint=prettyprint,
                                language=language, comment=comment)
    for line in str(writer).splitlines():
        yield line


class ProbModelXMLWriter(object):
    def __init__(self, network, encoding='utf-8', prettyprint=True,
                 language='English', comment=None):
        #TODO: add policies, InferenceOptions, Evidence
        self.encoding = encoding
        self.prettyprint = prettyprint
        self.xml = etree.Element("ProbModelXML", attrib={'formatVersion': '1.0'})
        self.probnet = etree.SubElement(self.xml, 'ProbNet')
        self.variables = etree.SubElement(self.probnet, 'Variables')
        self.links = etree.SubElement(self.probnet, 'Links')
        self.potential = etree.SubElement(self.probnet, 'Potential')
        etree.SubElement(self.probnet, 'Language').text = language
        etree.SubElement(self.probnet, 'Comment').text = comment

        if isinstance(network, nx.DiGraph):
            self.probnet.attrib['type'] = 'BayesianNetwork'
        elif isinstance(network, nx.Graph):
            self.probnet.attrib['type'] = 'MarkovNetwork'
        self.add_network(network)

    def __str__(self):
        return etree.tostring(self.xml, encoding=self.encoding, prettyprint=self.prettyprint)

    def add_network(self, network):
        for node in network.nodes():
            self.add_variable(node, type='FiniteStatae', role='Chance',
                              states=network.get_states(node))
            self.add_potential(node)
        for edge in network.edges():
            self.add_link(edge, is_directed='1' if isinstance(network, nx.DiGraph) else '0')

    def add_policies(self):
        pass

    def add_inference_options(self):
        pass

    def add_evidence(self):
        pass

    def add_additional_constraints(self):
        pass

    def add_comment(self, comment):
        self.xml.xpath('//ProbNet/Comment')[0].text = comment

    def add_language(self, language):
        self.xml.xpath('//Language')[0].text = language

    def add_additional_properties(self, **kwargs):
        add_prop = etree.SubElement(self.xml, 'AdditionalProperties')
        for key, value in kwargs:
            etree.SubElement(add_prop, 'Property', attrib={'name': key, 'value': value})

    def add_state(self, state, node, **kwargs):
        states = self.xml.xpath('//Variable[@name="' + node + '"]/States')[0]
        s = etree.SubElement(states, 'State', attrib={'name': state})
        add_prop = etree.SubElement(s, 'AdditionalProperties')
        for key, value in kwargs:
            etree.SubElement(add_prop, 'Property', attrib={'name': key, 'value': value})

    def add_variable(self, name, type='FiniteState', role='Chance', comment=None,
                      coordinates=None, states=None, **kwargs):
        #TODO: Add feature for accepting additional properties of states.
        variable = etree.SubElement(self.variables, 'Variable', attrib={'name': name,
                                                                        'type': type,
                                                                        'role': role})
        etree.SubElement(variable, 'Comment').text = comment
        etree.SubElement(variable, 'Coordinates').text = coordinates
        add_prop = etree.SubElement(variable, 'AdditionalProperties')
        for key, value in kwargs.items():
            etree.SubElement(add_prop, 'Property', attrib={'name': key, 'value': value})
        state = variable.SubElement(variable, 'States')
        for s in states:
            etree.SubElement(state, 'State', attrib={'name': s}).append(etree.Element('AdditionalProperties'))

    def add_link(self, edge, comment=None, label=None, is_directed='0', **kwargs):
        link = etree.SubElement(self.links, 'Link', attrib={'var1': edge[0], 'var2': edge[1],
                                                            'directed': is_directed})
        etree.SubElement(link, 'Comment').text = comment
        etree.SubElement(link, 'Label').text = label
        add_prop = etree.SubElement(link, 'AdditionalProperties')
        for key, value in kwargs.items():
            etree.SubElement(add_prop, 'Property', attrib={'name': key, 'value': value})

    def add_potential(self):
        pass

    def dump(self, stream):
        if self.prettyprint:
            self.indent(self.xml)
        document = etree.ElementTree(self.xml)
        header = '<?xml version="1.0" encoding="%s"?>' % self.encoding
        stream.write(header.encode(self.encoding))
        document.write(stream, encoding=self.encoding)

    def indent(self, elem, level=0):
        # in-place prettyprint formatter
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class ProbModelXMLReader(object):
    def __init__(self, path=None, string=None):
        if path is not None:
            self.xml = etree.ElementTree(file=path)
        elif string is not None:
            self.xml = etree.fromstring(string)
        else:
            raise ValueError("Must specify either 'path' or 'string' as kwarg.")
        #TODO: add parsing code 

@open_file(1, mode='wb')
def write_probmodelxml(model, path, encoding='utf-8', prettyprint=True):
    pass