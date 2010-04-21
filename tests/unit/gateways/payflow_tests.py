
from merchant_gateways.billing.gateways.payflow import Payflow, format, xStr
from merchant_gateways.billing.credit_card import CreditCard
from tests.test_helper import *
from pprint import pprint


class PayflowTests(MerchantGatewaysTestSuite, MerchantGatewaysTestSuite.CommonTests):

    def gateway_type(self):
        return Payflow

    def mock_webservice(self, response):
        self.mock_post_webservice(response)

    def assert_successful_authorization(self):

        assert self.response.is_test
        self.assertEqual('Approved', self.response.message)

        # TODO  assert the response is None if we epic-fail (oh, and trap exceptions)

        args = ('https://pilot-payflowpro.paypal.com', '<?xml version="1.0" encoding="UTF-8"?>\n<XMLPayRequest Timeout="30" version="2.1"\nxmlns="http://www.paypal.com/XMLPay">\n  <RequestData>\n    <Vendor>LOGIN</Vendor>\n    <Partner>PayPal</Partner>\n    <Transactions>\n      <Transaction>\n        <Verbosity>MEDIUM</Verbosity>\n        <Authorization>\n  <PayData>\n    <Invoice>\n      \n      <TotalAmt Currency="USD">1.00</TotalAmt>\n    </Invoice>\n    <Tender>\n      <Card>\n        <CardType>Visa</CardType>\n        <CardNum>4242424242424242</CardNum>\n        <ExpDate>201109</ExpDate>\n        <NameOnCard>Longbob</NameOnCard>\n        <CVNum>123</CVNum>\n        <ExtData Name="LASTNAME" Value="Longsen" />\n      </Card>\n    </Tender>\n  </PayData>\n</Authorization>\n      </Transaction>\n    </Transactions>\n  </RequestData>\n  <RequestAuth>\n    <UserPass>\n      <User>LOGIN</User>\n      <Password>PASSWORD</Password>\n    </UserPass>\n  </RequestAuth>\n</XMLPayRequest>\n', {'Content-Length': '904', 'Content-Type': 'text/xml', 'X-VPS-VIT-Integration-Product': "TODO what's my name", 'X-VPS-Request-ID': 'you neek', 'X-VPS-VIT-Runtime-Version': '4.2', 'X-VPS-Client-Timeout': '30'})
                       #  TODO  push out & beautify that string  ^

        self.gateway.post_webservice.assert_called_with(*args)  #  TODO  beautify the response

        #~ assert response = self.gateway.authorize(self.amount, self.credit_card)

        # TODO  test these        print self.response.params
        #        self.assertEqual('508141794', self.response.params['authorization'])  #  TODO  also self.response.authorization
        self.assertEqual('VUJN1A6E11D9', self.response.authorization)

    def assert_failed_authorization(self):
        self.assertEqual( "Declined", self.response.message)  #  TODO  what's the other message?
        # TODO assert self.response.params == {}
        self.assert_none(self.response.fraud_review)
        assert self.response.avs_result.__dict__ == {'message': 'Street address and 5-digit postal code match.', 'code': 'Y', 'postal_match': 'Y', 'street_match': 'Y'}
        assert self.response.message == 'Declined'
        assert self.response.authorization == 'VUJN1A6E11D9'
        assert self.response.is_test

    def test_successful_purchase(self):
        pass

    def successful_purchase_response(self):  #  TODO  this is bogus! What does a real one look like???
        return '''<ResponseData>
                    <Result>0</Result>
                    <Message>Approved</Message>
                    <Partner>verisign</Partner>
                    <HostCode>000</HostCode>
                    <ResponseText>AP</ResponseText>
                    <PnRef>VUJN1A6E11D9</PnRef>
                    <IavsResult>N</IavsResult>
                    <ZipMatch>Match</ZipMatch>
                    <AuthCode>094016</AuthCode>
                    <Vendor>ActiveMerchant</Vendor>
                    <AvsResult>Y</AvsResult>
                    <StreetMatch>Match</StreetMatch>
                    <CvResult>Match</CvResult>
                </ResponseData>'''

    def test_avs_result(self):
        self.test_successful_authorization()  #  no jury would convict me
        avs = self.response.avs_result
        self.assert_equal( 'Y', avs.code )
        self.assert_equal( 'Y', avs.street_match )
        self.assert_equal( 'Y', avs.postal_match )

    def test_cvv_result(self):
        self.test_failed_authorization()
        self.assert_equal('M', self.response.cvv_result.code)

    def test_build_headers(self):
        self.assertEqual({'Content-Length': '42',
                             'Content-Type': 'text/xml',
                             'X-VPS-Client-Timeout': '30',
                             'X-VPS-Request-ID': 'you neek',
                             'X-VPS-VIT-Integration-Product': "TODO what's my name",
                             'X-VPS-VIT-Runtime-Version': '4.2'},
                         self.gateway.build_headers(42))

    def test_build_request(self):
        sample = self.gateway.build_request(reference)
        self.assert_match_xml(sample, xml_pay_request)

    def test_add_address_bill_to(self):
        address = self.gateway.add_address('BillTo',
                                           name= 'Severus Snape',
                                           phone='(555)555-5555',
                                           address1='1234 My Street',  #  TODO  address2 ?
                                           city='Ottowa',
                                           state='ON',
                                           country='CA',
                                           zip='K1C2N6'
                                            )
        self.assert_xml_text(address, '/BillTo/Name', 'Severus Snape')

        self.assert_match_xml('''<BillTo>
                                   <Name>Severus Snape</Name>
                                   <Phone>(555)555-5555</Phone>
                                   <Address>
                                     <Street>1234 My Street</Street>
                                     <City>Ottowa</City>
                                     <State>ON</State>
                                     <Country>CA</Country>
                                     <Zip>K1C2N6</Zip>
                                   </Address>
                                 </BillTo>''', address)  #  TODO  cover the email!

        self.assert_xml(address, lambda xml:
                xml.BillTo(
                       xml.State('ON'),
                       xml.Country('CA'),
                       xml.Zip('K1C2N6')
                    )
                )

    def test_add_address_ship_to(self):
        address = self.gateway.add_address('ShipTo', name= 'Regulus Black',
                                           phone='(555)555-5555',
                                           address1='1234 My Street',
                                           city='Ottowa',
                                           state='ON',
                                           country='CA',
                                           zip='K1C2N6'
                                            )
        self.assert_xml_text(address, '/ShipTo/Name', 'Regulus Black')

        self.assert_match_xml('''<ShipTo>
                                   <Name>Regulus Black</Name>
                                   <Phone>(555)555-5555</Phone>
                                   <Address>
                                     <Street>1234 My Street</Street>
                                     <City>Ottowa</City>
                                     <State>ON</State>
                                     <Country>CA</Country>
                                     <Zip>K1C2N6</Zip>
                                   </Address>
                                 </ShipTo>''', address)  #  TODO  cover the other variables

    def test_add_different_address(self):
        address = self.gateway.add_address( 'ShipTo',
                                            name='Dumbledore',
                                            address1='39446 Hogwart Avenue',
                                            city='London',
                                            state='England', # so?
                                            country='UK',
                                            zip='N1 0',
                                            email='dumbledore@hogwarts.edu',
                                            phone='1-526-865-8896' )

        self.assert_xml_text(address, '/ShipTo/Name', 'Dumbledore')
        addy = self.assert_xml(address, '/ShipTo/Address')
        self.assert_xml_text(addy, 'Street', '39446 Hogwart Avenue')
        self.assert_xml_text(addy, 'City', 'London')
        self.assert_xml_text(addy, 'State', 'England')
        self.assert_xml_text(addy, 'Country', 'UK')
        self.assert_xml_text(addy, 'Zip', 'N1 0')

    #          xml.tag! 'Name', address[:name] unless address[:name].blank?
