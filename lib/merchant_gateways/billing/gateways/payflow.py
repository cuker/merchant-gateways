
from gateway import Gateway, default_dict
from merchant_gateways.billing.avs_result import AVSResult
from pprint import pprint
from merchant_gateways.billing import response
from lxml import etree
from lxml.builder import ElementMaker # TODO document we do lxml only !
XML = ElementMaker()

def xStr(doc):
    return etree.tostring(doc, pretty_print=True)  #  TODO  take out pretty_print to go out wire!

# TODO use this      XMLNS = 'http://www.paypal.com/XMLPay'

# TODO  actually write a real post_webservice

# TODO  advise NB that active_merchant has braintree - of course!

class Payflow(Gateway):

    TEST_URL = 'https://pilot-payflowpro.paypal.com'
    LIVE_URL = 'https://payflowpro.paypal.com'

    def authorize(self, money, credit_card_or_reference, **options):
        self.request = self.build_sale_or_authorization_request('authorization', money, credit_card_or_reference, **options)
        return self.commit(self.request)

    def build_sale_or_authorization_request(self, action, money, credit_card_or_reference, **options):  # TODO  tdd each arg
#        if credit_card_or_reference.is_a?(String)
        #$ self.build_reference_sale_or_authorization_request(action, money, credit_card_or_reference, options)
 # TODO       else
        return self.build_credit_card_request(action, money, credit_card_or_reference, **options)

    def commit(self, request_body, request_type = None):
        request = self.build_request(request_body, request_type)
        headers = self.build_headers(len(request))  #  TODO  glyph length or byte length???

        url = self.is_test and self.TEST_URL or self.LIVE_URL  #  TODO  test the live url is live
        self.result = self.parse(self.post_webservice(url, request, headers))

    	# self.result = parse(ssl_post(test? ? TEST_URL : LIVE_URL, request, headers))'''

        passed = self.result['Result'] == '0'
        self.message = passed and 'Approved' or 'Declined'

    	return self.build_response( passed, self.message, None, # TODO response[:result] == "0", response[:message], response,
    	    is_test=self.is_test,
    	    authorization='VUJN1A6E11D9', # TODO > response[:pn_ref] || response[:rp_ref],
 #   	    :cvv_result => CVV_CODE[response[:cv_result]],
    	    avs_result = self.result['AvsResult']
            )  #  TODO  stash the response in self.response

    def purchase(self, money, credit_card_or_reference, **options):  #  TODO every purchase can work on a cc or ref!
        self.message = self.build_sale_or_authorization_request('purchase', money, credit_card_or_reference, **options)
        self.commit(self.message)

    def build_headers(self, content_length):  #  TODO doesn't an HTTP library take care of this for us?
        return {
          "Content-Type" : "text/xml",
          "Content-Length" : str(content_length),
      	  "X-VPS-Client-Timeout" : '30',  #  TODO  bfd?!
      	  "X-VPS-VIT-Integration-Product" : "TODO what's my name",
      	  "X-VPS-VIT-Runtime-Version" : '4.2',  #  TODO  what's my version?
      	  "X-VPS-Request-ID" : 'you neek'  #  TODO  _how_ unique?
     	  }

    def build_request(self, request_body, request_type=None):  # TODO  what's the request_type for?
        template = '''<?xml version="1.0" encoding="UTF-8"?>
<XMLPayRequest Timeout="30" version="2.1"
xmlns="http://www.paypal.com/XMLPay">
  <RequestData>
    <Vendor>LOGIN</Vendor>
    <Partner>PayPal</Partner>
    <Transactions>
      <Transaction>
        <Verbosity>MEDIUM</Verbosity>
        %(request_body)s
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
'''  #  TODO  vary all this data
        return template % { 'request_body': request_body }

    def build_credit_card_request(self, action, money, credit_card, **options):
        template = '''<%(transaction_type)s>
  <PayData>
    <Invoice>
      %(billing_address)s
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
</%(transaction_type)s>'''  # Warning - you can't reformat this because a hyperactive test will fail CONSIDER a fix!

        transaction_type = TRANSACTIONS[action]

        return template % dict( billing_address=self.add_address('BillTo', **options.get('address', {})),
                                transaction_type=transaction_type )
        # return template % { 'billing_address': self.add_address('BillTo', options.get('address', None)) }

    def add_address(self, _where_to, **address):
        if not address:  return ''
        address = default_dict(address)

        return xStr(
                XML(_where_to,
                      XML.Name(address['name']),
                      XML.Phone('(555)555-5555'),
                      XML.Address(
                              XML.Street(address['address1']),
                              XML.City(address['city']),
                              XML.State(address['state']),
                              XML.Country(address['country']),
                              XML.Zip(address['zip'])
                      )
                )
        )

    class Response(response.Response):
        def avs_result(self):
            print self.__dict__

