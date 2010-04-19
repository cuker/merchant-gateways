
from merchant_gateways.billing.gateways.cybersource import Cybersource
from tests.test_helper import *

#  TODO  get working with many versions of python & django

#  ERGO  all Decimal objects should optionally be Currency objects - Decimal + ISO country code

#  TODO  should we be inheriting (object)?
#  TODO logging!

class CybersourceTests(MerchantGatewaysTestSuite,
                       MerchantGatewaysTestSuite.CommonTests): # TODO

    def gateway_type(self):
        return Cybersource

    def mock_webservice(self, response):
        self.options['billing_address'] = {}  #  TODO  put something in there, throw an error if it ain't there
        self.mock_post_webservice(response)

    def assert_successful_authorization(self):
        order_id = str(self.options['order_id'])  #  TODO  put something in options
        requestID = '1842651133440156177166'
        requestToken = 'AP4JY+Or4xRonEAOERAyMzQzOTEzMEM0MFZaNUZCBgDH3fgJ8AEGAMfd+AnwAwzRpAAA7RT/'
        authorization = ';'.join([order_id, requestID, requestToken])
        self.assert_equal(authorization, self.response.authorization) # TODO  why not from <c:authorizationCode>004542</c:authorizationCode> ?
        assert self.response.success

    def assert_failed_authorization(self):
        self.assert_none(self.response.params['authorizationCode'])
        self.assert_none(self.response.fraud_review)

        assert self.response.params == {'authorizationCode': None, 'avsCodeRaw': None, 'currency': None,
                                        'merchantReferenceCode': 'a1efca956703a2a5037178a8a28f7357',
                                        'authorizedDateTime': None, 'reconciliationID': None,
                                        'amount': None,  #  TODO  is this valid?
                                        'requestID': '2004338415330008402434',
                                        'processorResponse': None, 'reasonCode': '231', 'avsCode': None,
                                        'decision': 'REJECT',
                                        'requestToken': 'Afvvj7KfIgU12gooCFE2/DanQIApt+G1OgTSA+R9PTnyhFTb0KRjgFY+ynyIFNdoKKAghwgx'}
        # TODO retire for is_test: 'test': False,
        # 'message': 'TODO',
        assert self.response.authorization == '1;2004338415330008402434;Afvvj7KfIgU12gooCFE2/DanQIApt+G1OgTSA+R9PTnyhFTb0KRjgFY+ynyIFNdoKKAghwgx'

    def assert_successful_purchase(self):

        '''TODO self.assert_equal( 'Successful transaction', self.response.message )'''

        '''self.gateway.expects(:ssl_post).returns(successful_purchase_response)


    assert_success response
    assert_equal "#{self.options[:order_id]};#{response.params['requestID']};#{response.params['requestToken']}", response.authorization
    assert response.test?
  end      '''

    def test_build_request(self):
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
                amount="1.00",
                authorizationCode="004542",
                authorizedDateTime="2007-07-12T18:31:53Z",
                avsCode="A",
                avsCodeRaw="I7",
                currency="USD",
                decision="ACCEPT",
                merchantReferenceCode="TEST11111111111",
                processorResponse="100",
                reasonCode="100",
                reconciliationID="23439130C40VZ2FB",
                requestID="1842651133440156177166",
                requestToken="AP4JY+Or4xRonEAOERAyMzQzOTEzMEM0MFZaNUZCBgDH3fgJ8AEGAMfd+AnwAwzRpAAA7RT/"
        )

    def test_parse(self):
        soap = self.successful_authorization_response()
        sample = self.gateway.parse(soap)
        # TODO
        reference = self.parsed_authentication_response()
        self.assert_equal(reference, sample)  #  TODO  invent an assert_diff that can spot differences

    def test_setup_address_hash(self):  #  TODO  everyone should fixup like these (Payflow does it a different way)
        g = self.gateway
        self.assert_equal({}, g.setup_address_hash()['billing_address'])
        self.assert_equal(dict(yo=42), g.setup_address_hash(billing_address=dict(yo=42))['billing_address'])
        self.assert_equal(dict(yo=42), g.setup_address_hash(address=dict(yo=42))['billing_address'])
        self.assert_equal({}, g.setup_address_hash()['shipping_address'])
        self.assert_equal(dict(yo=42), g.setup_address_hash(shipping_address=dict(yo=42))['shipping_address'])

    #  TODO  always credit_card never creditcard

    def test_build_auth_request(self):
        self.money = Decimal('1.00')

        self.options = {
            'order_id': '1',
            'description': 'Time-Turner',
            'email': 'hgranger@hogwarts.edu',
            'customer': '947',# TODO  test this going through
            'ip': '192.168.1.1', # TODO  test this going through
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

        message = self.gateway.build_auth_request(self.money, self.credit_card, **self.options)
#        {'start_month': None, 'verification_value': None, 'start_year': None, 'card_type': 'v', 'issue_number': None, }

        expect = '''<billTo>
                      <firstName>Hermione</firstName>
                      <lastName>Granger</lastName>
                      <street1>444 Main St.</street1>
                      <street2>Apt 2</street2>
                      <city>Dallas</city>
                      <state>TX</state>
                      <postalCode>77777</postalCode>
                      <country>USA</country>
                      <email>hgranger@hogwarts.edu</email>
                    </billTo>
                    <purchaseTotals>
                      <currency>USD</currency>
                      <grandTotalAmount>1.00</grandTotalAmount>
                    </purchaseTotals>
                    <card>
                      <accountNumber>4242424242424242</accountNumber>
                      <expirationMonth>12</expirationMonth>
                      <expirationYear>2090</expirationYear>
                      <cvNumber>123</cvNumber>
                      <cardType>001</cardType>
                    </card>
                    <ccAuthService run="true"/>
                    <businessRules>
                    </businessRules>'''

        # why exp_year 2090? Extendicreditus!

        self.assert_match_xml(expect, message)

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

        self.assert_('<street2></street2>' in message)  #  TODO  assert_contains

#    def test_avs_result(self):  #  TODO  move Cybersource to an "AvsStyle" module, and move this test to its abstract testor
#        self.gateway.expects(:ssl_post).returns(successful_purchase_response)
#
#        response = self.gateway.purchase(self.amount, self.credit_card, self.options)
#        assert_equal 'Y', response.avs_result['code']

    def successful_authorization_response(self): #  TODO  get a real SOAP lib!
        return '''<?xml version="1.0" encoding="utf-8"?>
                  <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Header>
                      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
                        wsu:Id="Timestamp-32551101">
                          <wsu:Created>2007-07-12T18:31:53.838Z</wsu:Created>
                        </wsu:Timestamp>
                      </wsse:Security>
                    </soap:Header>
                    <soap:Body>
                      <c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.26">
                        <c:merchantReferenceCode>TEST11111111111</c:merchantReferenceCode>
                        <c:requestID>1842651133440156177166</c:requestID>
                        <c:decision>ACCEPT</c:decision>
                        <c:reasonCode>100</c:reasonCode>
                        <c:requestToken>AP4JY+Or4xRonEAOERAyMzQzOTEzMEM0MFZaNUZCBgDH3fgJ8AEGAMfd+AnwAwzRpAAA7RT/</c:requestToken>
                        <c:purchaseTotals>
                          <c:currency>USD</c:currency>
                        </c:purchaseTotals>
                        <c:ccAuthReply>
                          <c:reasonCode>100</c:reasonCode>
                          <c:amount>1.00</c:amount>
                          <c:authorizationCode>004542</c:authorizationCode>
                          <c:avsCode>A</c:avsCode>
                          <c:avsCodeRaw>I7</c:avsCodeRaw>
                          <c:authorizedDateTime>2007-07-12T18:31:53Z</c:authorizedDateTime>
                          <c:processorResponse>100</c:processorResponse>
                          <c:reconciliationID>23439130C40VZ2FB</c:reconciliationID>
                        </c:ccAuthReply>
                      </c:replyMessage>
                    </soap:Body>
                  </soap:Envelope>
                  '''

    def failed_authorization_response(self):
        return '''<?xml version="1.0" encoding="utf-8"?>
                  <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Header>
                      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
                        wsu:Id="Timestamp-28121162">
                          <wsu:Created>2008-01-15T21:50:41.580Z</wsu:Created>
                        </wsu:Timestamp>
                      </wsse:Security>
                    </soap:Header>
                    <soap:Body>
                      <c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.26">
                        <c:merchantReferenceCode>a1efca956703a2a5037178a8a28f7357</c:merchantReferenceCode>
                        <c:requestID>2004338415330008402434</c:requestID>
                        <c:decision>REJECT</c:decision>
                        <c:reasonCode>231</c:reasonCode>
                        <c:requestToken>Afvvj7KfIgU12gooCFE2/DanQIApt+G1OgTSA+R9PTnyhFTb0KRjgFY+ynyIFNdoKKAghwgx</c:requestToken>
                        <c:ccAuthReply>
                          <c:reasonCode>231</c:reasonCode>
                        </c:ccAuthReply>
                      </c:replyMessage>
                    </soap:Body>
                  </soap:Envelope>
                  '''

        #  ERGO  complain that 'private' in a test case is irrational...

    def successful_purchase_response(self):
        return '''<?xml version="1.0" encoding="utf-8"?>
                  <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Header>
                      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
                        wsu:Id="Timestamp-2636690">
                          <wsu:Created>2008-01-15T21:42:03.343Z</wsu:Created>
                        </wsu:Timestamp>
                      </wsse:Security>
                    </soap:Header>
                    <soap:Body>
                      <c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.26">
                        <c:merchantReferenceCode>b0a6cf9aa07f1a8495f89c364bbd6a9a</c:merchantReferenceCode>
                        <c:requestID>2004333231260008401927</c:requestID>
                        <c:decision>ACCEPT</c:decision>
                        <c:reasonCode>100</c:reasonCode>
                        <c:requestToken>Afvvj7Ke2Fmsbq0wHFE2sM6R4GAptYZ0jwPSA+R9PhkyhFTb0KRjoE4+ynthZrG6tMBwjAtT</c:requestToken>
                        <c:purchaseTotals>
                          <c:currency>USD</c:currency>
                        </c:purchaseTotals>
                        <c:ccAuthReply>
                          <c:reasonCode>100</c:reasonCode>
                          <c:amount>1.00</c:amount>
                          <c:authorizationCode>123456</c:authorizationCode>
                          <c:avsCode>Y</c:avsCode>
                          <c:avsCodeRaw>Y</c:avsCodeRaw>
                          <c:cvCode>M</c:cvCode>
                          <c:cvCodeRaw>M</c:cvCodeRaw>
                          <c:authorizedDateTime>2008-01-15T21:42:03Z</c:authorizedDateTime>
                          <c:processorResponse>00</c:processorResponse>
                          <c:authFactorCode>U</c:authFactorCode>
                        </c:ccAuthReply>
                      </c:replyMessage>
                    </soap:Body>
                  </soap:Envelope>'''


'''
class CyberSourceTest < Test::Unit::TestCase
  def setup
    Base.gateway_mode = :test

    self.gateway = CyberSourceGateway.new(
      :login => 'l',
      :password => 'p'
    )

    self.amount = 100
    self.credit_card = credit_card('4111111111111111', :type => 'visa')
    self.declined_card = credit_card('801111111111111', :type => 'visa')

    self.options = { :billing_address => {
                  :address1 => '1234 My Street',
                  :address2 => 'Apt 1',
                  :company => 'Widgets Inc',
                  :city => 'Ottawa',
                  :state => 'ON',
                  :zip => 'K1C2N6',
                  :country => 'Canada',
                  :phone => '(555)555-5555'
               },

               :email => 'someguy1232self.fakeemail.net',
               :order_id => '1000',
               :line_items => [
                   {
                      :declared_value => self.amount,
                      :quantity => 2,
                      :code => 'default',
                      :description => 'Giant Walrus',
                      :sku => 'WA323232323232323'
                   },
                   {
                      :declared_value => self.amount,
                      :quantity => 2,
                      :description => 'Marble Snowcone',
                      :sku => 'FAKE1232132113123'
                   }
                 ],
          :currency => 'USD'
    }
  end

  def test_unsuccessful_authorization
    self.gateway.expects(:ssl_post).returns(unsuccessful_authorization_response)

    assert response = self.gateway.purchase(self.amount, self.credit_card, self.options)
    assert_instance_of Response, response
    assert_failure response
  end


  def test_successful_tax_request
    self.gateway.stubs(:ssl_post).returns(successful_tax_response)
    assert response = self.gateway.calculate_tax(self.credit_card, self.options)
    assert_equal Response, response.class
    assert response.success?
    assert response.test?
  end

  def test_successful_capture_request
    self.gateway.stubs(:ssl_post).returns(successful_authorization_response, successful_capture_response)
    assert response = self.gateway.authorize(self.amount, self.credit_card, self.options)
    assert response.success?
    assert response.test?
    assert response_capture = self.gateway.capture(self.amount, response.authorization)
    assert response_capture.success?
    assert response_capture.test?
  end

  def test_successful_purchase_request
    self.gateway.stubs(:ssl_post).returns(successful_capture_response)
    assert response = self.gateway.purchase(self.amount, self.credit_card, self.options)
    assert response.success?
    assert response.test?
  end

  def test_requires_error_on_purchase_without_order_id
    assert_raise(ArgumentError){ self.gateway.purchase(self.amount, self.credit_card, self.options.delete_if{|key, val| key == :order_id}) }
  end

  def test_requires_error_on_authorization_without_order_id
    assert_raise(ArgumentError){ self.gateway.purchase(self.amount, self.credit_card, self.options.delete_if{|key, val| key == :order_id}) }
  end

  def test_requires_error_on_tax_calculation_without_line_items
    assert_raise(ArgumentError){ self.gateway.calculate_tax(self.credit_card, self.options.delete_if{|key, val| key == :line_items})}
  end

  def test_default_currency
    assert_equal 'USD', CyberSourceGateway.default_currency
  end

  def test_cvv_result
    self.gateway.expects(:ssl_post).returns(successful_purchase_response)

    response = self.gateway.purchase(self.amount, self.credit_card, self.options)
    assert_equal 'M', response.cvv_result['code']
  end

  def test_successful_credit_request
    self.gateway.stubs(:ssl_post).returns(successful_capture_response, successful_credit_response)
    assert response = self.gateway.purchase(self.amount, self.credit_card, self.options)
    assert response.success?
    assert response.test?
    assert response_capture = self.gateway.credit(self.amount, response.authorization)
    assert response_capture.success?
    assert response_capture.test?
  end

  private

  def successful_tax_response
    <<-XML
<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Header>
<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="Timestamp-21248497"><wsu:Created>2007-07-11T18:27:56.314Z</wsu:Created></wsu:Timestamp></wsse:Security></soap:Header><soap:Body><c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.26"><c:merchantReferenceCode>TEST11111111111</c:merchantReferenceCode><c:requestID>1841784762620176127166</c:requestID><c:decision>ACCEPT</c:decision><c:reasonCode>100</c:reasonCode><c:requestToken>AMYJY9fl62i+vx2OEQYAx9zv/9UBZAAA5h5D</c:requestToken><c:taxReply><c:reasonCode>100</c:reasonCode><c:grandTotalAmount>1.00</c:grandTotalAmount><c:totalCityTaxAmount>0</c:totalCityTaxAmount><c:city>Madison</c:city><c:totalCountyTaxAmount>0</c:totalCountyTaxAmount><c:totalDistrictTaxAmount>0</c:totalDistrictTaxAmount><c:totalStateTaxAmount>0</c:totalStateTaxAmount><c:state>WI</c:state><c:totalTaxAmount>0</c:totalTaxAmount><c:postalCode>53717</c:postalCode><c:item id="0"><c:totalTaxAmount>0</c:totalTaxAmount></c:item></c:taxReply></c:replyMessage></soap:Body></soap:Envelope>
    XML
  end


  def successful_capture_response
    <<-XML
<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Header> <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="Timestamp-6000655"><wsu:Created>2007-07-17T17:15:32.642Z</wsu:Created></wsu:Timestamp></wsse:Security></soap:Header><soap:Body><c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.26"><c:merchantReferenceCode>test1111111111111111</c:merchantReferenceCode><c:requestID>1846925324700976124593</c:requestID><c:decision>ACCEPT</c:decision><c:reasonCode>100</c:reasonCode><c:requestToken>AP4JZB883WKS/34BEZAzMTE1OTI5MVQzWE0wQjEzBTUt3wbOAQUy3D7oDgMMmvQAnQgl</c:requestToken><c:purchaseTotals><c:currency>GBP</c:currency></c:purchaseTotals><c:ccCaptureReply><c:reasonCode>100</c:reasonCode><c:requestDateTime>2007-07-17T17:15:32Z</c:requestDateTime><c:amount>1.00</c:amount><c:reconciliationID>31159291T3XM2B13</c:reconciliationID></c:ccCaptureReply></c:replyMessage></soap:Body></soap:Envelope>
    XML
  end

  def successful_credit_response
    <<-XML
<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Header>
<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsu:Timestamp xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="Timestamp-5589339"><wsu:Created>2008-01-21T16:00:38.927Z</wsu:Created></wsu:Timestamp></wsse:Security></soap:Header><soap:Body><c:replyMessage xmlns:c="urn:schemas-cybersource-com:transaction-data-1.32"><c:merchantReferenceCode>TEST11111111111</c:merchantReferenceCode><c:requestID>2009312387810008401927</c:requestID><c:decision>ACCEPT</c:decision><c:reasonCode>100</c:reasonCode><c:requestToken>Af/vj7OzPmut/eogHFCrBiwYsWTJy1r127CpCn0KdOgyTZnzKwVYCmzPmVgr9ID5H1WGTSTKuj0i30IE4+zsz2d/QNzwBwAACCPA</c:requestToken><c:purchaseTotals><c:currency>USD</c:currency></c:purchaseTotals><c:ccCreditReply><c:reasonCode>100</c:reasonCode><c:requestDateTime>2008-01-21T16:00:38Z</c:requestDateTime><c:amount>1.00</c:amount><c:reconciliationID>010112295WW70TBOPSSP2</c:reconciliationID></c:ccCreditReply></c:replyMessage></soap:Body></soap:Envelope>
    XML
  end

end
'''

# ERGO  put us into the test report system and see what we look like!