#          xml.tag! 'EMail', options[:email] unless options[:email].blank?
#          xml.tag! 'Phone', address[:phone] unless address[:phone].blank?
# TODO!         xml.tag! 'CustCode', options[:customer] if !options[:customer].blank? && tag == 'BillTo'
#
#          xml.tag! 'Address' do # TODO etc!
#            xml.tag! 'Street', address[:address1] unless address[:address1].blank?
#            xml.tag! 'City', address[:city] unless address[:city].blank?
#            xml.tag! 'State', address[:state].blank? ? "N/A" : address[:state]
#            xml.tag! 'Country', address[:country] unless address[:country].blank?
#            xml.tag! 'Zip', address[:zip] unless address[:zip].blank?

    def test_build_credit_card_request(self):
        options = { 'address': { 'name': 'Ron Weasley' } }
        sample = self.gateway.build_credit_card_request('authorization', '1.00', self.credit_card, **options)
        self.assert_match_xml(reference, sample)

    def test_build_credit_card_request(self):
        options = { 'address': { 'name': 'Ron Weasley' } }  #  TODO  change stuff; then test it
        sample = self.gateway.build_credit_card_request('purchase', '1.00', self.credit_card, **options)
        self.assert_xml(sample, '//Sale/PayData')

    def test_build_credit_card_request_without_an_address(self):
        sample = self.gateway.build_credit_card_request('authorization', '1.00', self.credit_card)  # TODO options is not optional
        self.deny_xml(sample, '//BillTo')

    def test_build_credit_card_request_with_an_address_but_without_a_name(self):
        sample = self.gateway.build_credit_card_request('authorization', '1.00', self.credit_card, address= {'city': 'TODO'})
        #self.assert_match_xml(reference.replace('Ron Weasley', ''), sample)
        name = self.assert_xml(sample, '//BillTo/Name')  #  TODO  find empty name
        # self.assertNone(name.text)

        #  CONSIDER  hallow as a feature if the address is a empty {}, it disappears anyway

    def successful_authorization_response(self):
        return '''<ResponseData>
                    <Result>0</Result>
                    <Message>Approved</Message>
                    <Partner>verisign</Partner>
                    <HostCode>000</HostCode>
                    <ResponseText>AP</ResponseText>
                    <PnRef>VUJN1A6E11D9</PnRef>
                    <IavsResult>N</IavsResult>
                    <ZipMatch>Match</ZipMatch>
                    <AuthCode>094016</AuthCode>
                    <Vendor>ActiveMerchant</Vendor>
                    <AvsResult>Y</AvsResult>
                    <StreetMatch>Match</StreetMatch>
                    <CvResult>Match</CvResult>
                </ResponseData>'''

    def failed_authorization_response(self):
        return '''<ResponseData>
                    <Result>12</Result>
                    <Message>Declined</Message>
                    <Partner>verisign</Partner>
                    <HostCode>000</HostCode>
                    <ResponseText>AP</ResponseText>
                    <PnRef>VUJN1A6E11D9</PnRef>
                    <IavsResult>N</IavsResult>
                    <ZipMatch>Match</ZipMatch>
                    <AuthCode>094016</AuthCode>
                    <Vendor>ActiveMerchant</Vendor>
                    <AvsResult>Y</AvsResult>
                    <StreetMatch>Match</StreetMatch>
                    <CvResult>Match</CvResult>
                </ResponseData>'''

    def test_add_credit_card(self):
        cc = CreditCard(verification_value="123", number="4242424242424242", year=2011, card_type="visa",
                                month=9, last_name="Longsen", first_name="Longbob")

        xml = self.gateway.add_credit_card(cc)

        card = self.assert_xml(xml, '/Card')
        self.assert_xml_text(card, 'CardType', 'Visa')
        self.assert_xml_text(card, 'CardNum', '4242424242424242')
        self.assert_xml_text(card, 'ExpDate', '201109')
        self.assert_xml_text(card, 'NameOnCard', 'Longbob')
        self.assert_xml_text(card, 'CVNum', '123')
        extdata = self.assert_xml(card, 'ExtData[ @Name = "LASTNAME" ]')
        self.assert_equal(extdata.attrib['Value'], 'Longsen')
        self.deny_xml(card, 'ExtData[ @Name = "CardIssue" ]')

    def test_add_credit_card_with_card_issue(self):
        cc = CreditCard(verification_value="123", number="5641820000000005", year=2011, issue_number=1,
                        card_type="switch",
                        month=9, last_name="Longsen", first_name="Longbob")

        xml = self.gateway.add_credit_card(cc)

        self.assert_match_xml( '''<Card>
                                      <CardType>Switch</CardType>
                                      <CardNum>5641820000000005</CardNum>
                                      <ExpDate>201109</ExpDate>
                                      <NameOnCard>Longbob</NameOnCard>
                                      <CVNum>123</CVNum>
                                      <ExtData Name="LASTNAME" Value="Longsen"/>
                                      <ExtData Name="CardIssue" Value="01"/>
                                    </Card>''', xml )

    def test_expdate(self):
        self.assert_equal('209012', self.gateway.expdate(self.credit_card))

    def test_format(self):
        self.credit_card.issue_number = 9
        self.assert_equal('09', format(self.credit_card.issue_number, two_digits=True))

