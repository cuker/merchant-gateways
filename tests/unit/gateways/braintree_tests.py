# -*- coding: utf-8 -*-

from merchant_gateways.billing.gateways.braintree import Braintree
from merchant_gateways.billing.gateways.gateway import xStr
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from pprint import pprint
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money
import os

#  TODO  trust nothing below this line

class BraintreeTests( MerchantGatewaysTestSuite,
                      MerchantGatewaysTestSuite.CommonTests ):

    def gateway_type(self):
        return Braintree

#  def successful_purchase_response
#    'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'
#  end

    def successful_authorization_response(self):
        return 'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&' + \
               'orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'
         #  TODO  get a real one - that one is just a copy of successful_purchase_response

    def assert_successful_authorization(self):
        order_id = str(self.options['order_id'])  #  TODO  put something in options


# TODO        authcode=123456&transactionid=510695343

#     TODO   self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.authorization)
#        self.assert_equal('Approved', self.gateway.message)
#
#        # CONSIDER stash it there self.gateway.response
#        #print self.response.result   #  TODO  and make it the RAW result!!
#
#        # CONSIDER what be 'RespCode': '00'?
#        # CONSIDER stash HostCVV2RespCode in CvvResult; use 'CAVVRespCode': None
#        # CONSIDER what be 'TerminalID': '000',
#
#        # CONSIDER use 'RespMsg': None,
#        # CONSIDER what be 'CardBrand': 'MC', 'MerchantID': '000000', 'ProfileProcStatus': '0','RecurringAdviceCd': None  'CustomerRefNum
#        # TODO  uh... 'CustomerName': 'JOE SMITH', 'MessageType': 'AC',
#        #  CONSIDER stash the  'HostAVSRespCode': 'I3',
#        # CONSIDER  use the 'AuthCode': 'tst554', 'RespTime': '121825', 'ProcStatus': '0', , 'HostRespCode': '100'}
#
#        self.assert_equal('B ', self.response.result['AVSRespCode'])  #  CONSIDER why 'B '?
#        avs = self.response.avs_result
#        self.assert_equal( 'B', avs.code )
#        self.assert_equal( 'Y', avs.street_match )  #  TODO  why none? What wrong with B?
#        self.assert_equal( None, avs.postal_match )
#        self.assert_equal('M', self.response.result['CVV2RespCode'])
#        cvv = self.response.cvv_result
#        cvv = self.response.cvv_result
#        self.assert_equal( 'M', cvv.code )
#        self.assert_equal( 'Match', cvv.message )  #  CONSIDER huh??
        assert self.response.success


        # type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&
        # ccexp=0911&currency=USD&amount=1.00&firstname=Longbob.address1=1234+My+Street&company=Widgets+Inc&
        # city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&
        # username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON..address1=1234+My+Street&company=Widgets+Inc&city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON'

    def test_add_billing_address(self):
        result = {}  #  TODO  use or lose this

        self.gateway.add_address(result, '', address1='164 Waverley Street', country='US', state='CO' )
        self.assert_equal(set(["address1", "address2", "city", "company", "country", "phone", "state", "zip"]), set(result.keys()))
        self.assert_equal('CO', result["state"])
        self.assert_equal('164 Waverley Street', result["address1"])
        self.assert_equal('US', result["country"])

    def test_add_billing_address(self):
        result = {}  #  TODO  make this a member

        self.gateway.add_invoice(result, order_id = 42)
        self.assert_equal('42', result["orderid"])

    def test_post_data(self):

        params = dict( lastname="Longsen", orderid="",
                       ccnumber="4242424242424242", amount="1.00", currency="USD",
                      ccexp="0911", cvv="123", firstname="Longbob" )

        self.gateway.options.update(login="LOGIN", password="PASSWORD", amount=Money('1.00'))
        action = 'sale'

        query = self.gateway.post_data(action, **params)

        self.assert_params(query, amount="1.00",  #  TODO  currency?
                                  ccexp="0911",
                                  ccnumber="4242424242424242",
                                  currency="USD",
                                  cvv="123",
                                  firstname="Longbob",
                                  lastname="Longsen",
                                  # orderid='',  #  TODO  order_id everywhere!! (and get assert_params to handle this correctly!!)
                                  password="PASSWORD",
                                  type=action,
                                  username="LOGIN"
                                  )

    #type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob

    def test_add_creditcard(self):
