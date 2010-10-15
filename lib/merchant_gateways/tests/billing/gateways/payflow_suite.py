
from lxml.builder import ElementMaker
XML = ElementMaker()

#  CONSIDER  orbital

class MerchantGatewaysPayflowSuite:

    def successful_authorization_response(self):
        return '''<XMLPayResponse xmlns="http://www.paypal.com/XMLPay">
                  <ResponseData>
                    <Vendor>LOGIN</Vendor>
                    <Partner>paypal</Partner>
                    <TransactionResults>
                        <TransactionResult>
                            <Result>0</Result>
                            <Message>Approved</Message>
                            <Partner>verisign</Partner>
                            <HostCode>000</HostCode>
                            <ResponseText>AP</ResponseText>
                            <PNRef>VUJN1A6E11D9</PNRef>
                            <IavsResult>N</IavsResult>
                            <ZipMatch>Match</ZipMatch>
                            <AuthCode>094016</AuthCode>
                            <Vendor>ActiveMerchant</Vendor>
                            <AvsResult>Y</AvsResult>
                            <StreetMatch>Match</StreetMatch>
                            <CvResult>Match</CvResult>
                        </TransactionResult>
                    </TransactionResults>
                </ResponseData>
                </XMLPayResponse>'''

    def failed_authorization_response(self):
        return '''<XMLPayResponse xmlns="http://www.paypal.com/XMLPay">
                  <ResponseData>
                    <Vendor>LOGIN</Vendor>
                    <Partner>paypal</Partner>
                    <TransactionResults>
                        <TransactionResult>
                            <Result>12</Result>
                            <Message>Declined</Message>
                            <Partner>verisign</Partner>
                            <HostCode>000</HostCode>
                            <ResponseText>AP</ResponseText>
                            <PNRef>VUJN1A6E11D9</PNRef>
                            <IavsResult>N</IavsResult>
                            <ZipMatch>Match</ZipMatch>
                            <AuthCode>094016</AuthCode>
                            <Vendor>ActiveMerchant</Vendor>
                            <AvsResult>Y</AvsResult>
                            <StreetMatch>Match</StreetMatch>
                            <CvResult>Match</CvResult>
                        </TransactionResult>
                    </TransactionResults>
                </ResponseData>
                </XMLPayResponse>'''

    def successful_void_response(self):
        return '''<XMLPayResponse xmlns="http://www.paypal.com/XMLPay">
                  <ResponseData>
                    <Vendor>LOGIN</Vendor>
                    <Partner>paypal</Partner>
                    <TransactionResults>
                        <TransactionResult>
                            <Result>0</Result>
                            <Message>Approved</Message>
                            <Partner>verisign</Partner>
                            <HostCode>000</HostCode>
                            <ResponseText>AP</ResponseText>
                            <PNRef>VUJN1A6E11D9</PNRef>
                            <IavsResult>N</IavsResult>
                            <ZipMatch>Match</ZipMatch>
                            <AuthCode>094016</AuthCode>
                            <Vendor>ActiveMerchant</Vendor>
                            <AvsResult>Y</AvsResult>
                            <StreetMatch>Match</StreetMatch>
                            <CvResult>Match</CvResult>
                        </TransactionResult>
                    </TransactionResults>
                </ResponseData>
                </XMLPayResponse>'''

    def successful_credit_response(self):
        return '''<XMLPayResponse xmlns="http://www.paypal.com/XMLPay">
                  <ResponseData>
                    <Vendor>LOGIN</Vendor>
                    <Partner>paypal</Partner>
                    <TransactionResults>
                        <TransactionResult>
                            <Result>0</Result>
                            <Message>Approved</Message>
                            <Partner>verisign</Partner>
                            <HostCode>000</HostCode>
                            <ResponseText>AP</ResponseText>
                            <PNRef>VUJN1A6E11D9</PNRef>
                            <IavsResult>N</IavsResult>
                            <ZipMatch>Match</ZipMatch>
                            <AuthCode>094016</AuthCode>
                            <Vendor>ActiveMerchant</Vendor>
                            <AvsResult>Y</AvsResult>
                            <StreetMatch>Match</StreetMatch>
                            <CvResult>Match</CvResult>
                        </TransactionResult>
                    </TransactionResults>
                </ResponseData>
                </XMLPayResponse>'''

    def assert_webservice_called(self, mock, vendor, amount, currency, card_type, cc_number, exp_date, cv_num,
                                       first_name, last_name, username, password):
        #args = self.gateway.post_webservice.call_args[0]
        args = mock.call_args[0]
        assert 2 == len(self.gateway.post_webservice.call_args), 'should be 1 but either we call twice or the Mock has an issue'

        if self.gateway.is_test:  #  TODO  ternary
            self.assert_equal('https://pilot-payflowpro.paypal.com', args[0])
        else:
            self.assert_equal('https://payflowpro.paypal.com', args[0])

        xml = args[1]
        xmlns = 'xmlns="http://www.paypal.com/XMLPay"' # TODO  pass to .xpath() instead of erasing!
        assert xmlns in xml
        xml = xml.replace(xmlns, '')

        self.assert_xml(xml, lambda x:
                x.XMLPayRequest(
                        x.RequestData(
                            x.Vendor('LOGIN'),
                            x.Partner('PayPal'),
                            x.Transactions(
                                x.Transaction(
                                    x.Verbosity('MEDIUM'),
                                    x.Authorization()
                                )
                            )
                        ),
                        x.PayData(
                            x.Invoice(
                                x.TotalAmt(amount, Currency=currency)  #  TODO  merge these into money
                            ),
                        x.Tender(
                            x.Card(
                                x.CardType(card_type),
                                x.CardNum(cc_number),
                                x.ExpDate('209012'),
                                x.NameOnCard(first_name),
                                x.CVNum(cv_num),
                                x.ExtData(Name="LASTNAME", Value=last_name)
                            )
                        )
                    ),
                    x.RequestAuth(
                        x.UserPass(
                            x.User('LOGIN'), # TODO  use username here
                            x.Password(password)
                        )
                    )
                )
            )

