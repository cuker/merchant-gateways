from merchant_gateways import MerchantGatewayError
from merchant_gateways.billing.gateways.payflow import Payflow, format
from merchant_gateways.billing.gateways.gateway import xStr
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from merchant_gateways.tests.billing.gateways.payflow_suite import MerchantGatewaysPayflowSuite
from pprint import pprint
from money import Money

class PayflowTests( MerchantGatewaysPayflowSuite,
                    MerchantGatewaysTestSuite,
                    MerchantGatewaysTestSuite.CommonTests ):

    def gateway_type(self):
        return Payflow

    def assert_successful_authorization(self):
        '''
        All gateways must pass the common test,
        L{tests.test_helper.MerchantGatewaysTestSuite.CommonTests.test_successful_authorization}.

        That calls this assertion, in each concrete test suite, to assert
        this gateway's specific details.

        See U{http://broadcast.oreilly.com/2010/05/abstract-tests.html} for more on the the
        Abstract Test pattern
        '''

        assert self.response.is_test
        self.assertEqual('Approved', self.response.message)

        # TODO  assert the response is None if we epic-fail (oh, and trap exceptions)
        self.assert_webservice_called( # vendor, amount, currency card_type, cc_number, exp_date, cv_num,
                        self.gateway.post_webservice,
                                       'LOGIN',
                        '100.00',
                        'USD',  #  TODO  use self.money.currency here
                        'Visa',
                        '4242424242424242',
                        '209012',
                        self.credit_card.verification_value,
                        first_name='Hermione',
                        last_name='Granger',
                        username='LOGIN',
                        password='Y')
        
        #~ assert response = self.gateway.authorize(self.money, self.credit_card)

        # TODO  test these        print self.response.params
        #        self.assertEqual('508141794', self.response.params['authorization'])  #  TODO  also self.response.authorization
        self.assertEqual('VUJN1A6E11D9', self.response.authorization)
    
    def assert_successful_purchase(self):
        pass
        #TODO

    def assert_failed_authorization(self):
        self.assertEqual( "Declined", self.response.message)  #  TODO  what's the other message?
        # TODO assert self.response.params == {}
        self.assert_none(self.response.fraud_review)
        assert self.response.avs_result.__dict__ == {'message': 'Street address and 5-digit postal code match.', 'code': 'Y', 'postal_match': 'Y', 'street_match': 'Y'}
        assert self.response.message == 'Declined'
        assert self.response.authorization == 'VUJN1A6E11D9'
        assert self.response.is_test

    def test_failed_authorization(self):
        try:
            self.mock_webservice( self.failed_authorization_response(),
                lambda:  self.gateway.authorize(self.money, self.credit_card, **self.options) )
        except MerchantGatewayError, error:
            self.response = error.args[1]
        else:
            self.fail('No epic fail on declined auth')
        #assert self.response.is_test
        #self.assert_failure()
        #self.assert_failed_authorization()

    def test_successful_purchase_with_reference(self):
        authorization = 'Mobiliarbus'
        self.mock_webservice(self.successful_purchase_response(),
                             lambda: self.gateway.purchase(self.money, authorization) )
        self.response = self.gateway.response

    def test_successful_void(self):
        authorization = 'Mobiliarbus'


        self.mock_webservice(self.successful_void_response(),
                             lambda: self.gateway.void(authorization) )
        self.response = self.gateway.response

    def test_successful_credit(self):
        authorization = 'Mobiliarbus'
        
        self.mock_webservice(self.successful_credit_response(),
                             lambda: self.gateway.credit(Money('42.00', 'MAD'), authorization) )
        self.response = self.gateway.response

    def test_bad_configuration_raises_proper_eception(self):
        authorization = 'Mobiliarbus'
        try:
            self.mock_webservice(self.invalid_configuration_response(),
                                 lambda: self.gateway.credit(Money('42.00', 'MAD'), authorization) )
        except MerchantGatewayError:
            pass
        else:
            self.fail('Did not raise proper error') #TODO assert raises?

    def invalid_configuration_response(self):
        return '''<XMLPayResponse xmlns="http://www.paypal.com/XMLPay">
                    <ResponseData>
                        <Vendor>LOGIN</Vendor>
                        <Partner>paypal</Partner>
                        <TransactionResults>
                            <TransactionResult>
                                <Result>26</Result>
                                <Message>Invalid vendor account</Message>
                            </TransactionResult>
                        </TransactionResults>
                    </ResponseData>
                </XMLPayResponse>'''

    def successful_purchase_response(self):  #  TODO  this is bogus! What does a real one look like???
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
                            <AuthCode>094016</AuthCode>
                            <Vendor>ActiveMerchant</Vendor>
                            <AvsResult>
                                <ZipMatch>Match</ZipMatch>
                                <StreetMatch>Match</StreetMatch>
                            </AvsResult>
                            <CvResult>Match</CvResult>
                        </TransactionResult>
                    </TransactionResults>
                </ResponseData>
                </XMLPayResponse>'''

    def test_avs_result(self):
        self.test_successful_authorization()  #  no jury would convict me
        avs = self.response.avs_result
        self.assert_equal( 'Y', avs.code )
        self.assert_equal( 'Y', avs.street_match )
        self.assert_equal( 'Y', avs.postal_match )

    def test_cvv_result(self):
        self.test_failed_authorization()
        #self.assert_equal('M', self.response.cvv_result.code) #TODO wth is this for?

    def test_build_headers(self):
        headers = self.gateway.build_headers(42)
        del headers['X-VPS-Request-ID']
        self.assertEqual({'Content-Length': '42',
                             'Content-Type': 'text/xml',
                             'X-VPS-Client-Timeout': '30',
                             'X-VPS-VIT-Integration-Product': "TODO what's my name",
                             'X-VPS-VIT-Runtime-Version': '4.2'},
                         headers)

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
        address = xStr(address)
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
                       xml.Name('Severus Snape'),
                       xml.Address(
                           xml.State('ON'),
                           xml.Country('CA'),
                           xml.Zip('K1C2N6')
                       )
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
        address = xStr(address)
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
        sample = self.gateway.build_credit_card_request('authorization', Money('1.00', 'USD'), self.credit_card, **options)
        self.assert_match_xml(reference, sample)

    def test_build_credit_card_request(self):
        options = { 'address': { 'name': 'Ron Weasley' } }  #  TODO  change stuff; then test it
        sample = self.gateway.build_credit_card_request('purchase', Money('1.00', 'USD'), self.credit_card, **options)
        self.assert_xml(sample, '//Sale/PayData')
    
    def test_build_referenced_transaction_request(self):
        sample = self.gateway.build_reference_sale_or_authorization_request('purchase', Money('1.00', 'USD'), 'VUJN1A6E11D9')
        self.assert_xml(sample, '//Sale/PayData') #TODO look for our ref

    def test_build_credit_card_request_without_an_address(self):
        sample = self.gateway.build_credit_card_request('authorization', Money('1.00', 'USD'), self.credit_card)  # TODO options is not optional
        self.deny_xml(sample, '//BillTo')

    def test_build_credit_card_request_with_an_address_but_without_a_name(self):
        sample = self.gateway.build_credit_card_request('authorization', Money('1.00', 'USD'), self.credit_card, address= {'city': 'TODO'})
        #self.assert_match_xml(reference.replace('Ron Weasley', ''), sample)
        name = self.assert_xml(sample, '//BillTo/Name')  #  TODO  find empty name
        # self.assertNone(name.text)

        #  CONSIDER  hallow as a feature if the address is a empty {}, it disappears anyway

    def test_build_credit_card_request_and_check_all_its_xml_in_nauseating_detail(self):
        sample = self.gateway.build_credit_card_request( 'authorization',
                                                         Money('1.00', 'USD'),  #  TODO  use self.money
                                                         self.credit_card,
                                                         address= {'city': 'TODO'})

        self.assert_xml(sample, lambda XML:
                XML.Authorization(
          XML.PayData(
            XML.Invoice(
              XML.BillTo(
                XML.Name(),
                XML.Phone('(555)555-5555'),
                XML.Address(
                  XML.Street(),
                  XML.City('TODO'),
                  XML.State(),
                  XML.Country(),
                  XML.Zip())),
              XML.TotalAmt('1.00', Currency='USD')),
            XML.Tender(
              XML.Card(
                XML.CardType('Visa'),
                XML.CardNum('4242424242424242'),
                XML.ExpDate('209012'),
                XML.NameOnCard('Hermione'),
                XML.CVNum('456'),
                XML.ExtData(Name='LASTNAME', Value='Granger')))))
            )  #  CONSIDER  make this the dominant test of its ilk

    def test_build_credit_card_request_with_a_foreign_currency_TODO_abstract_me(self):

        Moroccan_Dirham = 'MAD'  #  What, Moor worry? [ C-: ]

        sample = self.gateway.build_credit_card_request( 'authorization',
                                                         Money('21.00', Moroccan_Dirham),
                                                         self.credit_card,
                                                         address= {'city': 'TODO'} )
        self.assert_xml(sample, lambda XML:
                                    XML.Authorization(
                                      XML.PayData(
                                        XML.Invoice(
                                          XML.TotalAmt('1.00', Currency=Moroccan_Dirham)),
                                      )))

    def test_add_credit_card(self):
        cc = CreditCard(verification_value="123", number="4242424242424242", year=2011, card_type="visa",
                                month=9, last_name="Longsen", first_name="Longbob")

        xml = self.gateway.add_credit_card(cc)

        card = self.assert_xml(xml, '/Card')
        self.assert_xml_text(card, 'CardType', 'Visa')
        self.assert_xml_text(card, 'CardNum', '4242424242424242')
        self.assert_xml_text(card, 'ExpDate', '201109')
        self.assert_xml_text(card, 'NameOnCard', 'Longbob Longsen')
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
                                      <NameOnCard>Longbob Longsen</NameOnCard>
                                      <CVNum>123</CVNum>
                                      <ExtData Name="LASTNAME" Value="Longsen"/>
                                      <ExtData Name="CardIssue" Value="01"/>
                                    </Card>''', xml )

    def test_expdate(self):
        self.assert_equal('209012', self.gateway.expdate(self.credit_card))

    def test_format(self):
        self.credit_card.issue_number = 9
        self.assert_equal('09', format(self.credit_card.issue_number, two_digits=True))

    def test_build_reference_request(self):
        xml = self.gateway.build_reference_request('void', None, 'nagini')

        self.assert_xml(xml, lambda xml:
            xml.Void(
                xml.PNRef('nagini')
                )
            )

    def test_build_reference_request_with_money(self):
        money = Money('42.00', 'XPD')  #  Palladium!
        xml = self.gateway.build_reference_request('void', money, 'O.W.L.')

        self.assert_xml(xml, lambda xml:
            xml.Void(
                xml.PNRef('O.W.L.'),
                xml.Invoice(
                    xml.TotalAmt( '42.00',
                                  Currency=str(money.currency) )
            ) ) )

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

#  TODO  better name for reference - and use or lose it!
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
      <Password>Y</Password>
    </UserPass>
  </RequestAuth>
</XMLPayRequest>
'''

  # TODO reconstruct ssl_post
