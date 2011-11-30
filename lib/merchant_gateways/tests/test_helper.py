
import unittest

from mock import Mock
#  CONSIDER  django-test-extensions needs to work w/o django
from pprint import pformat
from money import Money
import cgi


class MerchantGatewaysUtilitiesTestSuite(unittest.TestCase):
    '''
    This contains copies of test utilities found in `django-test-extensions <http://github.com/cuker/django-test-extensions>`_.
    '''

    def assert_contains(self, needle, haystack, diagnostic=''):
        'Assert that one value (the hasystack) contains another value (the needle)'
        diagnostic = diagnostic + "\nContent should contain `%s' but doesn't:\n%s" % (needle, haystack)
        diagnostic = diagnostic.strip()
        return self.assert_(needle in haystack, diagnostic)

    def assert_none(self, *args, **kwargs):
        "assert you ain't nothin'"

        return self.assertEqual(None, *args, **kwargs)

    def assert_empty(self, *args, **kwargs):
        "assert you have nothin'"

        if args[0] != '':
            return self.assertEqual(None, *args, **kwargs)

    def assert_equal(self, *args, **kwargs):
        'Assert that two values are equal'

        return self.assertEqual(*args, **kwargs)

    def assert_equal_set(self, reference, sample, *args, **kwargs):
        'Assert that two values are equal'

        return self.assertEqual(set(reference), set(sample), *args, **kwargs)

    def assertEqual(self, first, second, message=''):
        'NOTE Python 3 fixes this: http://docs.python.org/dev/py3k/library/unittest.html#unittest.TestCase.longMessage '

        if first != second:
            self.assertTrue( first == second,
                          (message + ('\n%r != %r' % (first, second))).lstrip() )

    def assert_raises(self, except_cls, callable_, *args, **kw):  #  CONSIDER  merge with django-test-extensions' assert_raises?
        try:
            callable_(*args, **kw)
            assert False, "Callable should raise an exception"  #  TODO  assertFalse, with complete diagnostics
        except except_cls, e:
            return e

    def assert_xml(self, xml, xpath, **kw):
        'Check that a given extent of XML or HTML contains a given XPath, and return its first node'

        if hasattr(xpath, '__call__'):
            return self.assert_xml_tree(xml, xpath, **kw)

        tree = self._xml_to_tree(xml, forgiving=kw.get('forgiving', False))
        nodes = tree.xpath(xpath, **kw)  #  TODO  this could automatically do namespaces
        self.assertTrue(len(nodes) > 0, xpath + ' should match ' + self._xml)
        node = nodes[0]
        if kw.get('verbose', False):  self.reveal_xml(node)  #  "here have ye been? What have ye seen?"--Morgoth
        return node

    def assert_xml_tree(self, sample, block, **kw):  #  TODO  less sucktacular name!
        from lxml.builder import ElementMaker # TODO document we do lxml only !
        doc = block(ElementMaker())   #  TODO  or just pass in an element maker
        path = self._convert_nodes_to_nested_path(doc)
        self.assert_xml(sample, path, **kw)  #  this checks nesting
          #  CONSIDER  now detect which parts failed!!!
        doc_order = -1

        for node in doc.xpath('//*'):
            doc_order = self._assert_xml_node(doc_order, kw, node, sample)
              # TODO  amalgamate all errors - don't just kack on the first one!

    def _assert_xml_node(self, doc_order, kw, node, sample):
        nodes = [self._node_to_predicate(a) for a in node.xpath('ancestor-or-self::*')]
        path = '//' + '/descendant::'.join(nodes)
        node = self.assert_xml(sample, path, **kw)
        location = len(node.xpath('preceding::*'))
        self.assertTrue(doc_order <= location, 'Node out of order! ' + path)
        return location

    def _convert_nodes_to_nested_path(self, node):
        path = 'descendant-or-self::' + self._node_to_predicate(node)
        nodes = node.xpath('*')
        paths = [ '[ ' + self._convert_nodes_to_nested_path(n) + ' ]' for n in nodes ]
        path += ''.join(paths)
        return path

    def _node_to_predicate(self, node):
        path = node.tag

        for key, value in node.attrib.items():
            path += '[ contains(@%s, "%s") ]' % (key, value) # TODO  warn about (then fix) quote escaping bugs

        if node.text:  #  TODO  document only leaf nodes may check for text or attributes
            path += '[ contains(text(), "%s") ]' % node.text

        return path

    def _xml_to_tree(self, xml, forgiving=False):
        from lxml import etree
        self._xml = xml

        if not isinstance(xml, basestring):
            self._xml = str(xml)  #  CONSIDER  tostring
            return xml

        if '<html' in xml[:200]:
            parser = etree.HTMLParser(recover=forgiving) #  ERGO uh, strict?
            return etree.HTML(str(xml), parser)
        else:
            parser = etree.XMLParser(recover=forgiving)  #  TODO  NOT forgiving!!!
            return etree.XML(str(xml))

    def assert_xml_text(self, xml, path, text):
        path += '[ contains(text(), "%s") ]' % text  #  TODO  replace many 'text() =' with this; use XPath substitutions so " and ' cause no trouble
        return self.assert_xml(xml, path)

    def reveal_xml(self, node):
        'Spews an XML node as source, for diagnosis'

        from lxml import etree
        print etree.tostring(node, pretty_print=True)  #  CONSIDER  does pretty_print work? why not?

    def deny_xml(self, xml, xpath):
        'Check that a given extent of XML or HTML does not contain a given XPath'

        tree = self._xml_to_tree(xml)
        nodes = tree.xpath(xpath)
        self.assertEqual(0, len(nodes), xpath + ' should not appear in ' + self._xml)

    def assert_match_xml(self, reference, sample):
        import re
        reference = re.sub(r'\n\s*', '\n', reference).strip()
        sample = re.sub(r'\n\s*', '\n', sample).strip()
        self.assertEqual(reference, sample, "\n%s\nshould match:%s" % (reference, sample))  #  CONSIDER  use XPath to rotorouter the two samples!

    def assert_params(self, params, **dict):  #  ERGO  put me in django-test-extensions!
        qsparams = cgi.parse_qs(params)

        for k,v in qsparams.items():
            if len(v) == 1:
                qsparams[k] = v[0] # easier to manipulate, because most real-life params are singular

        if dict:  #  assert_params optionally does not check any params
            self.assert_dict_contains(qsparams, **dict)  #  ERGO  better diagnostic, as usual!

        return qsparams

    def assert_dict_contains(self, dict, **elements):  #  ERGO  promote me & merge with assert_match_dict
        assert elements, 'assert_dict_contains works best with "kwargs"!'

        for k,v in elements.items():
            self.assert_equal(v, dict.get(k, not v), 'for key `%s`' % k)

    #@deprecated
    def assert_match_hash(self, reference, sample, diagnostic=''):
        self.assert_match_dict(reference, sample, diagnostic)

    def assert_match_dict(self, reference, sample, diagnostic=''):
        if reference == sample:  return
        reference = reference.copy()
        sample = sample.copy()
        from pprint import pformat

        for key, value in reference.items():
            if value == sample.get(key, not(value)):
                reference.pop(key)
                sample.pop(key)

        diagnostic = ( 'hashes should not differ by these items:' +
                       '\n%s\n!=\n%s\n%s' %
                      ( pformat(reference),
                        pformat(sample),
                        diagnostic or '' ) )

        diagnostic = diagnostic.strip()
        self.assert_equal( reference, sample, diagnostic )

    def convert_xml_to_element_maker(self, thang):
        'script that coverts XML to its ElementMaker notation'

        from lxml import etree
        doc = etree.XML(thang)
        return self._convert_child_nodes(doc)

    def _convert_child_nodes(self, node, depth=0):
        code = '\n' + ' ' * depth * 2 + 'XML.' + node.tag + '('
        children = node.xpath('*')

        if node.text and not re.search('^\s*$', node.text):
            code += repr(node.text)
            if node.attrib or children:  code += ', '

        if children:
            child_nodes = [ self._convert_child_nodes(n, depth + 1) for n in children ]
            code += (',' ).join(child_nodes)
            if node.attrib:  code += ', '

        if node.attrib:
            attribs = [ '%s=%r' % (kv) for kv in node.attrib.items() ]
            code += ', '.join(attribs)

        code += ')'
        return code


