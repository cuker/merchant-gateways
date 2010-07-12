# -*- coding: utf-8 -*-

from merchant_gateways.billing.gateways.paymentech_orbital import PaymentechOrbital
from merchant_gateways.billing.gateways.gateway import xStr
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from merchant_gateways.tests.billing.gateways.paymentech_orbital_suite import MerchantGatewaysPaymentechOrbitalSuite
from pprint import pprint
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money
import os

# ERGO  put us into the test report system and see what we look like!

class PaymentechOrbitalTests(MerchantGatewaysTestSuite,
                             MerchantGatewaysPaymentechOrbitalSuite,
                             MerchantGatewaysTestSuite.CommonTests):

    def gateway_type(self):
        return PaymentechOrbital

    def test_generate_headers(self):
        headers = self.gateway._generate_headers('yo', merchant_id='nobbly')  # CONSIDER  harry potter trivia!
        assert len('yo') == headers['Content-length']
        assert 'nobbly' == headers['Merchant-id']

    def _test_REMOTE_authorization(self):
        #  CONSIDER log errors like: 'message': 'Security Information is Missing',

        # TODO  they will NOT be accepting American Express on the UK site.

        self.options['merchant_id'] = 'C-:'
        self.credit_card.number = '4111111111111111'

        self.gateway.purchase(self.money, self.credit_card, **self.options)
        self.response = self.gateway.response

        assert self.response.is_test
        self.assert_success()
        pprint(self.response.result)

        TODO_use_this_passing_auth_result = {
            'AVSRespCode': '3 ',
             'AccountNum': '4111111111111111',
             'ApprovalStatus': '1',
             'AuthCode': 'tst839',
             'CAVVRespCode': None,
             'CVV2RespCode': 'M',
             'CardBrand': 'VI',
             'CustomerName': 'HERMIONE GRANGER',
             'CustomerProfileMessage': 'Profile Created',
             'CustomerRefNum': '3813444',
             'HostAVSRespCode': '  ',
             'HostCVV2RespCode': 'M',
             'HostRespCode': '100',
             'IndustryType': None,
             'MerchantID': '041756',
             'MessageType': 'A',
             'OrderID': 'TODO',
             'ProcStatus': '0',
             'ProfileProcStatus': '0',
             'RecurringAdviceCd': None,
             'RespCode': '00',
             'RespMsg': None,
             'RespTime': '183559',
             'StatusMsg': 'Approved',
             'TerminalID': '001',
             'TxRefIdx': '0',
             'TxRefNum': '4BFEF3CF93E69568318ADC83DB054BD059AB54EE'}

        TODO_use_this_passing_purchase_result = {
            'AVSRespCode': '3 ',
             'AccountNum': '4111111111111111',
             'ApprovalStatus': '1',
             'AuthCode': 'tst839',
             'CAVVRespCode': None,
             'CVV2RespCode': 'M',
             'CardBrand': 'VI',
             'CustomerName': 'HERMIONE GRANGER',
             'CustomerProfileMessage': 'Profile Created',
             'CustomerRefNum': '3813446',
             'HostAVSRespCode': '  ',
             'HostCVV2RespCode': 'M',
             'HostRespCode': '100',
             'IndustryType': None,
             'MerchantID': '041756',
             'MessageType': 'AC',
             'OrderID': 'TODO',
             'ProcStatus': '0',
             'ProfileProcStatus': '0',
             'RecurringAdviceCd': None,
             'RespCode': '00',
             'RespMsg': None,
             'RespTime': '183937',
             'StatusMsg': 'Approved',
             'TerminalID': '001',
             'TxRefIdx': '1',
             'TxRefNum': '4BFEF4A9AF7862245FB58E77624909089D6954C2'}

        #self.assert_successful_authorization()

    def assert_successful_authorization(self):
        order_id = str(self.options['order_id'])  #  TODO  put something in options
        self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.authorization)
        self.assert_equal('Approved', self.gateway.message)

        # CONSIDER stash it there self.gateway.response
        #print self.response.result   #  TODO  and make it the RAW result!!

        # CONSIDER what be 'RespCode': '00'?
        # CONSIDER stash HostCVV2RespCode in CvvResult; use 'CAVVRespCode': None
        # CONSIDER what be 'TerminalID': '000',

        # CONSIDER use 'RespMsg': None,
        # CONSIDER what be 'CardBrand': 'MC', 'MerchantID': '000000', 'ProfileProcStatus': '0','RecurringAdviceCd': None  'CustomerRefNum

        #  CONSIDER stash the  'HostAVSRespCode': 'I3',
        # CONSIDER  use the 'AuthCode': 'tst554', 'RespTime': '121825', 'ProcStatus': '0', , 'HostRespCode': '100'}

        self.assert_equal('B ', self.response.result['AVSRespCode'])  #  CONSIDER why 'B '?
        avs = self.response.avs_result
        self.assert_equal( 'B', avs.code )
        self.assert_equal( 'Y', avs.street_match )  #  CONSIDER  why none? What wrong with B?
        self.assert_equal( None, avs.postal_match )
        self.assert_equal('M', self.response.result['CVV2RespCode'])
        cvv = self.response.cvv_result
        cvv = self.response.cvv_result
        self.assert_equal( 'M', cvv.code )
        self.assert_equal( 'Match', cvv.message )  #  CONSIDER huh??
        assert self.response.success

    def assert_failed_authorization(self):
        self.assert_none(self.response.result['TxRefNum'])
        self.assert_none(self.response.fraud_review)

        reference = { 'AVSRespCode': None,
                      'AccountNum': None,
                      'ApprovalStatus': None,
                      'AuthCode': None,
                      'CAVVRespCode': None,
                      'CVV2RespCode': None,
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

        self.assert_match_hash(self.response.result, reference)
        self.assert_equal('Error validating card/account number range', self.response.message)

    def assert_successful_purchase(self):
        self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.result['TxRefNum'])

        reference = { 'AVSRespCode': 'B ',
                      'AccountNum': '5454545454545454',
                      'ApprovalStatus': '1',
                      'AuthCode': 'tst554',
                      'CAVVRespCode': None,
                      'CVV2RespCode': 'M',
                      'CardBrand': 'MC',
                      'CustomerName': 'JOE SMITH',
                      'CustomerProfileMessage': 'Profile Created',
                      'CustomerRefNum': '2145108',
                      'HostAVSRespCode': 'I3',
                      'HostCVV2RespCode': 'M',
                      'HostRespCode': '100',
                      'IndustryType': None,
                      'MerchantID': '000000',
                      'MessageType': 'AC',
                      'OrderID': '1',
                      'ProcStatus': '0',
                      'ProfileProcStatus': '0',
                      'RecurringAdviceCd': None,
                      'RespCode': '00',
                      'RespMsg': None,
                      'RespTime': '121825',
                      'StatusMsg': 'Approved',
                      'TerminalID': '000',
                      'TxRefIdx': '1',
                      'TxRefNum': '4A785F5106CCDC41A936BFF628BF73036FEC5401'}

        self.assert_match_hash(reference, self.response.result)

        '''TODO self.assert_equal( 'Successful transaction', self.response.message )'''

    def parsed_authentication_response(self):
        return dict(
            AccountNum='5454545454545454',
            ApprovalStatus='1',
            AuthCode='tst554',
            AVSRespCode='B ',
            CardBrand='MC',
            CAVVRespCode=None,
            CustomerName='JOE SMITH',
            CustomerProfileMessage='Profile Created',  #  CONSIDER  use this?
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
        reference = {'AVSRespCode': 'B ', 'RespCode': '00', 'HostCVV2RespCode': 'M', 'TerminalID': '000', 'CVV2RespCode': 'M', 'RespMsg': None, 'CardBrand': 'MC', 'MerchantID': '000000', 'AccountNum': '5454545454545454', 'ProfileProcStatus': '0', 'CustomerName': 'JOE SMITH', 'MessageType': 'AC', 'HostAVSRespCode': 'I3', 'RecurringAdviceCd': None, 'IndustryType': None, 'OrderID': '1', 'StatusMsg': 'Approved', 'ApprovalStatus': '1', 'TxRefIdx': '1', 'TxRefNum': '4A785F5106CCDC41A936BFF628BF73036FEC5401', 'CustomerRefNum': '2145108', 'CustomerProfileMessage': 'Profile Created', 'AuthCode': 'tst554', 'RespTime': '121825', 'ProcStatus': '0', 'CAVVRespCode': None, 'HostRespCode': '100'}
        self.assert_match_dict(reference, sample)

    def test_setup_address_hash(self):  #  TODO  everyone should fixup like these (Payflow does it a different way)
        g = self.gateway
        self.assert_equal({}, g.setup_address_hash()['billing_address'])
        addy = dict(yo=42)
        billing_address = g.setup_address_hash(billing_address=addy)['billing_address']
        self.assert_equal(addy, billing_address)
        self.assert_equal(addy, g.setup_address_hash(address=addy)['billing_address'])
        self.assert_equal({}, g.setup_address_hash()['shipping_address'])
        self.assert_equal(addy, g.setup_address_hash(shipping_address=addy)['shipping_address'])

    def test_build_authorization_request(self):
        self.money = Money('100.00', 'USD')
        billing_address = self.assemble_billing_address()
        self.options['merchant_id'] = 'Triwizard_Tournament'  #  CONSIDER  accomodate users who prefer name/password

        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)