#        if options[:store] TODO here's your cim (?)
#          post[:customer_vault] = "add_customer"
#          post[:customer_vault_id] = options[:store] unless options[:store] == true
#        end
        post = {}
        self.gateway.add_credit_card(post, self.credit_card)

        self.assert_dict_contains( post,
                                   ccnumber=self.credit_card.number )
#        post[:cvv] = creditcard.verification_value if creditcard.verification_value?
                                   # ccexp=self.credit_card.ccexp )
#        post[:firstname] = creditcard.first_name
#        post[:lastname]  = creditcard.last_name

    def test_expdate(self):
        self.credit_card.month = 9
        self.credit_card.year = 2090
        self.assert_equal('0990', self.gateway.expdate(self. credit_card))
        self.credit_card.month = 9
        self.credit_card.year = 90
        self.assert_equal('0990', self.gateway.expdate(self. credit_card))

    def test_add_customer_data(self):
        post = {}
        self.gateway.add_customer_data(post, email='Lord.Hanuman@ArbudaDevi.org')
        self.assert_equal(dict(email='Lord.Hanuman@ArbudaDevi.org'), post, 'must not contain ipaddress')
        post = {}
        self.gateway.add_customer_data(post, ip='72.55.146.179')
        self.assert_equal(dict(ipaddress='72.55.146.179'), post, 'must not contain email')
        post = {}
        self.gateway.add_customer_data(post, email='Lord.Hanuman@ArbudaDevi.org', ip='72.55.146.179')
        self.assert_equal(dict(email='Lord.Hanuman@ArbudaDevi.org', ipaddress='72.55.146.179'), post)

    def test_add_currency(self):
        post = {}
        self.gateway.add_currency(post, Money('2.00', 'GTQ'))  # Guatemalan Quetzals!
        self.assert_equal(dict(currency='GTQ'), post) #  TODO  assert match dict?

    def test_parse(self):
        message = "response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100"
        reference = {"avsresponse": "N", "authcode": "123456", "response": "1", "orderid": "ea1e0d50dcc8cfc6e4b55650c592097e", "responsetext": "SUCCESS", "response_code": "100", "transactionid": "510695343", "type": "sale", "cvvresponse": "N"}
        sample = self.gateway.parse(message)
        self.assert_match_dict(reference, sample)

#"response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100"
#"results"
#{"avsresponse"=>"N", "authcode"=>"123456", "response"=>"1", "orderid"=>"ea1e0d50dcc8cfc6e4b55650c592097e", "responsetext"=>"SUCCESS", "response_code"=>"100", "transactionid"=>"510695343", "type"=>"sale", "cvvresponse"=>"N"}
#."body"
#"response=2&responsetext=DECLINE&authcode=&transactionid=510695919&avsresponse=N&cvvresponse=N&orderid=50357660b0b3ef16f72a3d3b83c46983&type=sale&response_code=200"
#"results"
#{"avsresponse"=>"N", "authcode"=>nil, "response"=>"2", "orderid"=>"50357660b0b3ef16f72a3d3b83c46983", "responsetext"=>"DECLINE", "response_code"=>"200", "transactionid"=>"510695919", "type"=>"sale", "cvvresponse"=>"N"}
#.."body"
#"response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100"
#"results"
#{"avsresponse"=>"N", "authcode"=>"123456", "response"=>"1", "orderid"=>"ea1e0d50dcc8cfc6e4b55650c592097e", "responsetext"=>"SUCCESS", "response_code"=>"100", "transactionid"=>"510695343", "type"=>"sale", "cvvresponse"=>"N"}


#  TODO  trust nothing below this comment