'''
class PayflowTest < Test::Unit::TestCase
  def setup
    Base.mode = :test

    @gateway = PayflowGateway.new( # TODO
      :login => 'LOGIN',
      :password => 'PASSWORD'
    )

    @amount = 100
    @credit_card = credit_card('4242424242424242')
    @options = { :billing_address => address }
  end


  def test_partial_avs_match
    @gateway.expects(:ssl_post).returns(successful_duplicate_response)

    response = @gateway.purchase(@amount, @credit_card, @options)
    assert_equal 'A', response.avs_result['code']
    assert_equal 'Y', response.avs_result['street_match']
    assert_equal 'N', response.avs_result['postal_match']
  end

  def test_using_test_mode
    assert @gateway.test?
  end

  def test_overriding_test_mode
    Base.gateway_mode = :production

    gateway = PayflowGateway.new(
      :login => 'LOGIN',
      :password => 'PASSWORD',
      :test => true
    )

    assert gateway.test?
  end

  def test_using_production_mode
    Base.gateway_mode = :production

    gateway = PayflowGateway.new(
      :login => 'LOGIN',
      :password => 'PASSWORD'
    )

    assert !gateway.test?
  end

  def test_partner_class_accessor
    assert_equal 'PayPal', PayflowGateway.partner
    gateway = PayflowGateway.new(:login => 'test', :password => 'test')
    assert_equal 'PayPal', gateway.options[:partner]
  end

  def test_partner_class_accessor_used_when_passed_in_partner_is_blank
    assert_equal 'PayPal', PayflowGateway.partner
    gateway = PayflowGateway.new(:login => 'test', :password => 'test', :partner => '')
    assert_equal 'PayPal', gateway.options[:partner]
  end

  def test_passed_in_partner_overrides_class_accessor
    assert_equal 'PayPal', PayflowGateway.partner
    gateway = PayflowGateway.new(:login => 'test', :password => 'test', :partner => 'PayPalUk')
    assert_equal 'PayPalUk', gateway.options[:partner]
  end

  def test_express_instance
    gateway = PayflowGateway.new(
      :login => 'test',
      :password => 'password'
    )
    express = gateway.express
    assert_instance_of PayflowExpressGateway, express
    assert_equal 'PayPal', express.options[:partner]
    assert_equal 'test', express.options[:login]
    assert_equal 'password', express.options[:password]
  end

  def test_default_currency
    assert_equal 'USD', PayflowGateway.default_currency
  end

  def test_supported_countries
    assert_equal ['US', 'CA', 'SG', 'AU'], PayflowGateway.supported_countries
  end

  def test_supported_card_types
    assert_equal [:visa, :master, :american_express, :jcb, :discover, :diners_club], PayflowGateway.supported_cardtypes
  end

  def test_initial_recurring_transaction_missing_parameters
    assert_raises ArgumentError do
      response = @gateway.recurring(@amount, @credit_card,
        :periodicity => :monthly,
        :initial_transaction => { }
      )
    end
  end

  def test_initial_purchase_missing_amount
    assert_raises ArgumentError do
      response = @gateway.recurring(@amount, @credit_card,
        :periodicity => :monthly,
        :initial_transaction => { :amount => :purchase }
      )
    end
  end

  def test_successful_recurring_action
    @gateway.stubs(:ssl_post).returns(successful_recurring_response)

    response = @gateway.recurring(@amount, @credit_card, :periodicity => :monthly)

    assert_instance_of PayflowResponse, response
    assert_success response
    assert_equal 'RT0000000009', response.profile_id
    assert response.test?
    assert_equal "R7960E739F80", response.authorization
  end

  def test_recurring_profile_payment_history_inquiry
    @gateway.stubs(:ssl_post).returns(successful_payment_history_recurring_response)

    response = @gateway.recurring_inquiry('RT0000000009', :history => true)
    assert_equal 1, response.payment_history.size
    assert_equal '1', response.payment_history.first['payment_num']
    assert_equal '7.25', response.payment_history.first['amt']
  end

  def test_recurring_profile_payment_history_inquiry_contains_the_proper_xml
    request = @gateway.send( :build_recurring_request, :inquiry, nil, :profile_id => 'RT0000000009', :history => true)
    assert_match %r(<PaymentHistory>Y</PaymentHistory), request
  end

  def test_format_issue_number
    xml = Builder::XmlMarkup.new
    credit_card = credit_card("5641820000000005",
      :type         => "switch",
      :issue_number => 1
    )

    @gateway.send(:add_credit_card, xml, credit_card)
    doc = REXML::Document.new(xml.target!)
    node = REXML::XPath.first(doc, '/Card/ExtData')
    assert_equal '01', node.attributes['Value']
  end

  def test_duplicate_response_flag
    @gateway.expects(:ssl_post).returns(successful_duplicate_response)

    response = @gateway.authorize(@amount, @credit_card, @options)
    assert_success response
    assert response.params['duplicate']
  end

  def test_ensure_gateway_uses_safe_retry
    assert @gateway.retry_safe
  end

  private
  def successful_recurring_response
    <<-XML
<ResponseData>
  <Result>0</Result>
  <Message>Approved</Message>
  <Partner>paypal</Partner>
  <RPRef>R7960E739F80</RPRef>
  <Vendor>ActiveMerchant</Vendor>
  <ProfileId>RT0000000009</ProfileId>
</ResponseData>
  XML
  end

  def successful_payment_history_recurring_response
    <<-XML
<ResponseData>
  <Result>0</Result>
  <Partner>paypal</Partner>
  <RPRef>R7960E739F80</RPRef>
  <Vendor>ActiveMerchant</Vendor>
  <ProfileId>RT0000000009</ProfileId>
  <RPPaymentResult>
    <PaymentNum>1</PaymentNum>
    <PNRef>V18A0D3048AF</PNRef>
    <TransTime>12-Jan-08 04:30 AM</TransTime>
    <Result>0</Result>
    <Tender>C</Tender>
    <Amt Currency="7.25"></Amt>
    <TransState>6</TransState>
  </RPPaymentResult>
</ResponseData>
  XML
  end


  def successful_duplicate_response
    <<-XML
<?xml version="1.0"?>
<XMLPayResponse xmlns="http://www.verisign.com/XMLPay">
	<ResponseData>
		<Vendor>ActiveMerchant</Vendor>
		<Partner>paypal</Partner>
		<TransactionResults>
			<TransactionResult Duplicate="true">
				<Result>0</Result>
				<ProcessorResult>
					<AVSResult>A</AVSResult>
					<CVResult>M</CVResult>
					<HostCode>A</HostCode>
				</ProcessorResult>
				<IAVSResult>N</IAVSResult>
				<AVSResult>
					<StreetMatch>Match</StreetMatch>
					<ZipMatch>No Match</ZipMatch>
				</AVSResult>
				<CVResult>Match</CVResult>
				<Message>Approved</Message>
				<PNRef>V18A0CBB04CF</PNRef>
				<AuthCode>692PNI</AuthCode>
				<ExtData Name="DATE_TO_SETTLE" Value="2007-11-28 10:53:50"/>
			</TransactionResult>
		</TransactionResults>
	</ResponseData>
</XMLPayResponse>
    XML
  end
end
'''