class MerchantGatewaysWebserviceTestSuite(object):

    def mock_gateway_webservice(self, returns, lamb):
        self.gateway.post_webservice = Mock(return_value=returns)  #  TODO  stop relying on this member!
        self.response = lamb()
        #self.response = self.gateway.response  #  TODO  take out redundant occurences of this


class MerchantGatewaysTestSuite( MerchantGatewaysUtilitiesTestSuite,
                                 MerchantGatewaysWebserviceTestSuite ):

    def setUp(self):
        self.gateway = self.gateway_type()(is_test=True, login='X', password='Y')
        self.gateway.gateway_mode = 'test'
        from decimal import Decimal
        self.money = Money('100', 'USD')
        self.options = dict(order_id=1)  #  TODO  change me to Harry Potter's favorite number & pass all tests
        from merchant_gateways.billing.credit_card import CreditCard

        self.credit_card = CreditCard( number='4242424242424242',
                                       month='12',  year='2090',
                                       card_type='V',
                                       verification_value='456',
                                       first_name='Hermione', last_name='Granger' )

        self.subscription_id = '100748'  #  TODO  use or lose this
        getattr(self, 'set_gateway_up', lambda: None)() #  CONSIDER explain to Python-land this is what virtual methods are FOR!!!
        #self.set_gateway_up()

