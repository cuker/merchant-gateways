# -*- coding: utf-8 -*-

from merchant_gateways.billing.gateways.braintree_orange import BraintreeOrange
from merchant_gateways.billing.gateways.gateway import xStr
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from merchant_gateways.tests.billing.gateways.braintree_orange_suite import MerchantGatewaysBraintreeOrangeSuite
from pprint import pprint
from money import Money
import os
import sys

#  TODO  teh test batch should hit the local package _before_ the globally installed one


class BraintreeOrangeTests( MerchantGatewaysBraintreeOrangeSuite, MerchantGatewaysTestSuite,
                              MerchantGatewaysTestSuite.CommonTests ):

    def gateway_type(self):
        return BraintreeOrange

    def test_successful_authorization(self):  'TODO'
    def test_failed_authorization(self):  'TODO'

    # def test_successful_purchase(self):  'TODO'

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
        self.assert_equal('123456',   self.response.authorization)  #  TODO  self.response.transaction_id in braintree_blue.rb !
        self.assert_equal('SUCCESS',  self.response.message)
        self.assert_equal('sale',     self.response.result['type'])

    def test_build_authorization_request_with_alternative_money(self):
        return # TODO
        Nuevo_Sol = 'PEN'  #  TODO  switch to a different token minority's tokens!
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

ruby_sample = '''
require 'test_helper'

class BraintreeOrangeTest < Test::Unit::TestCase

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
'''
