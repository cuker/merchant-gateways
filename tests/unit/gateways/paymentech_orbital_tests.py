
from merchant_gateways.billing.gateways.paymentech_orbital import PaymentechOrbital
from merchant_gateways.billing.gateways.gateway import xStr
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from pprint import pprint
from lxml.builder import ElementMaker
XML = ElementMaker()

class PaymentechOrbitalTests(MerchantGatewaysTestSuite,
                             MerchantGatewaysTestSuite.CommonTests):

    def gateway_type(self):
        return PaymentechOrbital

    def mock_webservice(self, response):

        self.options['billing_address'] = {}  #  TODO  put something in there, throw an error if it ain't there
        self.mock_post_webservice(response)

    def assert_successful_authorization(self):
        #  TODO  de-cybersource all this
        order_id = str(self.options['order_id'])  #  TODO  put something in options
#        requestID = '1842651133440156177166'
#        requestToken = 'AP4JY+Or4xRonEAOERAyMzQzOTEzMEM0MFZaNUZCBgDH3fgJ8AEGAMfd+AnwAwzRpAAA7RT/'
#        authorization = ';'.join([order_id, requestID, requestToken])
        self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.authorization) # TODO  why not from <c:authorizationCode>004542</c:authorizationCode> ?
        self.assert_equal('Approved', self.gateway.message)
        assert self.response.success

    def assert_failed_authorization(self):
        self.assert_none(self.response.params['TxRefNum'])
         #  TODO  assert the message
        self.assert_none(self.response.fraud_review)

        reference = { 'AVSRespCode': None,
                      'AccountNum': None,
                      'ApprovalStatus': None,
                      'AuthCode': None,
                      'CAVVRespCode': None,  #  CONSIDER  diff between CAVV and CVV2??
                      'CVV2RespCode': None,  #  TODO  cvv and avs systems?
                      'CardBrand': None,
                      'CustomerName': None,
                      'CustomerProfileMessage': 'Profile: Unable to Perform Profile Transaction. The Associated Transaction Failed. ',
                      'CustomerRefNum': None,
                      'HostAVSRespCode': None,
                      'HostCVV2RespCode': None,
                      'HostRespCode': None,
                      'IndustryType': None,
                      'MerchantID': None,
                      'MessageType': None,
                      'OrderID': None,
                      'ProcStatus': '841',
                      'ProfileProcStatus': '9576',
                      'RecurringAdviceCd': None,
                      'RespCode': None,
                      'RespMsg': None,
                      'RespTime': None,
                      'StatusMsg': 'Error validating card/account number range',
                      'TerminalID': None,
                      'TxRefIdx': None,
                      'TxRefNum': None }

        self.assert_match_hash(self.response.params, reference)
        self.assert_equal('Error validating card/account number range', self.response.message)

    def assert_successful_purchase(self):
        self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.params['TxRefNum'])

        '''TODO self.assert_equal( 'Successful transaction', self.response.message )'''

    def test_build_request(self):
        #  TODO  de-cybersource me
        reference = '''<?xml version="1.0" encoding="UTF-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
              <s:Header>
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" s:mustUnderstand="1">
                  <wsse:UsernameToken>
                    <wsse:Username>l</wsse:Username>
                    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">p</wsse:Password>
                  </wsse:UsernameToken>
                </wsse:Security>
              </s:Header>
              <s:Body xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <requestMessage xmlns="urn:schemas-cybersource-com:transaction-data-1.32">
                  <merchantID>l</merchantID>
                  <merchantReferenceCode>1000</merchantReferenceCode>
                  <clientLibrary>Ruby Active Merchant</clientLibrary>
                  <clientLibraryVersion>1.0</clientLibraryVersion>
                  <clientEnvironment>Linux</clientEnvironment>
                    Aparecium
                </requestMessage>
              </s:Body>
            </s:Envelope>
            '''

        sample = self.gateway.build_request('Aparecium')  #  TODO  as usual, options!
        self.assert_match_xml(reference, sample)

    def parsed_authentication_response(self):
        return dict(
            AccountNum='5454545454545454',
            ApprovalStatus='1',
            AuthCode='tst554',
            AVSRespCode='B ',
            CardBrand='MC',
            CAVVRespCode=None,
            CustomerName='JOE SMITH',
            CustomerProfileMessage='Profile Created',  #  TODO  use this?
            CustomerRefNum='2145108',
            CVV2RespCode='M',
            HostAVSRespCode='I3',
            HostCVV2RespCode='M',
            HostRespCode='100',
            IndustryType=None,
            MerchantID='000000',
            MessageType='AC',
            OrderID='1',
            ProcStatus='0',
            ProfileProcStatus='0',
            RecurringAdviceCd=None,
            RespCode='00',
            RespMsg=None,
            RespTime='121825',
            StatusMsg='Approved',
            TerminalID='000',
            TxRefIdx='1',
            TxRefNum='4A785F5106CCDC41A936BFF628BF73036FEC5401',
        )

    def test_parse(self):
        soap = self.successful_authorization_response()
        sample = self.gateway.parse(soap)
        reference = self.parsed_authentication_response()
        self.assert_match_hash(reference, sample)

    def test_parse_purchase_response(self):
        soap = self.successful_purchase_response()
        sample = self.gateway.parse(soap)
        return # TODO
        self.assert_equal(sample['cvCode'], 'M')
        self.assert_equal(sample['cvCodeRaw'], 'M')  #  TODO  what to do with the raw code?

    def test_setup_address_hash(self):  #  TODO  everyone should fixup like these (Payflow does it a different way)
        g = self.gateway
        self.assert_equal({}, g.setup_address_hash()['billing_address'])
        addy = dict(yo=42)
        self.assert_equal(addy, g.setup_address_hash(billing_address=addy)['billing_address'])
        self.assert_equal(addy, g.setup_address_hash(address=addy)['billing_address'])
        self.assert_equal({}, g.setup_address_hash()['shipping_address'])
        self.assert_equal(addy, g.setup_address_hash(shipping_address=addy)['shipping_address'])

    #  TODO  always credit_card never creditcard

    def test_build_auth_request(self):
        self.money = Decimal('100.00')

        self.options = {
            'order_id': '1',
            'description': 'Time-Turner',
            'email': 'hgranger@hogwarts.edu',
            'customer': '947',    #  TODO  test this going through
            'ip': '192.168.1.1',  #  TODO  test this going through
        }

        billing_address = {
            'address1': '444 Main St.',
            'address2': 'Apt 2',
            'company': 'ACME Software',  #  TODO  where's the love for the company?
            'phone': '222-222-2222',      #  TODO  where the phone number goes?
            'zip': '77777',
            'city': 'Dallas',
            'country': 'USA',
            'state': 'TX'
        }

        self.options['billing_address'] = billing_address
        self.options['login'] = 'Triwizard'  #  TODO  is the one true standard interface "login" or "username"
        self.options['password'] = 'Tournament'

        message = self.gateway.build_auth_request(self.money, self.credit_card, **self.options)