#        {'start_month': None, 'verification_value': None, 'start_year': None, 'card_type': 'v', 'issue_number': None, }

        #  ERGO  configure the sample correctly at error time

        assert   12 == self.credit_card.month
        assert 2090 == self.credit_card.year

        self.assert_xml(message, lambda x:
                 x.Request(
                     x.NewOrder(
                        x.IndustryType('EC'),
                        x.MessageType('A'),
                        x.BIN('1'),
                        x.MerchantID('Triwizard_Tournament'),
                        x.TerminalID('001'),
                        # CONSIDER  need this? x.CardBrand(''),
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
                        x.AVScountryCode('US'), # TODO get me from the billing address
                        #x.CustomerProfileFromOrderInd('A'),
                        #x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID('1'),
                        x.Amount('10000')
                           )
                       )
                   )

    def test_build_purchase_request(self):
        self.money = Money('101.00', 'USD')
        billing_address = self.assemble_billing_address()
        self.options['order_id'] = 42
        self.options['merchant_id'] = 'Triwizard_Tournament'  #  CONSIDER  accomodate users who prefer name/password

        message = self.gateway.build_purchase_request(self.money, self.credit_card, **self.options)

#        {'start_month': None, 'verification_value': None, 'start_year': None, 'card_type': 'v', 'issue_number': None, }

        # TODO enforce <?xml version="1.0" encoding="UTF-8"?> tags??
        #  ERGO  configure the sample correctly at error time

        assert   12 == self.credit_card.month
        assert 2090 == self.credit_card.year

        self.assert_xml(message, lambda x:
                             x.Request(
                                 x.NewOrder(
                        x.IndustryType('EC'),
                        x.MessageType('AC'),
                        x.BIN('1'),
                        x.MerchantID('Triwizard_Tournament'),
                        x.TerminalID('001'),
                        # CONSIDER  need this? x.CardBrand(''),
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
                        x.AVScountryCode('US'),
                        #x.CustomerProfileFromOrderInd('A'),
                        #x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID('42'),
                        x.Amount('10100')
                           )
                       )
                   )

    def test_build_purchase_request_with_null_order_id(self):
        self.options['order_id'] = None
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)
        self.assert_xml(message, lambda x: x.OrderID(''))
        self.assert_gateway_message_schema(message, 'Request_PTI49.xsd')

    def test_build_purchase_request_with_no_order_id(self):
        self.money = Money('101.00', 'USD')
        del self.options['order_id']
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)
        self.assert_xml(message, lambda x: x.OrderID(''))
        self.assert_gateway_message_schema(message, 'Request_PTI49.xsd')

    def test_build_purchase_request_with_blank_order_id(self):
        self.money = Money('101.00', 'USD')
        billing_address = self.assemble_billing_address()
        self.options['order_id'] = ' '
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)
        self.assert_xml(message, lambda x: x.OrderID(' '))
        self.assert_gateway_message_schema(message, 'Request_PTI49.xsd')

    def test_set_country_code(self):
        self.options['billing_address']['country'] = 'CN'  #  China! (right?;)
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)
        self.assert_xml(message, lambda x: x.AVScountryCode('CN'))

    def test_raise_an_exception_if_country_code_is_too_long(self):
        self.options['billing_address']['country'] = 'China'  # longer that 2 characters (that's all we can check!)
        yo = self.assert_raises(ValueError, self.gateway.build_authorization_request, self.money, self.credit_card, **self.options)
        self.assert_contains('Country code must be 2 characters (China)', yo)

        # TODO default_dict should expose all members as read-only data values

    def test_validate_purchase_request(self):
        Nuevo_Sol = 'PEN'
        Nuevo_Sol_numeric = '604'  #  CONSIDER  vary this, to prove we can
        self.money = Money('200.00', Nuevo_Sol)
        message = self.gateway.build_purchase_request(self.money, self.credit_card, **self.options)
        self.assert_gateway_message_schema(message, 'Request_PTI49.xsd')

    def TODO_test_build_authorization_request_with_alternative_money(self):
        Nuevo_Sol = 'PEN'
        Nuevo_Sol_numeric = '604'
        self.money = Money('200.00', Nuevo_Sol)
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)

        self.assert_xml( message, lambda x:
                             x.Request(
                               x.AC(
                                 XML.CommonData(
                                   XML.CommonMandatory(
                                     XML.Currency( CurrencyCode=Nuevo_Sol_numeric,
                                                   CurrencyExponent='2'  #  CONSIDER  vary this
                                          )
                                        )
                                      )
                                    )
                                 )
                             )

