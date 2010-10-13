# -*- coding: utf-8 -*-
import unittest

from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.billing.gateways.gateway import Gateway
from money import Money
from mock import patch

class GatewayTestCase(unittest.TestCase):

    def get_gateway(self):
        """
        Return an instantiated gateway
        """
        return Gateway()

    def get_success_mock(self):
        """
        Return a mock object
        """
        raise NotImplementedError

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
        if not gateway.supports_action('card_store'):
            return
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.card_store(credit_card)
        self.assertTrue(response.card_store_id)
        self.assertTrue(response.success)
    
    def test_successful_authorize(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('authorize'):
            return
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card)
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_capture(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('capture'):
            return
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.capture(Money(100, 'USD'), 'transaction_ref')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_authorize_with_card_store(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('authorize') or not gateway.CARD_STORE:
            return
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_purchase(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('purchase'):
            return
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card)
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_purchase_with_card_store(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('purchase') or not gateway.CARD_STORE:
            return
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_void(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('void'):
            return
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.void('999999999')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_credit(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('credit'):
            return
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.credit(Money(100, 'USD'), '999999999')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)

