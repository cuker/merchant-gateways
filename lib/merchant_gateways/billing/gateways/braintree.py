# -*- coding: utf-8 -*-

from gateway import Gateway, default_dict, xStr
from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money

#  TODO  trust nothing below this line

TEST_URL = 'https://orbitalvar1.paymentech.net/authorize'
LIVE_URL = 'https://orbital1.paymentech.net/authorize'

class Braintree(Gateway):

    def authorize(self, money, creditcard, **options):
        '''
        Request an authorization for an amount from CyberSource

        You must supply an :order_id in the options hash  TODO  complain if it ain't there
        '''

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        self.options.update(options)

        message = self.build_authorization_request(money, creditcard, **self.options)  #  TODO  _authorization_request, everywhere!!
        return self.commit(message, **self.options)

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

    def parse(self, soap):
        result = {}
        keys  = self.soap_keys()
        doc  = etree.XML(soap)

        for key in keys:
            nodes = doc.xpath('//' + key)
            result[key] = len(nodes) and nodes[0].text or None

        return result

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

    class Response(response.Response):
        pass

    def commit(self, request, **options):
        url           = self.is_test and TEST_URL or LIVE_URL
        self.request  = request  # CONSIDER  standardize this
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
#      def api_url
#        'https://secure.braintreepaymentgateway.com/api/transact.php'
#      end
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
#      def authorize(money, creditcard, options = {})
#        post = {}
#        add_invoice(post, options)
#        add_payment_source(post, creditcard,options)
#        add_address(post, options[:billing_address] || options[:address])
#        add_address(post, options[:shipping_address], "shipping")
#        add_customer_data(post, options)
#        add_currency(post, money, options)
#        add_processor(post, options)
#        commit('auth', money, post)
#      end
#
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
#      def add_currency(post, money, options)
#        post[:currency] = options[:currency] || currency(money)
#      end
#
#      def add_processor(post, options)
#        post[:processor] = options[:processor] unless options[:processor].nil?
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
#      def parse(body)
#        results = {}
#        body.split(/&/).each do |pair|
#          key,val = pair.split(/=/)
#          results[key] = val
#        end
#
#        results
#      end
#
#      def commit(action, money, parameters)
#        parameters[:amount]  = amount(money) if money
#        response = parse( ssl_post(api_url, post_data(action,parameters)) )
#        Response.new(response["response"] == "1", message_from(response), response,
#          :authorization => response["transactionid"],
#          :test => test?,
#          :cvv_result => response["cvvresponse"],
#          :avs_result => { :code => response["avsresponse"] }
#        )
#
#      end
#
#      def expdate(creditcard)
#        year  = sprintf("%.04i", creditcard.year.to_i)
#        month = sprintf("%.02i", creditcard.month.to_i)
#
#        "#{month}#{year[-2..-1]}"
#      end
#
#
#      def message_from(response)
#        case response["responsetext"]
#        when "SUCCESS", "Approved", nil # This is dubious, but responses from UPDATE are nil.
#          "This transaction has been approved"
#        when "DECLINE"
#          "This transaction has been declined"
#        else
#          response["responsetext"]
#        end
#      end
#
#      def post_data(action, parameters = {})
#        post = {}
#        post[:username]      = @options[:login]
#        post[:password]   = @options[:password]
#        post[:type]       = action if action
#
#        request = post.merge(parameters).map {|key,value| "#{key}=#{CGI.escape(value.to_s)}"}.join("&")
#        request
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