#  TODO  Transaction Amount:
# Keys:
# Implied decimal including those currencies that are a zero exponent. For example, both $100.00 (an exponent of ‘2’) and 100 Yen (an exponent of ‘0’) should be sent as <Amount>10000</Amount>.
# See table for min/max amount for each currency type.

# holy f--- do we gotta do all that?? note added later: YES!

# TODO  comprehend this: Sample XML Auth Response with MIME Header

#HTTP/1.1 200 OK Date: Fri, 14 Feb 2003 12:00:00 GMT MIME-Version: 1.0 Content-type: application/PTI26 Content-length: 646 Content-transfer-encoding: text Request-number: 1 Document-type: Response
#<Response> <RefundResponse CapStatus="1" HcsTcsInd="T" LangInd="00" MessageType="FR"
#TzCode="705" Version="2"> <TxRefIdx>1</TxRefIdx>
#<TxRefNum>EB847AD1B02AD5119F5F00508B94EDEC844FE27A</TxRefNum> <ProcStatus>0</ProcStatus> <ApprovalStatus>1</ApprovalStatus> <MerchantID>123456789012</MerchantID>
#<TerminalID>001</TerminalID> <OrderNumber>1234567890123456</OrderNumber> <AccountNum>4012888888881</AccountNum> <POSEntryMode>01</POSEntryMode> <RespDate>010410</RespDate> <RespTime>10012001120003</RespTime> <CardType1>VI</CardType1> <ExpDate1>1205</ExpDate1>
#<ResponseCodes> <RespCode/>
#</ResponseCodes> </RefundResponse>
#</Response>