# CONSIDER  does Payflow have a remote test mode?

#  TODO  better name for reference
reference = '''<Authorization>
  <PayData>
    <Invoice>
          <BillTo>
            <Name>Ron Weasley</Name>
            <Phone>(555)555-5555</Phone>
            <Address>
              <Street>1234 My Street</Street>
              <City>Ottawa</City>
              <State>ON</State>
              <Country>CA</Country>
              <Zip>K1C2N6</Zip>
            </Address>
          </BillTo>
      <TotalAmt Currency="USD">1.00</TotalAmt>
    </Invoice>
    <Tender>
      <Card>
        <CardType>Visa</CardType>
        <CardNum>4242424242424242</CardNum>
        <ExpDate>201109</ExpDate>
        <NameOnCard>Longbob</NameOnCard>
        <CVNum>123</CVNum>
        <ExtData Name="LASTNAME" Value="Longsen" />
      </Card>
    </Tender>
  </PayData>
</Authorization>'''

'''      def build_credit_card_request(action, money, credit_card, options)
        xml = Builder::XmlMarkup.new
        xml.tag! TRANSACTIONS[action] do
          xml.tag! 'PayData' do
            xml.tag! 'Invoice' do
              xml.tag! 'CustIP', options[:ip] unless options[:ip].blank?
              xml.tag! 'InvNum', options[:order_id].to_s.gsub(/[^\w.]/, '') unless options[:order_id].blank?
              xml.tag! 'Description', options[:description] unless options[:description].blank?

              billing_address = options[:billing_address] || options[:address]
              add_address(xml, 'BillTo', billing_address, options) if billing_address
              add_address(xml, 'ShipTo', options[:shipping_address], options) if options[:shipping_address]

              xml.tag! 'TotalAmt', amount(money), 'Currency' => options[:currency] || currency(money)
            end

            xml.tag! 'Tender' do
              add_credit_card(xml, credit_card)
            end
          end
        end
        xml.target!
      end

      def add_address(xml, tag, address, options)
        return if address.nil?
        xml.tag! tag do
          xml.tag! 'Name', address[:name] unless address[:name].blank?
          xml.tag! 'EMail', options[:email] unless options[:email].blank?
          xml.tag! 'Phone', address[:phone] unless address[:phone].blank?
          xml.tag! 'CustCode', options[:customer] if !options[:customer].blank? && tag == 'BillTo'

          xml.tag! 'Address' do # TODO etc!
            xml.tag! 'Street', address[:address1] unless address[:address1].blank?
            xml.tag! 'City', address[:city] unless address[:city].blank?
            xml.tag! 'State', address[:state].blank? ? "N/A" : address[:state]
            xml.tag! 'Country', address[:country] unless address[:country].blank?
            xml.tag! 'Zip', address[:zip] unless address[:zip].blank?
      '''

