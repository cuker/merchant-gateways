# -*- coding: utf-8 -*-
import unittest

from merchant_gateways.billing.gateways.braintree_orange import BraintreeOrange
from merchant_gateways.tests.test_helper import MerchantGatewaysTestSuite
from merchant_gateways.tests.billing.gateways.braintree_orange_suite import MerchantGatewaysBraintreeOrangeSuite, BrainTreeOrangeMockServer
from merchant_gateways.billing.credit_card import CreditCard
from pprint import pprint
from money import Money
import os
import sys
from mock import Mock, patch

class BraintreeOrangeTests(unittest.TestCase):

    def get_gateway(self):
        return BraintreeOrange(**{'login':'username',
                                  'password':'password'})

    def get_success_mock(self):
        return Mock(side_effect=BrainTreeOrangeMockServer())

    def get_dummy_credit_card(self):
        return CreditCard(number='4111111111111111',
                          month='10',
                          year='2020',
                          card_type='V',
                          verification_value='111',
                          first_name='John',
                          last_name='Smith')

    def test_successful_card_store(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.card_store(credit_card)
        self.assertTrue(response.card_store_id)
        self.assertTrue(response.success)
    
    def test_successful_authorize(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card)
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
    def test_successful_authorize_with_card_store(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
    def test_successful_purchase(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card)
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
    def test_successful_purchase_with_card_store(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
    def test_successful_void(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.void('999999999')
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
    def test_successful_credit(self):
        gateway = self.get_gateway()
        mock_server = self.get_success_mock()
        with patch.object(BraintreeOrange, 'post_webservice', mock_server) as mock_do:
            response = gateway.credit(Money(100, 'USD'), '999999999')
        self.assertTrue(response.transaction)
        self.assertTrue(response.success)
    
