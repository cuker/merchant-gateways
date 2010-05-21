# -*- coding: utf-8 -*-


from gateway import Gateway, default_dict, xStr


from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money
import sys
sys.path.insert(0, '/home/phlip/tools/braintree-2.2.1')
import braintree
from braintree import Transaction, Environment

TEST_URI = 'sandbox.braintreegateway.com'

# TODO  what's with the cert? Environment.Sandbox = Environment("sandbox.braintreegateway.com", "443", True, Environment.braintree_root() + "/ssl/sandbox_braintreegateway_com.ca.crt")

#  TODO  clone the Bogus active_gateway module! (tip: configure its auto-responses to match Braintrees?;)

LIVE_URI = 'secure.braintreepaymentgateway.com'

class BraintreeGateway(Gateway):  # CONSIDER most of this belongs in a class SmartPs, which is Braintree's actual implementation

    class Response(response.Response):
        pass

    def authorize(self, money, credit_card, **options):  #  TODO  self.amount -> self.money

        self.result = Transaction.sale({
                "amount": "100",
                "credit_card": {
                    "number": "5105105105105101",
                    "expiration_date": "05/2012"
                } #,
    #            "options": {
     #               "submit_for_settlement": True TODO  turn this on for sale (purchase) off for authorize
               # }
            })
        #print dir(self.result.transaction)
        self.response = self.__class__.Response(self.result.is_success, self.result.transaction.processor_response_text, 'TODO 3',
                                                is_test = self.gateway_mode =='test',
                                                authorization = self.result.transaction.processor_authorization_code
                                                )
        self.response.result = self.result
        return self.response


#  TODO  trust nothing below this line
#  TODO  trust nothing below this line
#  TODO  trust nothing below this line
#  TODO  trust nothing below this line
#  TODO  trust nothing below THIS line!


    def add_address(self, post, prefix, **address):
#      def add_address(post, address,prefix="")
        if prefix:  prefix += "_"
#        unless address.blank? or address.values.blank? TODO
        post[prefix+"address1"]   = address.get('address1', '')
        post[prefix+"address2"]   = address.get('address2', '')
        post[prefix+"company"]    = address.get('company', '')
        post[prefix+"phone"]      = address.get('phone', '')
        post[prefix+"zip"]        = address.get('zip', '')
        post[prefix+"city"]       = address.get('city', '')
        post[prefix+"state"]      = address.get('state', 'n/a') or 'n/a'
        post[prefix+"country"]    = address.get('country', '') # TODO .to_s? safe unicode??

#    def authorize(self, money, credit_card, **options):
#        post = {}
#        self.add_invoice(post, **options)
#        self.add_payment_source(post, credit_card, **options)
#        self.add_address(post, '', **options.get('billing_address', options.get('address', {})))  #  TODO  TDD all that nonsense!
#        self.add_address(post, "shipping", **options.get('shipping_address', {}))  #  TODO  require the addresses?
#        self.add_customer_data(post, **options)
#        self.add_currency(post, money) # TODO, **options)
#        # TODO self.add_processor(post, **options)
#        return self.commit('auth', money, post)  #  TODO  rely on this return nowhere

    def commit(self, action, money, parameters):  #  TODO  is it post or parameters?
        if money:  parameters['amount'] = money.amount
        data         = self.post_data(action, **parameters)
        string       = self.post_webservice(self.api_url(), data)
        self.result  = self.parse( string )
        self.success = self.result['response'] == '1'
        self.message = self.message_from()

        r = self.__class__.Response( self.success, self.message, self.result,
                                     is_test=self.is_test )