# TODO      def profile_id
#        @params['profile_id']
 #     end

#      def payment_history
#        @payment_history ||= @params['rp_payment_result'].collect{ |result| result.stringify_keys } rescue []
#      end

    def parse(self, data):  #  TODO  use self.message
        response = {}
        from lxml import etree
        xml = etree.XML(data)
        root = xml.xpath('//ResponseData')[0]  #  TODO  useful, logged errors if these ain't here

        for node in root.xpath('*'):
            response[node.tag] = node.text
        '''
        root = REXML::XPath.first(xml, "//ResponseData")

        # REXML::XPath in Ruby 1.8.6 is now unable to match nodes based on their attributes
        tx_result = REXML::XPath.first(root, "//TransactionResult")

        if tx_result && tx_result.attributes['Duplicate'] == "true"
          response[:duplicate] = true
        end

        root.elements.to_a.each do |node|
          parse_element(response, node)  #  TODO  so what?
        end'''

        return response

    def build_response(self, success, message, response, **options):
        r = Payflow.Response(success, message, response, **options)
        r.avs_result = AVSResult(options['avs_result'])  #  TODO  ain't this what constructors are for??
        return r

'''      include PayflowCommonAPI

      RECURRING_ACTIONS = Set.new([:add, :modify, :cancel, :inquiry, :reactivate, :payment])

      self.supported_cardtypes = [:visa, :master, :american_express, :jcb, :discover, :diners_club]
      self.homepage_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_payflow-pro-overview-outside'
      self.display_name = 'PayPal Payflow Pro'

      def purchase(money, credit_card_or_reference, options = {})
        request = build_sale_or_authorization_request(:purchase, money, credit_card_or_reference, options)

        commit(request)
      end

      def credit(money, identification_or_credit_card, options = {})
        if identification_or_credit_card.is_a?(String)
          # Perform referenced credit
          request = build_reference_request(:credit, money, identification_or_credit_card, options)
        else
          # Perform non-referenced credit
          request = build_credit_card_request(:credit, money, identification_or_credit_card, options)
        end

        commit(request)
      end

      # Adds or modifies a recurring Payflow profile.  See the Payflow Pro Recurring Billing Guide for more details:
      # https://www.paypal.com/en_US/pdf/PayflowPro_RecurringBilling_Guide.pdf
      #
      # Several options are available to customize the recurring profile:
      #
      # * <tt>profile_id</tt> - is only required for editing a recurring profile
      # * <tt>starting_at</tt> - takes a Date, Time, or string in mmddyyyy format. The date must be in the future.
      # * <tt>name</tt> - The name of the customer to be billed.  If not specified, the name from the credit card is used.
      # * <tt>periodicity</tt> - The frequency that the recurring payments will occur at.  Can be one of
      # :bimonthly, :monthly, :biweekly, :weekly, :yearly, :daily, :semimonthly, :quadweekly, :quarterly, :semiyearly
      # * <tt>payments</tt> - The term, or number of payments that will be made
      # * <tt>comment</tt> - A comment associated with the profile
      def recurring(money, credit_card, options = {})
        options[:name] = credit_card.name if options[:name].blank? && credit_card
        request = build_recurring_request(options[:profile_id] ? :modify : :add, money, options) do |xml|
          add_credit_card(xml, credit_card) if credit_card
        end
        commit(request, :recurring)
      end

      def cancel_recurring(profile_id)
        request = build_recurring_request(:cancel, 0, :profile_id => profile_id)
        commit(request, :recurring)
      end

      def recurring_inquiry(profile_id, options = {})
        request = build_recurring_request(:inquiry, nil, options.update( :profile_id => profile_id ))
        commit(request, :recurring)
      end

      def express
        @express ||= PayflowExpressGateway.new(@options)
      end

      private

      def build_reference_sale_or_authorization_request(action, money, reference, options)
        xml = Builder::XmlMarkup.new
        xml.tag! TRANSACTIONS[action] do
          xml.tag! 'PayData' do
            xml.tag! 'Invoice' do
              xml.tag! 'TotalAmt', amount(money), 'Currency' => options[:currency] || currency(money)
            end
            xml.tag! 'Tender' do
              xml.tag! 'Card' do
                xml.tag! 'ExtData', 'Name' => 'ORIGID', 'Value' =>  reference
              end
            end
          end
        end
        xml.target!
      end

      def build_credit_card_request(action, money, credit_card, options)
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

      def add_credit_card(xml, credit_card)
        xml.tag! 'Card' do
          xml.tag! 'CardType', credit_card_type(credit_card)
          xml.tag! 'CardNum', credit_card.number
          xml.tag! 'ExpDate', expdate(credit_card)
          xml.tag! 'NameOnCard', credit_card.first_name
          xml.tag! 'CVNum', credit_card.verification_value if credit_card.verification_value?

          if requires_start_date_or_issue_number?(credit_card)
            xml.tag!('ExtData', 'Name' => 'CardStart', 'Value' => startdate(credit_card)) unless credit_card.start_month.blank? || credit_card.start_year.blank?
            xml.tag!('ExtData', 'Name' => 'CardIssue', 'Value' => format(credit_card.issue_number, :two_digits)) unless credit_card.issue_number.blank?
          end
          xml.tag! 'ExtData', 'Name' => 'LASTNAME', 'Value' =>  credit_card.last_name
        end
      end

      def credit_card_type(credit_card)
        return '' if card_brand(credit_card).blank?

        CARD_MAPPING[card_brand(credit_card).to_sym]
      end

      def expdate(creditcard)
        year  = sprintf("%.4i", creditcard.year)
        month = sprintf("%.2i", creditcard.month)

        "#{year}#{month}"
      end

      def startdate(creditcard)
        year  = format(creditcard.start_year, :two_digits)
        month = format(creditcard.start_month, :two_digits)

        "#{month}#{year}"
      end

      def build_recurring_request(action, money, options)
        unless RECURRING_ACTIONS.include?(action)
          raise StandardError, "Invalid Recurring Profile Action: #{action}"
        end

        xml = Builder::XmlMarkup.new
        xml.tag! 'RecurringProfiles' do
          xml.tag! 'RecurringProfile' do
            xml.tag! action.to_s.capitalize do
              unless [:cancel, :inquiry].include?(action)
                xml.tag! 'RPData' do
                  xml.tag! 'Name', options[:name] unless options[:name].nil?
                  xml.tag! 'TotalAmt', amount(money), 'Currency' => options[:currency] || currency(money)
                  xml.tag! 'PayPeriod', get_pay_period(options)
                  xml.tag! 'Term', options[:payments] unless options[:payments].nil?
                  xml.tag! 'Comment', options[:comment] unless options[:comment].nil?


                  if initial_tx = options[:initial_transaction]
                    requires!(initial_tx, [:type, :authorization, :purchase])
                    requires!(initial_tx, :amount) if initial_tx[:type] == :purchase

                    xml.tag! 'OptionalTrans', TRANSACTIONS[initial_tx[:type]]
                    xml.tag! 'OptionalTransAmt', amount(initial_tx[:amount]) unless initial_tx[:amount].blank?
                  end

                  xml.tag! 'Start', format_rp_date(options[:starting_at] || Date.today + 1 )
                  xml.tag! 'EMail', options[:email] unless options[:email].nil?

                  billing_address = options[:billing_address] || options[:address]
                  add_address(xml, 'BillTo', billing_address, options) if billing_address
                  add_address(xml, 'ShipTo', options[:shipping_address], options) if options[:shipping_address]
                end
                xml.tag! 'Tender' do
                  yield xml
                end
              end
              if action != :add
                xml.tag! "ProfileID", options[:profile_id]
              end
              if action == :inquiry
                xml.tag! "PaymentHistory", ( options[:history] ? 'Y' : 'N' )
              end
            end
          end
        end
      end

      def get_pay_period(options)
        requires!(options, [:periodicity, :bimonthly, :monthly, :biweekly, :weekly, :yearly, :daily, :semimonthly, :quadweekly, :quarterly, :semiyearly])
        case options[:periodicity]
          when :weekly then 'Weekly'
          when :biweekly then 'Bi-weekly'
          when :semimonthly then 'Semi-monthly'
          when :quadweekly then 'Every four weeks'
          when :monthly then 'Monthly'
          when :quarterly then 'Quarterly'
          when :semiyearly then 'Semi-yearly'
          when :yearly then 'Yearly'
        end
      end

      def format_rp_date(time)
        case time
          when Time, Date then time.strftime("%m%d%Y")
        else
          time.to_s
        end
      end


'''

TRANSACTIONS = dict(
        purchase       = 'Sale',
        authorization  = 'Authorization',
        capture        = 'Capture',
        void           = 'Void',
        credit         = 'Credit'
      )
