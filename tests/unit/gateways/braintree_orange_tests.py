# -*- coding: utf-8 -*-

from merchant_gateways.billing.gateways.braintree_orange import BraintreeOrange
from merchant_gateways.tests.test_helper import MerchantGatewaysTestSuite
from merchant_gateways.tests.billing.gateways.braintree_orange_suite import MerchantGatewaysBraintreeOrangeSuite
from pprint import pprint
from money import Money
import os
import sys

#  CONSIDER  teh test batch should hit the local package _before_ the globally installed one


class BraintreeOrangeTests( MerchantGatewaysBraintreeOrangeSuite, MerchantGatewaysTestSuite,
                              MerchantGatewaysTestSuite.CommonTests ):

    def gateway_type(self):
        return BraintreeOrange

    def test_successful_authorization(self):  'TODO'
    def test_failed_authorization(self):  'TODO'

    def assert_successful_authorization(self):
        return # TODO
        self.assert_equal('fbyrfg',   self.response.result.transaction.id)
        self.assert_equal('54173',    self.response.authorization)
        self.assert_equal('Approved', self.response.message)
        self.assert_equal('1000',     self.response.result.transaction.processor_response_code)

    def assert_failed_authorization(self):
        return # TODO
        self.assert_equal('kb3k4w', self.response.result.transaction.id)
        self.assert_none(self.response.fraud_review)
        self.assert_none(self.response.authorization)
        self.assert_equal('Unknown ()', self.response.message)  #  CONSIDER  what the heck is that??

    def assert_successful_purchase(self):
        self.assert_equal(BraintreeOrange.TEST_URI, self.call_args[0])
        print self.call_args[1]
        print self.credit_card.__dict__
        params = self.call_args[1]

        pprint(self.gateway.__dict__)
        assert 'X' == self.gateway.options['login']  #  CONSIDER  less unimaginative name and password!
        assert 'Y' == self.gateway.options['password']
        # post[:username]      = @options[:login]
        # post[:password]   = @options[:password]

        self.assert_equal('X', params['username'])
        self.assert_equal('Y', params['password'])

        self.assert_equal('4242424242424242', params['ccnumber'])
        self.assert_equal('1290', params['ccexp'])

#        username=demoapi&password=password1&ccnumber=4111111111111111&ccexp=1010&type=sale&amount=10.00

        #  TODO  check that it actually goes over the wire urlencoded

        self.assert_equal('123456',   self.response.authorization)  #  TODO  self.response.transaction_id in braintree_blue.rb !
        self.assert_equal('SUCCESS',  self.response.message)
        self.assert_equal('sale',     self.response.result['type'])

    def test_build_authorization_request_with_alternative_money(self):

        Yemeni_rial = 'YER'

        self.money = Money('200.00', Yemeni_rial)
        return
        billing_address = self.assemble_billing_address()
        message = self.gateway.build_authorization_request(self.money, self.credit_card, **self.options)
        return
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