#        Response.new(response["response"] == "1", message_from(response), response,
#          :authorization => response["transactionid"],
#          :test => test?,
#          :cvv_result => response["cvvresponse"],
#          :avs_result => { :code => response["avsresponse"] }
#        )
       # TODO assert r == self.response
        self.response = r
        return r

    def commit_TODO_deprecate_me(self, request, **options):
        # request       = self.build_request(request, **options)
        self.result   = self.parse(self.post_webservice(url, request))  #  CONSIDER  no version of post_webservice needs options
        self.success  = self.result['ApprovalStatus'] == '1'
        self.message  = self.result['StatusMsg']
        authorization = self.result['TxRefNum']
        avs_resp_code = self.result.get('AVSRespCode', '') or ''

        r = self.__class__.Response( self.success, self.message, self.result,
                                     is_test=self.is_test,
                                     authorization=authorization,
                                     avs_result=avs_resp_code.strip(),
                                     cvv_result=self.result['CVV2RespCode']  #  CONSIDER  what about the 2?
                                    )
        r.result = self.result  #  TODO  use params for something else
        return r

    def message_from(self):  #  TODO  better name
        if self.result["responsetext"] in ("SUCCESS", "Approved", None): # This is dubious, but responses from UPDATE are nil.
            return "This transaction has been approved"  #  TODO  test this
        elif self.result['responsetext'] == "DECLINE":
            return "This transaction has been declined"  #  TODO  test this

#  TODO  if I move all a package's includes into its __init__.py, does everyone see them automatically?

        return self.result["responsetext"]

    def api_url(self):  #  TODO  api_uri !!!
        uri = self.is_test and TEST_URI or LIVE_URI
        return 'https://%s/transactions' % uri
        # return 'https://%s/api/transact.php' % uri

    def post_data(self, action, **parameters):

        post = dict( username=self.options['login'],
                     password=self.options['password'],
                     type=action ) # TODO if action

        post.update(parameters)
        from urllib import urlencode  #  TODO use me more

        return urlencode(post)

    def add_invoice(self, post, **options):
        post['orderid'] = str(options.get('order_id', '')) # TODO .to_s.gsub(/[^\w.]/, '')

    def add_payment_source(self, params, source, **options):  #  TODO  rename params to post
# TODO        case determine_funding_source(source)
#        when :vault       then add_customer_vault_id(params, source)
#        when :credit_card then
        self.add_credit_card(params, source, **options)
#        when :check       then add_check(params, source, options)
#        end
#      end

    def add_credit_card(self, post, credit_card, **options):
#        if options[:store]  #  TODO
#          post[:customer_vault] = "add_customer"
#          post[:customer_vault_id] = options[:store] unless options[:store] == true
#        end
        post.update(ccnumber=credit_card.number)
#        post[:cvv] = creditcard.verification_value if creditcard.verification_value?
#        post[:ccexp]  = expdate(creditcard)  #  TODO
#        post[:firstname] = creditcard.first_name
#        post[:lastname]  = creditcard.last_name
#      end

    def expdate(self, credit_card):
        return '%02i%s' % (credit_card.month, str(credit_card.year)[-2:])

    def add_customer_data(self, post, **options):
        email = options.get('email', None)
        if email:  post['email'] = email
        ip = options.get('ip', None)
        if ip:  post['ipaddress'] = ip

    def add_currency(self, post, money):
        post['currency'] = str(money.currency)
            # TODO post[:currency] = options[:currency] || currency(money)

#      def add_processor(post, options)  #  TODO  find anyone who gives a darn about this!
#        post[:processor] = options[:processor] unless options[:processor].nil?
#      end

    def parse(self, urlencoded):
        import cgi
        qsparams = cgi.parse_qs(urlencoded)

        for k,v in qsparams.items():  #  TODO  have we seen this before..?
            if len(v) == 1:
                qsparams[k] = v[0] # easier to manipulate, because most real-life params are singular

        return qsparams


#  TODO  trust nothing below this comment

    def purchase(self, money, credit_card, **options):
        '''Purchase is an auth followed by a capture
           You must supply an order_id in the options hash'''

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        self.options = self.setup_address_hash(**self.options)
        message = self.build_purchase_request(money, credit_card, **self.options)
        return self.commit(message, **self.options)

    def build_authorization_request_TODO(self, money, credit_card, **options):  #  where'd "NewOrder" come from? not in docs...

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'

        fields = default_dict(**self.options)