#    def test_successful_authorization(self):
 #       pass # run away!

    def test_failed_authorization(self):
        pass # run away!

    def test_successful_purchase(self):
        pass # run away!

    def test_assert_params(self):
        params = 'type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob'
        # type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob.address1=1234+My+Street&company=Widgets+Inc&city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON..address1=1234+My+Street&company=Widgets+Inc&city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON'
        qsparams = self.assert_params(params,
                                         password='PASSWORD',
                                         #orderid=False,  #  ERGO  uh, is this helpful??
                                         ccnumber='4242424242424242')
   #     print qsparams
        action = 'AUTH_ONLY'

    def test_post_data_TODO_deprecate(self):
        #  TODO  how similar is this to AuthorizeNet? merge with?
        #  TODO  why was the rumor that Braintree used an iframe? is this the alternate?
        params = 'type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob'
        # type=sale&lastname=Longsen&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob.address1=1234+My+Street&company=Widgets+Inc&city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON..address1=1234+My+Street&company=Widgets+Inc&city=Ottawa&type=auth&lastname=Longsen&address2=Apt+1&zip=K1C2N6&country=CA&password=PASSWORD&username=LOGIN&orderid=&ccnumber=4242424242424242&phone=%28555%29555-5555&cvv=123&ccexp=0911&currency=USD&amount=1.00&firstname=Longbob&state=ON'
  #      print self.assert_params(params)
        action = 'AUTH_ONLY'
        return
        parameters = {'first_name': 'Hermione', 'card_num': '4242424242424242', 'description': 'Chamber of Secrets', 'card_code': None, 'invoice_num': 1, 'test_request': 'TRUE', 'amount': '1.00', 'last_name': 'Granger', 'exp_date': '1290'}
        reference = '?x_login=X&x_invoice_num=1&x_last_name=Granger&x_card_code=None&x_card_num=4242424242424242&x_amount=1.00&x_delim_char=%2C&x_tran_key=Y&x_encap_char=%24&x_version=3.1&x_first_name=Hermione&x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&x_type=AUTH_ONLY&x_description=Chamber+of+Secrets&x_test_request=TRUE'
        self.assert_equal(reference, self.gateway.post_data(action, parameters))
        action = 'AUTH_CAPTURE'
        parameters = {'first_name': 'Hermione', 'card_num': '4242424242424242', 'description': '', 'card_code': None, 'invoice_num': 1, 'test_request': 'TRUE', 'amount': '1.00', 'last_name': 'Granger', 'exp_date': '1290', 'login': 'X', 'trans_id': 'Y'}
        reference = '?x_login=X&x_invoice_num=1&x_trans_id=Y&x_last_name=Granger&x_card_code=None&x_card_num=4242424242424242&x_amount=1.00&x_delim_char=%2C&x_tran_key=Y&x_encap_char=%24&x_version=3.1&x_first_name=Hermione&x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&x_type=AUTH_CAPTURE&x_description=&x_test_request=TRUE'
        self.assert_equal(reference, self.gateway.post_data(action, parameters))

    def mock_webservice(self, response):
        self.options['billing_address'] = {}
        self.mock_post_webservice(response)

    def assert_failed_authorization(self):
        self.assert_none(self.response.params['TxRefNum'])
        self.assertFalse(self.response.success)
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

        self.assert_match_hash(self.response.params, reference)
        self.assert_equal('Error validating card/account number range', self.response.message)

    def assert_successful_purchase(self):
        self.assert_equal('4A785F5106CCDC41A936BFF628BF73036FEC5401', self.response.params['TxRefNum'])

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

        self.assert_match_hash(reference, self.response.params)

        '''TODO self.assert_equal( 'Successful transaction', self.response.message )'''

    def test_build_request(self):
        #  TODO  de-cybersource me

