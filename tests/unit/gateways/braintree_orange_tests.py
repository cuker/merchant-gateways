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

    def _test_remote_successful_authorization(self):
        '''All gateways authorize with these inputs and outputs'''

        self.options['description'] = 'Chamber of Secrets'
        self.gateway.options['login'] = 'PhlipTest'  #  TODO  or username
        self.gateway.options['password'] = ''
        self.credit_card.number = '4111111111111111'
        self.gateway.authorize(self.money, self.credit_card, **self.options)  #  TODO  the options can also transport the username & password
        self.response = self.gateway.response

    def assert_successful_authorization(self):
        self.assert_equal('123456',     self.response.authorization)
        self.assert_equal('1274650052', self.response.result['transactionid'])
        self.assert_equal('SUCCESS',    self.response.message)

    def test_successful_capture(self):
        '''TODO All gateways authorize with these inputs and outputs'''

        self.options['description'] = 'Hogwarts Express'

        self.mock_webservice(self.successful_capture_response(),
            lambda: self.gateway.capture(self.money, '1234', **self.options) )

        self.response = self.gateway.response
        assert self.response.is_test
        self.assert_success()
        self.assert_successful_capture()

    def test_failed_capture(self):
        self.mock_webservice( self.failed_capture_response(),
            lambda:  self.gateway.capture(self.money, '1234', **self.options) )

        self.response = self.gateway.response
        assert self.response.is_test
        self.assert_failure()
        self.assert_failed_capture()

    def assert_successful_capture(self):
        self.assert_equal('123456',     self.response.authorization)
        self.assert_equal('1274650052', self.response.result['transactionid'])
        self.assert_equal('SUCCESS',    self.response.message)

    def successful_authorization_response(self):
        return "response=1&responsetext=SUCCESS&authcode=123456&transactionid=1274650052&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=100"

    def failed_authorization_response(self):
        return "response=2&responsetext=DECLINE&authcode=&transactionid=1274647575&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=200"

    def successful_capture_response(self):
        #  TODO  get real samples
        return "response=1&responsetext=SUCCESS&authcode=123456&transactionid=1274650052&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=100"

    def failed_capture_response(self):
        #  TODO  get real samples
        return "response=2&responsetext=DECLINE&authcode=&transactionid=1274647575&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=200"

    def assert_failed_capture(self):
        self.assert_equal('', self.response.authorization)
        self.assert_equal('1274647575', self.response.result['transactionid'])

    def assert_failed_authorization(self):
        self.assert_equal('', self.response.authorization)
        self.assert_equal('1274647575', self.response.result['transactionid'])
        self.assert_equal('1274647575', self.response.transaction)
        self.assert_equal('DECLINE',    self.response.message)
        self.assert_none(self.response.fraud_review)
        self.assert_empty(self.response.authorization)  #  TODO promulgate meaning of "empty"

    def assert_successful_purchase(self):
        self.assert_equal(BraintreeOrange.TEST_URI, self.call_args[0])
        params = self.call_args[1]
        assert 'X' == self.gateway.options['login']  #  CONSIDER  less unimaginative name and password!
        assert 'Y' == self.gateway.options['password']
        self.assert_equal('X',      params['username'])
        self.assert_equal('Y',      params['password'])
        self.assert_equal('sale',   params['type'])
        self.assert_equal('100.00', params['amount'])
        self.assert_equal('USD',    params['currency'])
        self.assert_equal('4242424242424242', params['ccnumber'])
        self.assert_equal('1290',   params['ccexp'])
        self.assert_equal('456',    params['cvv'])
        self.assert_equal('Hermione', params['firstname'])
        self.assert_equal('Granger', params['lastname'])
        self.assert_equal(str(self.options['order_id']), params['orderid'])

        #  TODO  check that it actually goes over the wire urlencoded

        self.assert_equal('123456',   self.response.authorization)  #  TODO  self.response.transaction_id in braintree_blue.rb !
        self.assert_equal('SUCCESS',  self.response.message)
        self.assert_equal('sale',     self.response.result['type'])
        borrowed_example = "type=sale&firstname=Longbob&lastname=Longsen&cvv=123&username=LOGIN&amount=1.00&ccnumber=4242424242424242&currency=USD&orderid=&ccexp=0911&password=PASSWORD"

        keys = [ x.split('=')[0] for x in borrowed_example.split('&') ]
        keys.sort()
        for key in keys:  self.assert_contains(key, params.keys())

    def test_build_authorization_request_with_alternative_money(self):

        Yemeni_rial = 'YER'

        self.money = Money('200.00', Yemeni_rial)
        request = {}
        self.gateway._add_currency(self.money, request)
        self.assert_equal('200.00', request['amount'])
        self.assert_equal('YER', request['currency'])



ruby_sample = '''

    @options = { :billing_address => address }

  def test_successful_purchase
    @gateway.expects(:ssl_post).returns(successful_purchase_response)

    assert response = @gateway.authorize(@amount, @credit_card, @options)
    assert_instance_of Response, response
    assert_success response
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
