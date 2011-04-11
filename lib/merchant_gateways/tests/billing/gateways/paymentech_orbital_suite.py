from __future__ import with_statement

from merchant_gateways.tests.test_helper import MerchantGatewaysWebserviceTestSuite
from lxml.builder import ElementMaker
XML = ElementMaker()
from merchant_gateways.billing.gateways.gateway import xStr

class MerchantGatewaysPaymentechOrbitalSuite(MerchantGatewaysWebserviceTestSuite):

    def set_gateway_up(self):
        self.options['merchant_id'] = 'Anglia 105E'
        self.assemble_billing_address()

    def assemble_billing_address(self):
        self.options.update({
            'order_id': '1',
            'description': 'Time-Turner',
            'email': 'hgranger@hogwarts.edu',
            'customer': '947', #  TODO  test this going through
            'ip': '192.168.1.1', #  TODO  test this going through
            })
        billing_address = {
            'address1': '444 Main St.',
            'address2': 'Apt 2',
            'company': 'ACME Software', #  CONSIDER  Orbital seems to have no slot for the company
            'phone': '222-222-2222',
            'zip': '77777',
            'city': 'Dallas',
            'country': 'US',  #  TODO  must be US not USA at the interface!
            'state': 'TX'
            }
        self.options['billing_address'] = billing_address
        return billing_address

    def successful_purchase_response(self):  #  TODO  get a real one!
        return self.successful_authorization_response()

    def successful_authorization_response(self):

#        response = '''<?xml version="1.0" encoding="UTF-8"?> <Response> <ACResponse> <CommonDataResponse> <CommonMandatoryResponse HcsTcsInd="T" LangInd="00" MessageType="A" TzCode="705" Version="2"> <MerchantID>123456789012</MerchantID> <TerminalID>001</TerminalID> <TxRefNum>128E6C6A4FC6D4119A3700D0B706C51EE26DF570</TxRefNum> <TxRefIdx>0</TxRefIdx> <OrderNumber>1234567890123456</OrderNumber> <RespTime>10012001120003</RespTime> <ProcStatus>0</ProcStatus> <ApprovalStatus>1</ApprovalStatus> <ResponseCodes> <AuthCode>tntC09</AuthCode> <RespCode>00</RespCode> <HostRespCode>00</HostRespCode> <CVV2RespCode>M</CVV2RespCode> <HostCVV2RespCode>M</HostCVV2RespCode> <AVSRespCode>H</AVSRespCode> <HostAVSRespCode>Y</HostAVSRespCode> </ResponseCodes> </CommonMandatoryResponse> <CommonOptionalResponse> <AccountNum>4012888888881</AccountNum> <RespDate>010801</RespDate> <CardType>VI</CardType> <ExpDate>200512</ExpDate> <CurrencyCd>840</CurrencyCd> </CommonOptionalResponse> </CommonDataResponse> <AuthResponse> <AuthMandatoryResponse/> <AuthOptionalResponse> <POSEntryMode>01</POSEntryMode> <MISCData> <ActualRespCd>00 </ActualRespCd> </MISCData> <NetworkData> <AuthNetwkID>01</AuthNetwkID> </NetworkData> <VisaCard> <CPSData> <AuthCharInd>V</AuthCharInd> <ValidationCd>JU9E</ValidationCd> </CPSData> <AuthSource AuthSrc="5"/> <VisaCommCard VCC="S"/> </VisaCard> </AuthOptionalResponse> </AuthResponse> </ACResponse> </Response>'''

        #$print self.convert_xml_to_element_maker(response)

        alternate_TODO = XML.Response(
          XML.ACResponse(
            XML.CommonDataResponse(
              XML.CommonMandatoryResponse(
                XML.MerchantID('123456789012'),
                XML.TerminalID('001'),
                XML.TxRefNum('128E6C6A4FC6D4119A3700D0B706C51EE26DF570'),
                XML.TxRefIdx('0'),
                XML.OrderNumber('1234567890123456'),
                XML.RespTime('10012001120003'),
                XML.ProcStatus('0'),
                XML.ApprovalStatus('1'),
                XML.ResponseCodes(
                  XML.AuthCode('tntC09'),
                  XML.RespCode('00'),
                  XML.HostRespCode('00'),
                  XML.CVV2RespCode('M'),
                  XML.HostCVV2RespCode('M'),
                  XML.AVSRespCode('H'),
                  XML.HostAVSRespCode('Y')), HcsTcsInd='T', LangInd='00', MessageType='A', TzCode='705', Version='2'),
              XML.CommonOptionalResponse(
                XML.AccountNum('4012888888881'),
                XML.RespDate('010801'),
                XML.CardType('VI'),
                XML.ExpDate('200512'),
                XML.CurrencyCd('840'))),
            XML.AuthResponse(
              XML.AuthMandatoryResponse(),
              XML.AuthOptionalResponse(
                XML.POSEntryMode('01'),
                XML.MISCData(
                  XML.ActualRespCd('00 ')),
                XML.NetworkData(
                  XML.AuthNetwkID('01')),
                XML.VisaCard(
                  XML.CPSData(
                    XML.AuthCharInd('V'),
                    XML.ValidationCd('JU9E')),
                  XML.AuthSource(AuthSrc='5'),
                  XML.VisaCommCard(VCC='S'))))))

        return xStr(XML.Response(
                      XML.NewOrderResp(
                        XML.IndustryType(),
                        XML.MessageType('AC'),
                        XML.MerchantID('000000'),
                        XML.TerminalID('000'),
                        XML.CardBrand('MC'),
                        XML.AccountNum('5454545454545454'),
                        XML.OrderID('1'),
                        XML.TxRefNum('4A785F5106CCDC41A936BFF628BF73036FEC5401'),
                        XML.TxRefIdx('1'),
                        XML.ProcStatus('0'),
                        XML.ApprovalStatus('1'),
                        XML.RespCode('00'),
                        XML.AVSRespCode('B '),
                        XML.CVV2RespCode('M'),
                        XML.AuthCode('tst554'),
                        XML.RecurringAdviceCd(),
                        XML.CAVVRespCode(),
                        XML.StatusMsg('Approved'),
                        XML.RespMsg(),
                        XML.HostRespCode('100'),
                        XML.HostAVSRespCode('I3'),
                        XML.HostCVV2RespCode('M'),
                        XML.CustomerRefNum('2145108'),
                        XML.CustomerName('JOE SMITH'),
                        XML.ProfileProcStatus('0'),
                        XML.CustomerProfileMessage('Profile Created'),
                        XML.RespTime('121825'))))

    def failed_authorization_response(self):
        return xStr(XML.Response(
                      XML.QuickResp(
                        XML.ProcStatus('841'),
                        XML.StatusMsg('Error validating card/account number range'),
                        XML.CustomerBin(),
                        XML.CustomerMerchantID(),
                        XML.CustomerName(),
                        XML.CustomerRefNum(),
                        XML.CustomerProfileAction(),
                        XML.ProfileProcStatus('9576'),
                        XML.CustomerProfileMessage('Profile: Unable to Perform Profile Transaction. The Associated Transaction Failed. '),
                        XML.CustomerAddress1(),
                        XML.CustomerAddress2(),
                        XML.CustomerCity(),
                        XML.CustomerState(),
                        XML.CustomerZIP(),
                        XML.CustomerEmail(),
                        XML.CustomerPhone(),
                        XML.CustomerProfileOrderOverrideInd(),
                        XML.OrderDefaultDescription(),
                        XML.OrderDefaultAmount(),
                        XML.CustomerAccountType(),
                        XML.CCAccountNum(),
                        XML.CCExpireDate(),
                        XML.ECPAccountDDA(),
                        XML.ECPAccountType(),
                        XML.ECPAccountRT(),
                        XML.ECPBankPmtDlv(),
                        XML.SwitchSoloStartDate(),
                        XML.SwitchSoloIssueNum())))

    def assert_xml_schema(self, xml, schema_file):  #  ERGO  merge with assert_schema
        from lxml import etree

        with open(schema_file, 'r') as xsd:
            self._xmlschema_doc = etree.parse(xsd)

        xmlschema = etree.XMLSchema(self._xmlschema_doc)
        root = etree.XML(xml)
        xmlschema.assertValid(root)

    def assert_gateway_message_schema(self, message, schema_file):
        from os import path
        here = path.dirname(__file__)
        there = path.join(here, 'schemas', 'paymentech_orbital', schema_file)
        self.assert_xml_schema(message, there)