# TODO worry about: POST /AUTHORIZE HTTP/1.0 MIME-Version: 1.0 Content-type: application/PTI26 Content-length: 876 Content-transfer-encoding: text Request-number: 1 Document-type: Request Interface-Version: Test 1.4

        reference_too = '''<?xml version="1.0" encoding="UTF-8"?> <Request> <AC> <CommonData> <CommonMandatory AuthOverrideInd="N" LangInd="00" CardHolderAttendanceInd="01" HcsTcsInd="T" TxCatg="7" MessageType="A" Version="2" TzCode="705"> <AccountNum AccountTypeInd="91">4012888888881</AccountNum> <POSDetails POSEntryMode="01"/> <MerchantID>123456789012</MerchantID> <TerminalID TermEntCapInd="05" CATInfoInd="06" TermLocInd="01" CardPresentInd="N" POSConditionCode="59" AttendedTermDataInd="01">001</TerminalID> <BIN>000002</BIN> <OrderID>1234567890123456</OrderID> <AmountDetails> <Amount>000000005000</Amount> </AmountDetails> <TxTypeCommon TxTypeID="G"/> <Currency CurrencyCode="840" CurrencyExponent="2"/> <CardPresence> <CardNP> <Exp>1205</Exp> </CardNP> </CardPresence> <TxDateTime/> </CommonMandatory> <CommonOptional> <Comments>This is an AVS/CVV2 auth request</Comments> <ShippingRef>FEDEX WB12345678 Pri 1</ShippingRef> <CardSecVal CardSecInd="1">705</CardSecVal> <ECommerceData ECSecurityInd="07"> <ECOrderNum>1234567890123456</ECOrderNum> </ECommerceData> </CommonOptional> </CommonData> <Auth> <AuthMandatory FormatInd="H"/> <AuthOptional> <AVSextended> <AVSname>JOE SMITH</AVSname> <AVSaddress1>1234 WEST MAIN STREET</AVSaddress1> <AVSaddress2>SUITE 123</AVSaddress2> <AVScity>TAMPA</AVScity> <AVSstate>FL</AVSstate> <AVSzip>33123-1234</AVSzip> <AVScountryCode>US</AVScountryCode> </AVSextended> </AuthOptional> </Auth> <Cap> <CapMandatory> <EntryDataSrc>02</EntryDataSrc> </CapMandatory> <CapOptional/> </Cap> </AC> </Request>'''

#<?xml version="1.0" encoding="utf-8"?>
#<Request>
#  <AC>
#    <CommonData>
#      <CommonMandatory AuthOverrideInd="N" LangInd="00" CardHolderAttendanceInd="01" HcsTcsInd="T" TxCatg="7" MessageType="A"
#      Version="2" TzCode="705">
#        <AccountNum AccountTypeInd="91">4012888888881</AccountNum>
#        <POSDetails POSEntryMode="01" />
#        <MerchantID>123456789012</MerchantID>
#        <TerminalID TermEntCapInd="05" CATInfoInd="06" TermLocInd="01" CardPresentInd="N" POSConditionCode="59"
#        AttendedTermDataInd="01">001</TerminalID>
#        <BIN>000002</BIN>
#        <OrderID>1234567890123456</OrderID>
#        <AmountDetails>
#          <Amount>000000005000</Amount>
#        </AmountDetails>
#        <TxTypeCommon TxTypeID="G" />
#        <Currency CurrencyCode="840" CurrencyExponent="2" />
#        <CardPresence>
#          <CardNP>
#            <Exp>1205</Exp>
#          </CardNP>
#        </CardPresence>
#        <TxDateTime />
#      </CommonMandatory>
#      <CommonOptional>
#        <Comments>This is an AVS/CVV2 auth request</Comments>
#        <ShippingRef>FEDEX WB12345678 Pri 1</ShippingRef>
#        <CardSecVal CardSecInd="1">705</CardSecVal>
#        <ECommerceData ECSecurityInd="07">
#          <ECOrderNum>1234567890123456</ECOrderNum>
#        </ECommerceData>
#      </CommonOptional>
#    </CommonData>
#    <Auth>
#      <AuthMandatory FormatInd="H" />
#      <AuthOptional>
#        <AVSextended>
#          <AVSname>JOE SMITH</AVSname>
#          <AVSaddress1>1234 WEST MAIN STREET</AVSaddress1>
#          <AVSaddress2>SUITE 123</AVSaddress2>
#          <AVScity>TAMPA</AVScity>
#          <AVSstate>FL</AVSstate>
#          <AVSzip>33123-1234</AVSzip>
#          <AVScountryCode>US</AVScountryCode>
#        </AVSextended>
#      </AuthOptional>
#    </Auth>
#    <Cap>
#      <CapMandatory>
#        <EntryDataSrc>02</EntryDataSrc>
#      </CapMandatory>
#      <CapOptional />
#    </Cap>
#  </AC>
#</Request>

        #q = os.popen('tidy -i -xml -wrap 130', 'w')
        #q.write(reference_too)
        #return
        #print self.convert_xml_to_element_maker(reference_too)
        self.money = Money('1.00', 'USD')

        sample = self.gateway.build_authorization_request(self.money, self.credit_card)  #  TODO  as usual, options! and respect the body!

        self.assert_xml(sample, lambda XML:
                XML.Request(
                  XML.AC(
                    XML.CommonData(
                      XML.CommonMandatory(
                        XML.AccountNum('4012888888881', AccountTypeInd='91'),
                        XML.POSDetails(POSEntryMode='01'),
                        XML.MerchantID('123456789012'),
                        XML.TerminalID('001', TermEntCapInd='05',
                                                CATInfoInd='06',
                                                TermLocInd='01',
                                                CardPresentInd='N',
                                                POSConditionCode='59',
                                                AttendedTermDataInd='01'),
                        XML.BIN('000002'),
                        XML.OrderID('1234567890123456'),
                        XML.AmountDetails(
                          XML.Amount('000000005000')),
                        XML.TxTypeCommon(TxTypeID='G'),
                        XML.Currency(CurrencyCode='840', CurrencyExponent='2'),
                        XML.CardPresence(
                          XML.CardNP(
                            XML.Exp('1205'))),
                        XML.TxDateTime(), AuthOverrideInd='N',
                                            LangInd='00',
                                            CardHolderAttendanceInd='01',
                                            HcsTcsInd='T',
                                            TxCatg='7',
                                            MessageType='A',
                                            Version='2',
                                            TzCode='705'),
                      XML.CommonOptional(
                        XML.Comments('This is an AVS/CVV2 auth request'),
                        XML.ShippingRef('FEDEX WB12345678 Pri 1'),
                        XML.CardSecVal('705', CardSecInd='1'),
                        XML.ECommerceData(
                          XML.ECOrderNum('1234567890123456'), ECSecurityInd='07'))),
                    XML.Auth(
                      XML.AuthMandatory(FormatInd='H'),
                      XML.AuthOptional(
                        XML.AVSextended(
                          XML.AVSname('JOE SMITH'),
                          XML.AVSaddress1('1234 WEST MAIN STREET'),
                          XML.AVSaddress2('SUITE 123'),
                          XML.AVScity('TAMPA'),
                          XML.AVSstate('FL'),
                          XML.AVSzip('33123-1234'),
                          XML.AVScountryCode('US')))),
                    XML.Cap(
                      XML.CapMandatory(
                        XML.EntryDataSrc('02')),
                      XML.CapOptional())))
                  )

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

    def test_parse_purchase_response(self):
        return # TODO  drain me away!