#        {'start_month': None, 'verification_value': None, 'start_year': None, 'card_type': 'v', 'issue_number': None, }

        # TODO enforce <?xml version="1.0" encoding="UTF-8"?> tags??
        #  ERGO  configure the sample correctly at error time

        assert   12 == self.credit_card.month
        assert 2090 == self.credit_card.year

        self.assert_xml(message, lambda x:
                             x.Request(
                                 x.NewOrder(
                        x.OrbitalConnectionUsername('Triwizard'),
                        x.OrbitalConnectionPassword('Tournament'),
                        x.IndustryType('EC'),
                        x.MessageType('A'),
                        x.BIN('1'),
                        x.MerchantID('1'),   #  TODO  configure all these so we don't need to think about them
                        x.TerminalID('1'),
                        x.CardBrand(''),
                        x.AccountNum('4242424242424242'),
                        x.Exp('1290'),
                        x.CurrencyCode('840'),
                        x.CurrencyExponent('2'),
                        x.CardSecValInd('1'),
                        x.CardSecVal(self.credit_card.verification_value),
                        x.AVSzip(billing_address['zip']),
                        x.AVSaddress1(billing_address['address1']),
                        x.AVSaddress2(billing_address['address2']),
                        x.AVScity(billing_address['city']),
                        x.AVSstate(billing_address['state']),
                        x.AVSphoneNum(billing_address['phone']),
                        x.AVSname(self.credit_card.first_name + ' ' + self.credit_card.last_name), #  TODO is this really the first & last names??
                        x.AVScountryCode('840'),
                        x.CustomerProfileFromOrderInd('A'),
                        x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID(''),
                        x.Amount('100.00')
                                 )
                             )
                   )

        # TODO default_dict should expose all members as read-only data values

    def test_build_auth_request_without_street2(self):
        self.money = Decimal('2.00')

        self.options = {
            'order_id': '1',
            'description': 'Time-Turner',  # TODO  take as much of this out as possible
            'email': 'hgranger@hogwarts.edu',
            'customer': '947',
            'ip': '192.168.1.1',
        }

        billing_address = {
            'address1': '444 Main St.',
            'company': 'ACME Software',  #  TODO  where's the love for the company?
            'phone': '222-222-2222',      #  TODO  where the phone number goes?
            'zip': '77777',
            'city': 'Dallas',
            'country': 'USA',
            'state': 'TX'
        }

        self.options['billing_address'] = billing_address

        message = self.gateway.build_auth_request(self.money, self.credit_card, **self.options)

        #  TODO  default not to USD

        # self.assert_('<street2></street2>' in message)  #  TODO  assert_contains

    def successful_purchase_response(self):  #  TODO  get a real one!
        return self.successful_authorization_response()

    def successful_authorization_response(self):
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


# ERGO  put us into the test report system and see what we look like!
