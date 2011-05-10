from __future__ import with_statement

from lxml.builder import ElementMaker
XML = ElementMaker()

from merchant_gateways.billing.common import xmltodict, dicttoxml, ET, XMLDict

class CybersourceMockServer(object):
    namespace = 'urn:schemas-cybersource-com:transaction-data-1.59'
    
    def __init__(self, failure=None):
        self.failure = failure

    def __call__(self, url, msg, headers):
        if self.failure:
            return self.failure
        self.validate_request(msg)
        msg = msg.replace('xmlns="%s"' % self.namespace, '')
        data = xmltodict(ET.fromstring(msg))
        response = self.receive(data)
        ret = ET.tostring(self.send(data, response))
        self.validate_response(ret)
        return ret
    
    def validate_request(self, msg):
        from lxml import etree
        from os import path
        location = path.join(path.dirname(__file__), 'schemas', 'cybersource', 'CyberSourceTransaction_1.59.xsd')
        schema_doc = etree.XMLSchema(etree.parse(open(location, 'r')))
        xml = etree.XML(msg)
        try:
            schema_doc.assertValid(xml)
        except:
            print msg
            raise

    def validate_response(self, msg):
        from lxml import etree
        from os import path
        location = path.join(path.dirname(__file__), 'schemas', 'cybersource', 'CyberSourceTransaction_1.59.xsd')
        schema_doc = etree.XMLSchema(etree.parse(open(location, 'r')))
        xml = etree.XML(msg)
        schema_doc.assertValid(xml)

    def receive(self, data):
        for key in ['ccAuthService', 'ccCaptureService', 'ccCreditService', 'ccAuthReversalService']:
            if key in data:
                return getattr(self, key.lower())(data)
        assert False, 'Unrecognized action'

    def send(self, data, response):
        root = ET.Element('replyMessage')
        root.attrib['xmlns'] = self.namespace
        dicttoxml(response, root)
        return root
    
    def ccauthservice(self, data):
        response = XMLDict([('merchantReferenceCode', data['merchantReferenceCode']),
                            ('requestID', '0305782650000167905080'),
                            ('decision', 'ACCEPT'),
                            ('reasonCode', '100'),
                            ('requestToken', 'AA4JUrWguaLLQxMUGwxSWVdPS1BIRk5IMUwA2yCv'),
                            ('purchaseTotals', {'currency':data['purchaseTotals']['currency']}),
                            ('ccAuthReply', XMLDict([('reasonCode', '100'),
                                                     ('amount', data['purchaseTotals']['grandTotalAmount']),
                                                     ('authorizationCode', '123456'),
                                                     ('avsCode', 'Y'),
                                                     ('avsCodeRaw', 'YYY'),
                                                     ('processorResponse', 'A'),
                                                     ('accountBalance', data['purchaseTotals']['grandTotalAmount']),
                                                    ])),
                           ])
        return response
    
    def cccaptureservice(self, data):
        response = XMLDict([('merchantReferenceCode', data['merchantReferenceCode']),
                            ('requestID', '0305782650000167905080'),
                            ('decision', 'ACCEPT'),
                            ('reasonCode', '100'),
                            ('requestToken', 'AA4JUrWguaLLQxMUGwxSWVdPS1BIRk5IMUwA2yCv'),
                            ('purchaseTotals', {'currency':data['purchaseTotals']['currency']}),
                            ('ccCaptureReply', XMLDict([('reasonCode', '100'),
                                                        ('amount', data['purchaseTotals']['grandTotalAmount']),
                                                        ('reconciliationID', '1094820975023470'),
                                                    ])),
                           ])
        return response
    
    def cccreditservice(self, data):
        response = XMLDict([('merchantReferenceCode', data['merchantReferenceCode']),
                            ('requestID', '0305782650000167905080'),
                            ('decision', 'ACCEPT'),
                            ('reasonCode', '100'),
                            ('requestToken', 'AA4JUrWguaLLQxMUGwxSWVdPS1BIRk5IMUwA2yCv'),
                            ('purchaseTotals', {'currency':data['purchaseTotals']['currency']}),
                            ('ccCreditReply', XMLDict([('reasonCode', '100'),
                                                        ('amount', data['purchaseTotals']['grandTotalAmount']),
                                                        ('reconciliationID', '1094820975023470'),
                                                    ])),
                           ])
        return response
    
    def ccauthreversalservice(self, data):
        response = XMLDict([('merchantReferenceCode', data['merchantReferenceCode']),
                            ('requestID', '0305782650000167905080'),
                            ('decision', 'ACCEPT'),
                            ('reasonCode', '100'),
                            ('requestToken', 'AA4JUrWguaLLQxMUGwxSWVdPS1BIRk5IMUwA2yCv'),
                            ('purchaseTotals', {'currency':data['purchaseTotals']['currency']}),
                            ('ccAuthReversalReply', XMLDict([('reasonCode', '100'),
                                                        ('amount', data['purchaseTotals']['grandTotalAmount']),
                                                        ('authorizationCode', '1094820975023470'),
                                                    ])),
                           ])
        return response