ruby_sample = '''

  def setup
    @gateway = BraintreeOrangeGateway.new(
      :login => 'LOGIN',
      :password => 'PASSWORD'
    )

    @credit_card = credit_card
    @amount = 100

    @options = { :billing_address => address }
  end

  def test_successful_purchase
    @gateway.expects(:ssl_post).returns(successful_purchase_response)

    assert response = @gateway.authorize(@amount, @credit_card, @options)
    assert_instance_of Response, response
    assert_success response
    assert_equal '510695343', response.authorization
  end

  def test_failed_purchase
    @gateway.expects(:ssl_post).returns(failed_purchase_response)

    assert response = @gateway.authorize(@amount, @credit_card, @options)
    assert_instance_of Response, response
    assert_failure response
  end

  def test_add_address
    result = {}

    @gateway.send(:add_address, result,   {:address1 => '164 Waverley Street', :country => 'US', :state => 'CO'} )
    assert_equal ["address1", "city", "company", "country", "phone", "state", "zip"], result.stringify_keys.keys.sort
    assert_equal 'CO', result["state"]
    assert_equal '164 Waverley Street', result["address1"]
    assert_equal 'US', result["country"]
  end

  def test_add_shipping_address
    result = {}

    @gateway.send(:add_address, result,   {:address1 => '164 Waverley Street', :country => 'US', :state => 'CO'},"shipping" )
    assert_equal ["shipping_address1", "shipping_city", "shipping_company", "shipping_country", "shipping_phone", "shipping_state", "shipping_zip"], result.stringify_keys.keys.sort
    assert_equal 'CO', result["shipping_state"]
    assert_equal '164 Waverley Street', result["shipping_address1"]
    assert_equal 'US', result["shipping_country"]
  end

  def test_supported_countries
    assert_equal ['US'], BraintreeOrangeGateway.supported_countries
  end

  def test_supported_card_types
    assert_equal [:visa, :master, :american_express, :discover, :jcb], BraintreeOrangeGateway.supported_cardtypes
  end

  def test_adding_store_adds_vault_id_flag
    result = {}

    @gateway.send(:add_creditcard, result, @credit_card, :store => true)
    assert_equal ["ccexp", "ccnumber", "customer_vault", "cvv", "firstname", "lastname"], result.stringify_keys.keys.sort
    assert_equal 'add_customer', result[:customer_vault]
  end

  def test_blank_store_doesnt_add_vault_flag
    result = {}

    @gateway.send(:add_creditcard, result, @credit_card, {} )
    assert_equal ["ccexp", "ccnumber", "cvv", "firstname", "lastname"], result.stringify_keys.keys.sort
    assert_nil result[:customer_vault]
  end

  def test_accept_check
    post = {}
    check = Check.new(:name => 'Fred Bloggs',
                      :routing_number => '111000025',
                      :account_number => '123456789012',
                      :account_holder_type => 'personal',
                      :account_type => 'checking')
    @gateway.send(:add_check, post, check, {})
    assert_equal %w[account_holder_type account_type checkaba checkaccount checkname payment], post.stringify_keys.keys.sort
  end

  def test_funding_source
    assert_equal :check, @gateway.send(:determine_funding_source, Check.new)
    assert_equal :credit_card, @gateway.send(:determine_funding_source, @credit_card)
    assert_equal :vault, @gateway.send(:determine_funding_source, '12345')
  end

  def test_avs_result
    @gateway.expects(:ssl_post).returns(successful_purchase_response)

    response = @gateway.purchase(@amount, @credit_card)
    assert_equal 'N', response.avs_result['code']
  end

  def test_cvv_result
    @gateway.expects(:ssl_post).returns(successful_purchase_response)

    response = @gateway.purchase(@amount, @credit_card)
    assert_equal 'N', response.cvv_result['code']
  end

  private
  def successful_purchase_response
  end

  def failed_purchase_response
    'response=2&responsetext=DECLINE&authcode=&transactionid=510695919&avsresponse=N&cvvresponse=N&orderid=50357660b0b3ef16f72a3d3b83c46983&type=sale&response_code=200'
  end
end


require File.dirname(__FILE__) +  '/smart_ps.rb'
require File.dirname(__FILE__) + '/braintree/braintree_common'

module ActiveMerchant #:nodoc:
  module Billing #:nodoc:
    class BraintreeOrangeGateway < SmartPs
      include BraintreeCommon

      self.display_name = 'Braintree (Orange Platform)'  #  TODO  also do a display_name like this

      def api_url
        'https://secure.braintreepaymentgateway.com/api/transact.php'
      end
    end
  end
end

module BraintreeCommon
  def self.included(base)
    base.supported_countries = ['US']  #  TODO
    base.supported_cardtypes = [:visa, :master, :american_express, :discover, :jcb]  #  TODO
    base.homepage_url = 'http://www.braintreepaymentsolutions.com'
    base.display_name = 'Braintree'
    base.default_currency = 'USD'
  end
end

module ActiveMerchant #:nodoc:
  module Billing #:nodoc:
    class SmartPs < Gateway #:nodoc:

      ##
      # This is the base gateway for processors who use the smartPS processing system

      def initialize(options = {})
        requires!(options, :login, :password)
        @options = options
        super
      end

      # Pass :store => true in the options to store the
      # payment info at the gateway and get a generated
      # customer_vault_id in the response.
      # Pass :store => some_number_or_string to specify the
      # customer_vault_id the gateway should use (make sure it's
      # unique).
      def authorize(money, creditcard, options = {})
        post = {}
        add_invoice(post, options)
        add_payment_source(post, creditcard,options)
        add_address(post, options[:billing_address] || options[:address])
        add_address(post, options[:shipping_address], "shipping")
        add_customer_data(post, options)
        add_currency(post, money, options)
        add_processor(post, options)
        commit('auth', money, post)
      end

      def purchase(money, payment_source, options = {})
        post = {}
        add_invoice(post, options)
        add_payment_source(post, payment_source, options)
        add_address(post, options[:billing_address] || options[:address])
        add_address(post, options[:shipping_address], "shipping")
        add_customer_data(post, options)
        add_currency(post, money, options)
        add_processor(post, options)
        commit('sale', money, post)
      end

      def capture(money, authorization, options = {})
        post ={}
        post[:transactionid] = authorization
        commit('capture', money, post)
      end

      def void(authorization, options = {})
        post ={}
        post[:transactionid] = authorization
        commit('void', nil, post)
      end

      def credit(money, payment_source, options = {})
        post = {}
        add_invoice(post, options)
        add_payment_source(post, payment_source, options)
        add_address(post, options[:billing_address] || options[:address])
        add_customer_data(post, options)
        add_sku(post,options)
        add_currency(post, money, options)
        add_processor(post, options)
        commit('credit', money, post)
      end

      def refund(auth, options = {})
        post = {}
        add_transaction(post, auth)
        commit('refund', options.delete(:amount), post)
      end


      # Update the values (such as CC expiration) stored at
      # the gateway.  The CC number must be supplied in the
      # CreditCard object.
      def update(vault_id, creditcard, options = {})
        post = {}
        post[:customer_vault] = "update_customer"
        add_customer_vault_id(post, vault_id)
        add_creditcard(post, creditcard, options)
        add_address(post, options[:billing_address] || options[:address])
        add_customer_data(post, options)

        commit(nil, nil, post)
      end

      # Amend an existing transaction
      def amend(auth, options = {})
        post = {}
        add_invoice(post, options)
        add_transaction(post, auth)
        commit('update', nil, post)
      end


      def delete(vault_id)
        post = {}
        post[:customer_vault] = "delete_customer"
        add_customer_vault_id(post, vault_id)
        commit(nil, nil, post)
      end

      # To match the other stored-value gateways, like TrustCommerce,
      # store and unstore need to be defined
      def store(payment_source, options = {})
        post = {}
        billing_id = options.delete(:billing_id).to_s || true
        add_payment_source(post, payment_source, :store => billing_id)
        add_address(post, options[:billing_address] || options[:address])
        add_customer_data(post, options)
        commit(nil, nil, post)
      end

      alias_method :unstore, :delete

      private
      def add_customer_data(post, options)
        if options.has_key? :email
          post[:email] = options[:email]
        end

        if options.has_key? :ip
          post[:ipaddress] = options[:ip]
        end
      end

      def add_address(post, address,prefix="")
        prefix +="_" unless prefix.blank?
        unless address.blank? or address.values.blank?
          post[prefix+"address1"]    = address[:address1].to_s
          post[prefix+"address2"]    = address[:address2].to_s unless address[:address2].blank?
          post[prefix+"company"]    = address[:company].to_s
          post[prefix+"phone"]      = address[:phone].to_s
          post[prefix+"zip"]        = address[:zip].to_s
          post[prefix+"city"]       = address[:city].to_s
          post[prefix+"country"]    = address[:country].to_s
          post[prefix+"state"]      = address[:state].blank?  ? 'n/a' : address[:state]
        end
      end

      def add_currency(post, money, options)
        post[:currency] = options[:currency] || currency(money)
      end

      def add_processor(post, options)
        post[:processor] = options[:processor] unless options[:processor].nil?
      end

      def add_invoice(post, options)
        post[:orderid] = options[:order_id].to_s.gsub(/[^\w.]/, '')
      end

      def add_payment_source(params, source, options={})
        case determine_funding_source(source)
        when :vault       then add_customer_vault_id(params, source)
        when :credit_card then add_creditcard(params, source, options)
        when :check       then add_check(params, source, options)
        end
      end

      def add_customer_vault_id(params, vault_id)
        params[:customer_vault_id] = vault_id
      end

      def add_creditcard(post, creditcard, options)
        if options[:store]
          post[:customer_vault] = "add_customer"
          post[:customer_vault_id] = options[:store] unless options[:store] == true
        end
        post[:ccnumber]  = creditcard.number
        post[:cvv] = creditcard.verification_value if creditcard.verification_value?
        post[:ccexp]  = expdate(creditcard)
        post[:firstname] = creditcard.first_name
        post[:lastname]  = creditcard.last_name
      end

      def add_check(post, check, options)
        if options[:store]
          post[:customer_vault] = "add_customer"
          post[:customer_vault_id] = options[:store] unless options[:store] == true
        end

        post[:payment] = 'check' # Set transaction to ACH
        post[:checkname] = check.name # The name on the customer's Checking Account
        post[:checkaba] = check.routing_number # The customer's bank routing number
        post[:checkaccount] = check.account_number # The customer's account number
        post[:account_holder_type] = check.account_holder_type # The customer's type of ACH account
        post[:account_type] = check.account_type # The customer's type of ACH account
      end

      def add_sku(post,options)
        post["product_sku_#"] = options[:sku] || options["product_sku_#"]
      end

      def add_transaction(post, auth)
        post[:transactionid] = auth
      end

      def parse(body)
        results = {}
        body.split(/&/).each do |pair|
          key,val = pair.split(/=/)
          results[key] = val
        end

        results
      end

      def commit(action, money, parameters)
        parameters[:amount]  = amount(money) if money
        response = parse( ssl_post(api_url, post_data(action,parameters)) )
        Response.new(response["response"] == "1", message_from(response), response,
          :authorization => response["transactionid"],
          :test => test?,
          :cvv_result => response["cvvresponse"],
          :avs_result => { :code => response["avsresponse"] }
        )

      end

      def expdate(creditcard)
        year  = sprintf("%.04i", creditcard.year.to_i)
        month = sprintf("%.02i", creditcard.month.to_i)

        "#{month}#{year[-2..-1]}"
      end


      def message_from(response)
        case response["responsetext"]
        when "SUCCESS", "Approved", nil # This is dubious, but responses from UPDATE are nil.
          "This transaction has been approved"
        when "DECLINE"
          "This transaction has been declined"
        else
          response["responsetext"]
        end
      end

      def post_data(action, parameters = {})
        post = {}
        post[:username]      = @options[:login]
        post[:password]   = @options[:password]
        post[:type]       = action if action

        request = post.merge(parameters).map {|key,value| "#{key}=#{CGI.escape(value.to_s)}"}.join("&")
        request
      end

      def determine_funding_source(source)
        case
        when source.is_a?(String) then :vault
        when CreditCard.card_companies.keys.include?(card_brand(source)) then :credit_card
        when card_brand(source) == 'check' then :check
        else raise ArgumentError, "Unsupported funding source provided"
        end
      end
    end
  end
end



'''