#                            country='USA',  #  TODO vet this default

        grandTotalAmount = '%.2f' % money.amount  #  CONSIDER  format AMOUNT like this better, everywhere
        fields.update(options['billing_address'])  #  TODO  what about address?
        fields.update(options)

        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:] #  CONSIDER  credit_card_format
        x = XML

        from money.Money import CURRENCY
        numeric = CURRENCY[str(money.currency)].numeric  #  TODO  this should be an accessor

        new_order = x.NewOrder(
                        x.OrbitalConnectionUsername(fields['login']),  #  TODO  from configs
                        x.OrbitalConnectionPassword(fields['password']),  #  TODO  ibid
                        x.IndustryType('EC'),  #  'EC'ommerce - a web buy
                        x.MessageType('A'),  #  auth fwt!
                            # TODO  hallow A – Authorization request AC – Authorization and Mark for Capture FC – Force-Capture request R – Refund request
                        x.BIN('1'),
                        x.MerchantID('1'),
                        x.TerminalID('1'),
                        x.CardBrand(''),

# TODO SW – Switch / Solo ED – European Direct Debit EC – Electronic Check BL – Bill Me Later DP – PINLess Debit [Generic Value Used in Requests]

                        x.AccountNum(credit_card.number),
                        x.Exp(exp_code),
                        x.CurrencyCode(numeric),
                        x.CurrencyExponent('2'),  #  TODO  figure out what this is it's probably important
                        x.CardSecValInd('1'),  #  CONSIDER  visa & discover only - nullify for others
                        x.CardSecVal(credit_card.verification_value),
                        x.AVSzip(fields['zip']),
                        x.AVSaddress1(fields['address1']),  #  TODO  pull an AVSresponse?
                        x.AVSaddress2(fields['address2']),
                        x.AVScity(fields['city']),
                        x.AVSstate(fields['state']),
                        x.AVSphoneNum(fields['phone']),
                        x.AVSname(credit_card.first_name + ' ' + credit_card.last_name),
                        x.AVScountryCode('840'), #  CONSIDER  other countries
                        x.CustomerProfileFromOrderInd('A'),
                        x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID(''),  #  TODO
                        x.Amount(grandTotalAmount)
                        )
        return xStr(XML.Request(new_order))

#                        XML.email(fields['email']),
#                      XML.expirationMonth(str(credit_card.month)),
#                      XML.expirationYear(str(credit_card.year)),
#                      XML.cardType('001')  #  TODO