#  def successful_purchase_response

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

    def assemble_billing_address(self):
        self.options = {
            'order_id': '1',
            'description': 'Time-Turner',
            'email': 'hgranger@hogwarts.edu',
            'customer': '947', #  TODO  test this going through
            'ip': '192.168.1.1', #  TODO  test this going through
            }
        billing_address = {
            'address1': '444 Main St.',
            'address2': 'Apt 2',
            'company': 'ACME Software', #  CONSIDER  Orbital seems to have no slot for the company
            'phone': '222-222-2222',
            'zip': '77777',
            'city': 'Dallas',
            'country': 'USA',
            'state': 'TX'
            }
        self.options['billing_address'] = billing_address
        return billing_address

    def assemble_billing_address_too(self):
        self.options = {
            'order_id': '1',
            'description': 'Time-Turner',
            'email': 'hgranger@hogwarts.edu',
            'customer': '947',
            'ip': '192.168.1.1',
            }
        billing_address = {
            'address1': '444 Main St.',
            'company': 'ACME Software',
            'phone': '222-222-2222',
            'zip': '77777',
            'city': 'Dallas',
            'country': 'USA',
            'state': 'TX'
            }
        self.options['billing_address'] = billing_address

    def test_build_authorization_request(self):
        self.money = Money('100.00', 'USD')

        billing_address = self.assemble_billing_address()
        self.options['login'] = 'Triwizard'  #  TODO  is the one true standard interface "login" or "username"
        self.options['password'] = 'Tournament'

        message = self.gateway.build_authorization_request_TODO(self.money, self.credit_card, **self.options)

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

    def test_build_authorization_request_with_alternative_money(self):
        Nuevo_Sol = 'PEN'
        Nuevo_Sol_numeric = '604'
        self.money = Money('200.00', Nuevo_Sol)
        billing_address = self.assemble_billing_address()
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)

        self.assert_xml(message, lambda x:
                             x.Request(
                                 x.AC(
                                    XML.CommonData(
                                      XML.CommonMandatory(
                                        XML.Currency(CurrencyCode=Nuevo_Sol_numeric,
                                                     CurrencyExponent='2'  #  TODO  vary this
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

# holy f--- do we gotta do all that??

    def test_build_authorization_request_without_street2(self):
        self.money = Money('2.00', 'USD')

        self.assemble_billing_address_too()

        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)

        # self.assert_('<street2></street2>' in message)  #  TODO  assert_contains

    def successful_purchase_response(self):  #  TODO  get a real one!
        return self.successful_authorization_response()


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

#  TODO  trust everything below this line:

#class BraintreeTest < Test::Unit::TestCase
#
#  def setup
#    @gateway = BraintreeGateway.new(
#      :login => 'LOGIN',
#      :password => 'PASSWORD'
#    )
#
#    @credit_card = credit_card
#    @amount = 100
#
#    @options = { :billing_address => address }
#  end
#
#  def test_successful_purchase
#    @gateway.expects(:ssl_post).returns(successful_purchase_response)
#
#    assert response = @gateway.authorize(@amount, @credit_card, @options)
#    assert_instance_of Response, response
#    assert_success response
#    assert_equal '510695343', response.authorization
#  end
#
#  def test_failed_purchase
#    @gateway.expects(:ssl_post).returns(failed_purchase_response)
#
#    assert response = @gateway.authorize(@amount, @credit_card, @options)
#    assert_instance_of Response, response
#    assert_failure response
#  end
#
#  def test_add_shipping_address
#    result = {}
#
#    @gateway.send(:add_address, result,   {:address1 => '164 Waverley Street', :country => 'US', :state => 'CO'},"shipping" )
#    assert_equal ["shipping_address1", "shipping_city", "shipping_company", "shipping_country", "shipping_phone", "shipping_state", "shipping_zip"], result.stringify_keys.keys.sort
#    assert_equal 'CO', result["shipping_state"]
#    assert_equal '164 Waverley Street', result["shipping_address1"]
#    assert_equal 'US', result["shipping_country"]
#
#  end
#
#  def test_supported_countries
#    assert_equal ['US'], BraintreeGateway.supported_countries
#  end
#
#  def test_supported_card_types
#    assert_equal [:visa, :master, :american_express, :discover], BraintreeGateway.supported_cardtypes
#  end
#
#  def test_adding_store_adds_vault_id_flag
#    result = {}
#
#    @gateway.send(:add_creditcard, result, @credit_card, :store => true)
#    assert_equal ["ccexp", "ccnumber", "customer_vault", "cvv", "firstname", "lastname"], result.stringify_keys.keys.sort
#    assert_equal 'add_customer', result[:customer_vault]
#  end
#
#  def test_blank_store_doesnt_add_vault_flag
#    result = {}
#
#    @gateway.send(:add_creditcard, result, @credit_card, {} )
#    assert_equal ["ccexp", "ccnumber", "cvv", "firstname", "lastname"], result.stringify_keys.keys.sort
#    assert_nil result[:customer_vault]
#  end
#
#  def test_accept_check
#    post = {}
#    check = Check.new(:name => 'Fred Bloggs',
#                      :routing_number => '111000025',
#                      :account_number => '123456789012',
#                      :account_holder_type => 'personal',
#                      :account_type => 'checking')
#    @gateway.send(:add_check, post, check, {})
#    assert_equal %w[account_holder_type account_type checkaba checkaccount checkname payment], post.stringify_keys.keys.sort
#  end
#
#  def test_funding_source
#    assert_equal :check, @gateway.send(:determine_funding_source, Check.new)
#    assert_equal :credit_card, @gateway.send(:determine_funding_source, @credit_card)
#    assert_equal :vault, @gateway.send(:determine_funding_source, '12345')
#  end
#
#  def test_avs_result
#    @gateway.expects(:ssl_post).returns(successful_purchase_response)
#
#    response = @gateway.purchase(@amount, @credit_card)
#    assert_equal 'N', response.avs_result['code']
#  end
#
#  def test_cvv_result
#    @gateway.expects(:ssl_post).returns(successful_purchase_response)
#
#    response = @gateway.purchase(@amount, @credit_card)
#    assert_equal 'N', response.cvv_result['code']
#  end
#
#  private
#
#  def failed_purchase_response
#    'response=2&responsetext=DECLINE&authcode=&transactionid=510695919&avsresponse=N&cvvresponse=N&orderid=50357660b0b3ef16f72a3d3b83c46983&type=sale&response_code=200'
#  end
#end