from merchant_gateways.billing.common import xmltodict, dicttoxml, ET

class PayflowProMockServer(object):
    def __init__(self, failure=None):
        self.failure = failure

    def __call__(self, url, msg, headers):
        msg = msg.replace('xmlns="http://www.paypal.com/XMLPay"', '') #arghhh, don't care to deal with namespaces
        data = xmltodict(ET.fromstring(msg))
        response = self.receive(data)
        return ET.tostring(self.send(data, response))

    def receive(self, data):
        if self.failure:
            return self.failure
        assert data['RequestAuth']['UserPass']['User']
        assert data['RequestAuth']['UserPass']['Password']
        transaction_data = data['RequestData']['Transactions']['Transaction']
        for key in ['Sale', 'Authorization', 'Capture', 'Void', 'Credit']:
            if key in transaction_data:
                return getattr(self, key.lower())(transaction_data[key])
        assert False, 'Unrecognized action'

    def send(self, data, response):
        root = ET.Element('XMLPayResponse', {'xmlns':'http://www.paypal.com/XMLPay'})
        msg = {'ResponseData': {'Vendor':data['RequestData']['Vendor'],
                                'Partner':data['RequestData']['Partner'],
                                'TransactionResults': {'TransactionResult': response }}}
        dicttoxml(msg, root)
        return root
    
    def failure_message(self, data):
        return {'Result':12,
                'Message':'Declined',
                'Partner':'verisign',
                'HostCode':'000',
                'ResponseText':'AP',
                'PNRef':'VUJN1A6E11D9',}
    
    def success_message(self, data):
        return {'Result':0,
                'Message':'Approved',
                'Partner':'verisign',
                'HostCode':'000',
                'ResponseText':'AP',
                'PNRef':'VUJN1A6E11D9',
                'Vendor':'ActiveMerchant',}

    def avs_success_message(self, data):
        return {'IavsResult':'N',
                'ZipMatch':'Match',
                'AvsResult':'Y',
                'StreetMatch':'Match',
                'CvResult':'Match',}

    def assert_amount(self, data):
        assert 'TotalAmt' in data['Invoice']
        assert data['Invoice']['TotalAmt'].text
        assert 'Currency' in data['Invoice']['TotalAmt'].attrib
    
    def assert_payment_info(self, data):
        tender = data['PayData']['Tender']['Card']
        if 'CardNum' in tender:
            assert 'CardType' in tender
            assert 'CardNum' in tender
            assert 'ExpDate' in tender
        else:
            assert tender['ExtData'].attrib['Name'] == 'ORIGID'
            assert 'Value' in tender['ExtData'].attrib

    def capture(self, data):
        assert 'PNRef' in data
        self.assert_amount(data)
        return self.success_message(data)

    def credit(self, data):
        assert 'PNRef' in data
        self.assert_amount(data)
        return self.success_message(data)
    
    def void(self, data):
        assert 'PNRef' in data
        return self.success_message(data)

    def authorization(self, data):
        self.assert_payment_info(data)
        self.assert_amount(data['PayData'])
        response = self.success_message(data)
        response.update(self.avs_success_message(data))
        return response
    
    sale = authorization

