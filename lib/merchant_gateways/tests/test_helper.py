

from mock import Mock
#  CONSIDER  django-test-extensions needs to work w/o django
import unittest
from pprint import pformat
from decimal import Decimal


class MerchantGatewaysUtilitiesTestSuite(unittest.TestCase):

    def assert_success(self):
        #  TODO assert is_test
        self.assertTrue(isinstance(self.response, self.gateway_response_type()))
        self.assertTrue(self.response.success, 'Response should not fail: ' + pformat(self.response.__dict__))

    def assert_failure(self):
        self.assertTrue(isinstance(self.response, self.gateway_response_type()))
            #~ clean_backtrace do
        self.assertFalse(self.response.success, 'Response should fail: ' + pformat(self.response.__dict__))

    def assert_raises_(self, except_cls, callable_, *args, **kw):  #  CONSIDER  merge with django-test-extensions' assert_raises?
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
        nodes = tree.xpath(xpath, **kw)
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

    def assert_none(self, *args, **kwargs):
        "assert you ain't nothin'"

        return self.assertEqual(None, *args, **kwargs)

    def assert_equal(self, *args, **kwargs):
        'Assert that two values are equal'

        return self.assertEqual(*args, **kwargs)

    def assert_match_hash(self, reference, sample, diagnostic=''):
        if reference == sample:  return
        print dir(reference)
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


class MerchantGatewaysWebserviceTestSuite(object):

    def mock_get_webservice(self, returns):
        self.gateway.get_webservice = Mock(return_value=returns)

    def mock_post_webservice(self, returns):
        self.gateway.post_webservice = Mock(return_value=returns)


class MerchantGatewaysTestSuite( MerchantGatewaysUtilitiesTestSuite,
                                 MerchantGatewaysWebserviceTestSuite ):

    def setUp(self):
        self.gateway = self.gateway_type()(is_test=True, login='X', password='Y')
        self.gateway.gateway_mode = 'test'
        from decimal import Decimal
        self.amount = Decimal('100')  #  TODO  all are Currency type no exceptions
        self.options = dict(order_id=1)  #  TODO  change me to Harry Potter's favorite number & pass all tests
        from merchant_gateways.billing.credit_card import CreditCard

        self.credit_card = CreditCard( number='4242424242424242',
                                       month='12',  year='2090',
                                       card_type='V',
                                       first_name='Hermione', last_name='Granger' )

        self.subscription_id = '100748'  #  TODO  use or lose this

    class CommonTests:

        def gateway_response_type(self):
            return self.gateway_type().Response

        def test_successful_authorization(self):
            self.mock_webservice(self.successful_authorization_response())
            self.options['description'] = 'Chamber of Secrets'
            self.response = self.gateway.authorize(self.amount, self.credit_card, **self.options)

    # TODO        assert self.response.is_test
            self.assert_successful_authorization()
            self.assert_success()
            self.assert_equal(repr(True), repr(self.response.is_test))

        def test_failed_authorization(self):
            self.mock_webservice(self.failed_authorization_response())
            self.response = self.gateway.authorize(self.amount, self.credit_card, **self.options)
            self.assert_failure()
            self.assert_failed_authorization()
            self.assert_equal(repr(True), repr(self.response.is_test))

        def test_successful_purchase(self):
            self.mock_get_webservice(self.successful_purchase_response())
            self.response = self.gateway.purchase(self.amount, self.credit_card, **self.options)
            self.assert_successful_purchase()

nil = None # C-;

import re
def grep(string,list):
    expr = re.compile(string)
    for text in list:
        match = expr.search(text)
        if match != None:
            print match.string