# TODO  question fields in Cybersource        (template_p % fields) )

    def soap_keys(self):  #   CONSIDER  better name coz it's not always about the SOAP
        return ( 'AccountNum',                'MerchantID',
                 'ApprovalStatus',            'MessageType',
                 'AuthCode',                  'OrderID',
                 'AVSRespCode',               'ProcStatus',
                 'CardBrand',                 'ProfileProcStatus',
                 'CAVVRespCode',              'RecurringAdviceCd',
                 'CustomerName',              'RespCode',
                 'CustomerProfileMessage',    'RespMsg',
                 'CustomerRefNum',            'RespTime',
                 'CVV2RespCode',              'StatusMsg',
                 'HostAVSRespCode',           'TerminalID',
                 'HostCVV2RespCode',          'TxRefIdx',
                 'HostRespCode',              'TxRefNum',
                 'IndustryType', )

    def build_authorization_request(self, money, credit_card, **options):
        from money.Money import CURRENCY
        numeric = CURRENCY[str(money.currency)].numeric  #  TODO  this should be an accessor
        return xStr(
          XML.Request(
              XML.AC(
                XML.CommonData(
                  XML.CommonMandatory(
                    XML.AccountNum('4012888888881', AccountTypeInd='91'),
                    XML.POSDetails(POSEntryMode='01'),
                    XML.MerchantID('123456789012'),
                    XML.TerminalID('001',
                                   TermEntCapInd='05',
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
                    XML.Currency(CurrencyCode=numeric,
                                 CurrencyExponent='2'),
                    XML.CardPresence(
                      XML.CardNP(
                        XML.Exp('1205'))),
                    XML.TxDateTime(),
                        AuthOverrideInd='N',
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

    def build_purchase_request(self, money, creditcard, **options):

        XML = ElementMaker(
        #        namespace="http://my.de/fault/namespace",
         #        nsmap=dict(s="http://schemas.xmlsoap.org/soap/envelope/",
          #              wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
           #            )
        )

        my_doc = XML.Body(XML.billTo)
        #print(etree.tostring(my_doc, pretty_print=True))

CREDIT_CARD_CODES = dict( v='001',  #  TODO  convert to Orbital
                          m='002', # TODO  verify
                          a='003',  # TODO  verify
                          d='004' )  # TODO  verify

#  TODO  trust everything below this line

#require File.join(File.dirname(__FILE__),'smart_ps.rb')
#module ActiveMerchant #:nodoc:
#  module Billing #:nodoc:
#    class BraintreeGateway < SmartPs
#
#      self.supported_countries = ['US']
#      self.supported_cardtypes = [:visa, :master, :american_express, :discover]
#      self.homepage_url = 'http://www.braintreepaymentsolutions.com'
#      self.display_name = 'Braintree'
#      self.default_currency = 'USD'
#    end
#  end
#end

#require File.join(File.dirname(__FILE__), '..', 'check.rb')
#
#module ActiveMerchant #:nodoc:
#  module Billing #:nodoc:
#    class SmartPs < Gateway #:nodoc:
#
#      ##
#      # This is the base gateway for processors who use the smartPS processing system
#
#      def initialize(options = {})
#        requires!(options, :login, :password)
#        @options = options
#        super
#      end
#
#      # Pass :store => true in the options to store the
#      # payment info at the gateway and get a generated
#      # customer_vault_id in the response.
#      # Pass :store => some_number_or_string to specify the
#      # customer_vault_id the gateway should use (make sure it's
#      # unique).
#      def purchase(money, payment_source, options = {})
#        post = {}
#        add_invoice(post, options)
#        add_payment_source(post, payment_source, options)
#        add_address(post, options[:billing_address] || options[:address])
#        add_address(post, options[:shipping_address], "shipping")
#        add_customer_data(post, options)
#        add_currency(post, money, options)
#        add_processor(post, options)
#        commit('sale', money, post)
#      end
#
#      def capture(money, authorization, options = {})
#        post ={}
#        post[:transactionid] = authorization
#        commit('capture', money, post)
#      end
#
#      def void(authorization, options = {})
#        post ={}
#        post[:transactionid] = authorization
#        commit('void', nil, post)
#      end
#
#      def credit(money, payment_source, options = {})
#        post = {}
#        add_invoice(post, options)
#        add_payment_source(post, payment_source, options)
#        add_address(post, options[:billing_address] || options[:address])
#        add_customer_data(post, options)
#        add_sku(post,options)
#        add_currency(post, money, options)
#        add_processor(post, options)
#        commit('credit', money, post)
#      end
#
#      def refund(auth, options = {})
#        post = {}
#        add_transaction(post, auth)
#        commit('refund', options.delete(:amount), post)
#      end
#
#
#      # Update the values (such as CC expiration) stored at
#      # the gateway.  The CC number must be supplied in the
#      # CreditCard object.
#      def update(vault_id, creditcard, options = {})
#        post = {}
#        post[:customer_vault] = "update_customer"
#        add_customer_vault_id(post, vault_id)
#        add_creditcard(post, creditcard, options)
#        add_address(post, options[:billing_address] || options[:address])
#        add_customer_data(post, options)
#
#        commit(nil, nil, post)
#      end
#
#      # Amend an existing transaction
#      def amend(auth, options = {})
#        post = {}
#        add_invoice(post, options)
#        add_transaction(post, auth)
#        commit('update', nil, post)
#      end
#
#
#      def delete(vault_id)
#        post = {}
#        post[:customer_vault] = "delete_customer"
#        add_customer_vault_id(post, vault_id)
#        commit(nil, nil, post)
#      end
#
#      # To match the other stored-value gateways, like TrustCommerce,
#      # store and unstore need to be defined
#      def store(payment_source, options = {})
#        post = {}
#        billing_id = options.delete(:billing_id).to_s || true
#        add_payment_source(post, payment_source, :store => billing_id)
#        add_address(post, options[:billing_address] || options[:address])
#        add_customer_data(post, options)
#        commit(nil, nil, post)
#      end
#
#      alias_method :unstore, :delete
#
#      private
#      def add_customer_data(post, options)
#        if options.has_key? :email
#          post[:email] = options[:email]
#        end
#
#        if options.has_key? :ip
#          post[:ipaddress] = options[:ip]
#        end
#      end
#
#      def add_address(post, address,prefix="")
#        prefix +="_" unless prefix.blank?
#        unless address.blank? or address.values.blank?
#          post[prefix+"address1"]    = address[:address1].to_s
#          post[prefix+"address2"]    = address[:address2].to_s unless address[:address2].blank?
#          post[prefix+"company"]    = address[:company].to_s
#          post[prefix+"phone"]      = address[:phone].to_s
#          post[prefix+"zip"]        = address[:zip].to_s
#          post[prefix+"city"]       = address[:city].to_s
#          post[prefix+"country"]    = address[:country].to_s
#          post[prefix+"state"]      = address[:state].blank?  ? 'n/a' : address[:state]
#        end
#      end
#
#      def add_invoice(post, options)
#        post[:orderid] = options[:order_id].to_s.gsub(/[^\w.]/, '')
#      end
#
#      def add_payment_source(params, source, options={})
#        case determine_funding_source(source)
#        when :vault       then add_customer_vault_id(params, source)
#        when :credit_card then add_creditcard(params, source, options)
#        when :check       then add_check(params, source, options)
#        end
#      end
#
#      def add_customer_vault_id(params, vault_id)
#        params[:customer_vault_id] = vault_id
#      end
#
#      def add_creditcard(post, creditcard, options)
#        if options[:store]
#          post[:customer_vault] = "add_customer"
#          post[:customer_vault_id] = options[:store] unless options[:store] == true
#        end
#        post[:ccnumber]  = creditcard.number
#        post[:cvv] = creditcard.verification_value if creditcard.verification_value?
#        post[:ccexp]  = expdate(creditcard)
#        post[:firstname] = creditcard.first_name
#        post[:lastname]  = creditcard.last_name
#      end
#
#      def add_check(post, check, options)
#        if options[:store]
#          post[:customer_vault] = "add_customer"
#          post[:customer_vault_id] = options[:store] unless options[:store] == true
#        end
#
#        post[:payment] = 'check' # Set transaction to ACH
#        post[:checkname] = check.name # The name on the customer's Checking Account
#        post[:checkaba] = check.routing_number # The customer's bank routing number
#        post[:checkaccount] = check.account_number # The customer's account number
#        post[:account_holder_type] = check.account_holder_type # The customer's type of ACH account
#        post[:account_type] = check.account_type # The customer's type of ACH account
#      end
#
#      def add_sku(post,options)
#        post["product_sku_#"] = options[:sku] || options["product_sku_#"]
#      end
#
#      def add_transaction(post, auth)
#        post[:transactionid] = auth
#      end
#
#      def expdate(creditcard)
#        year  = sprintf("%.04i", creditcard.year.to_i)
#        month = sprintf("%.02i", creditcard.month.to_i)
#
#        "#{month}#{year[-2..-1]}"
#      end
#
#      def determine_funding_source(source)
#        case
#        when source.is_a?(String) then :vault
#        when CreditCard.card_companies.keys.include?(card_brand(source)) then :credit_card
#        when card_brand(source) == 'check' then :check
#        else raise ArgumentError, "Unsupported funding source provided"
#        end
#      end
#    end
#  end
#end
#