from merchant_gateways.billing.common import xmltodict, dicttoxml, ET, XMLDict

class PaymentechOrbitalMockServer(object):
    def __init__(self, failure=None):
        self.failure = failure

    def __call__(self, url, msg, headers):
        if self.failure:
            return self.failure
        self.validate_request(msg)
        data = xmltodict(ET.fromstring(msg))
        response = self.receive(data)
        ret = ET.tostring(self.send(data, response))
        self.validate_response(ret)
        return ret
    
    def validate_request(self, msg):
        from lxml import etree
        from os import path
        location = path.join(path.dirname(__file__), 'schemas', 'paymentech_orbital', 'Request_PTI50.xsd')
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
        location = path.join(path.dirname(__file__), 'schemas', 'paymentech_orbital', 'Response_PTI50.xsd')
        schema_doc = etree.XMLSchema(etree.parse(open(location, 'r')))
        xml = etree.XML(msg)
        schema_doc.assertValid(xml)

    def receive(self, data):
        for key in ['NewOrder', 'Profile', 'MarkForCapture', 'Reversal']:
            if key in data:
                return getattr(self, key.lower())(data[key])
        assert False, 'Unrecognized action'

    def send(self, data, response):
        root = ET.Element('Response')
        dicttoxml(response, root)
        return root

    def common_response(self, data):
        return XMLDict([('IndustryType', data['IndustryType']),
                        ('MessageType', data['MessageType']),
                        ('MerchantID', data['MerchantID']),
                        ('TerminalID', data['TerminalID']),])
    
    def reversal(self, data):
        response = XMLDict([('MerchantID', data['MerchantID']),
                            ('TerminalID', data['TerminalID']),
                             ('OrderID', data.get('OrderID', '')),
                             ('TxRefNum', '4A785F5106CCDC41A936BFF628BF73036FEC5401'),
                             ('TxRefIdx', '1'),
                             ('OutstandingAmt', '0'),
                             ('ProcStatus','0'),
                             ('StatusMsg', 'Approved'),
                             ('RespTime', '121825'),])
        return {'ReversalResp':response}
    
    def markforcapture(self, data):
        response = XMLDict([('MerchantID', data['MerchantID']),
                            ('TerminalID', data['TerminalID']),
                             ('OrderID', data.get('OrderID', '')),
                             ('TxRefNum', '4A785F5106CCDC41A936BFF628BF73036FEC5401'),
                             ('TxRefIdx', '1'),
                             ('Amount', data.get('Amount')),
                             ('ProcStatus','0'),
                             ('StatusMsg', 'Approved'),
                             ('RespTime', '121825'),
                             ('ApprovalStatus', '1'),
                             ('RespCode', '00'),
                             ('AVSRespCode', 'B'),
                             ('AuthCode', 'tst554'),
                             ('RespMsg', None),
                             ('HostRespCode', '100'),
                             ('HostAVSRespCode', 'I3'),])
        return {'MarkForCaptureResp':response}
    
    def neworder(self, data):
        response = self.common_response(data)
        if data['MessageType'] in ('A', 'AC'):
            assert data.get('AccountNum') or data.get('CustomerRefNum')
        elif data['MessageType'] in ('FC', 'R'):
            assert data.get('TxRefNum')
        else:
            assert False, 'Invalid Message Type: %s' % data['MessageType']
        response.update(XMLDict([('CardBrand', 'MC'),
                                 ('AccountNum', data.get('AccountNum')),
                                 ('OrderID', data.get('OrderID', '')),
                                 ('TxRefNum', '4A785F5106CCDC41A936BFF628BF73036FEC5401'),
                                 ('TxRefIdx', '1'),
                                 ('ProcStatus','0'),
                                 ('ApprovalStatus', '1'),
                                 ('RespCode', '00'),
                                 ('AVSRespCode', 'B'),
                                 ('CVV2RespCode', 'M'),
                                 ('AuthCode', 'tst554'),
                                 ('RecurringAdviceCd', None),
                                 ('CAVVRespCode', None),
                                 ('StatusMsg', 'Approved'),
                                 ('RespMsg', None),
                                 ('HostRespCode', '100'),
                                 ('HostAVSRespCode', 'I3'),
                                 ('HostCVV2RespCode', 'M'),
                                 ('CustomerRefNum', '2145108'),
                                 ('CustomerName', data.get('AVSname')),
                                 ('ProfileProcStatus', '0'),
                                 ('CustomerProfileMessage', 'Profile Created'),
                                 ('RespTime', '121825'),
                                 ('PartialAuthOccurred', ''),
                                 ('RequestedAmount', ''),
                                 ('RedeemedAmount', ''),
                                 ('RemainingBalance', ''),
                                 ('CountryFraudFilterStatus', ''),
                                 ('IsoCountryCode', data.get('AVScountryCode', '')),]))
        return {'NewOrderResp':response}
    
    def profile(self, data):
        response = XMLDict([('CustomerBin', data['CustomerBin']),
                            ('CustomerMerchantID', data['CustomerMerchantID']),
                            ('CustomerName', data['CustomerName']),
                            ('CustomerRefNum', 'CUSTOMERREFNUM'),
                            ('CustomerProfileAction', 'CREATE'),
                            ('ProfileProcStatus', '0'),
                            ('CustomerProfileMessage', 'Profile Request Processed'),
                            ('CustomerAddress1', data['CustomerAddress1']),
                            ('CustomerAddress2', data.get('CustomerAddress2', '')),
                            ('CustomerCity', data['CustomerCity']),
                            ('CustomerState', data['CustomerState']),
                            ('CustomerZIP', data['CustomerZIP']),
                            ('CustomerEmail', data.get('CustomerEmail', '')),
                            ('CustomerPhone', data['CustomerPhone']),
                            ('CustomerCountryCode', data['CustomerCountryCode']),
                            ('CustomerProfileOrderOverrideInd', data['CustomerProfileOrderOverrideInd']),
                            ('OrderDefaultDescription', data.get('OrderDefaultDescription', '')),
                            ('OrderDefaultAmount', data.get('OrderDefaultAmount', '')),
                            ('CustomerAccountType', data['CustomerAccountType']),
                            ('Status', data.get('Status', 'A')),
                            ('CardBrand', data.get('CardBrand', '')),
                            ('CCAccountNum', data['CCAccountNum']),
                            ('CCExpireDate', data['CCExpireDate']),
                            ('ECPAccountDDA',''),
                            ('ECPAccountType',''),
                            ('ECPAccountRT',''),
                            ('ECPBankPmtDlv',''),
                            ('SwitchSoloStartDate',''),
                            ('SwitchSoloIssueNum',''),
                            ('BillerReferenceNumber',''),
                            ('RespTime',''),])
        return {'ProfileResp': response}