#    def set_gateway_up(self):  pass  #  oh yeah!

    def assert_success(self):
        #  TODO assert is_test
        self.assertTrue(isinstance(self.response, self.gateway_response_type()), str(self.response))
        self.assertTrue(self.response.success, 'Response should not fail: ' + pformat(self.response.__dict__))

    def assert_failure(self):
        self.assertTrue(isinstance(self.response, self.gateway_response_type()), str(self.response))
            #~ clean_backtrace do
        self.assertFalse(self.response.success, 'Response should fail: ' + pformat(self.response.__dict__))


    class CommonTests:  #  CONSIDER  move us to gateway_test.py?

        def gateway_response_type(self):
            return self.gateway_type().Response

        def test_successful_authorization(self):
            '''All gateways authorize with these inputs and outputs'''

            self.options['description'] = 'Chamber of Secrets'
            
            self.mock_gateway_webservice(self.successful_authorization_response(),
                lambda: self.gateway.authorize(self.money, self.credit_card, **self.options) )
            
            assert self.response
            #self.response = self.gateway.response
            assert self.response.is_test
            self.assert_success()
            self.assert_successful_authorization()

        def test_failed_authorization(self):
            self.mock_gateway_webservice( self.failed_authorization_response(),
                lambda:  self.gateway.authorize(self.money, self.credit_card, **self.options) )

            self.response = self.gateway.response
            assert self.response.is_test
            self.assert_failure()
            self.assert_failed_authorization()

        def test_successful_purchase(self):
            self.mock_gateway_webservice(self.successful_purchase_response(),
                lambda: self.gateway.purchase(self.money, self.credit_card, **self.options) )
            
            assert self.response
            #self.response = self.gateway.response  #  CONSIDER move inside ??
            assert self.response.is_test
            self.assert_success()
            self.assert_successful_purchase()

nil = None # C-;

import re
def grep(string,list):
    expr = re.compile(string)
    for text in list:
        match = expr.search(text)
        if match != None:
            yield match.string