xml_pay_request = '''<?xml version="1.0" encoding="UTF-8"?>
<XMLPayRequest Timeout="30" version="2.1"
xmlns="http://www.paypal.com/XMLPay">
  <RequestData>
    <Vendor>LOGIN</Vendor>
    <Partner>PayPal</Partner>
    <Transactions>
      <Transaction>
        <Verbosity>MEDIUM</Verbosity>
        <Authorization>
          <PayData>
            <Invoice>
              <BillTo>
                <Name>Ron Weasley</Name>
                <Phone>(555)555-5555</Phone>
                <Address>
                  <Street>1234 My Street</Street>
                  <City>Ottawa</City>
                  <State>ON</State>
                  <Country>CA</Country>
                  <Zip>K1C2N6</Zip>
                </Address>
              </BillTo>
              <TotalAmt Currency="USD">1.00</TotalAmt>
            </Invoice>
            <Tender>
              <Card>
                <CardType>Visa</CardType>
                <CardNum>4242424242424242</CardNum>
                <ExpDate>201109</ExpDate>
                <NameOnCard>Longbob</NameOnCard>
                <CVNum>123</CVNum>
                <ExtData Name="LASTNAME" Value="Longsen" />
              </Card>
            </Tender>
          </PayData>
        </Authorization>
      </Transaction>
    </Transactions>
  </RequestData>
  <RequestAuth>
    <UserPass>
      <User>LOGIN</User>
      <Password>PASSWORD</Password>
    </UserPass>
  </RequestAuth>
</XMLPayRequest>
'''

  # TODO reconstruct ssl_post
