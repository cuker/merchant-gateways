# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest

from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.billing.gateways.gateway import Gateway
from money import Money
from mock import patch

class GatewayTestCase(unittest.TestCase):
    def run(self, *args, **kwargs):
        if type(self) == GatewayTestCase: #abstract test case
            return
        return super(GatewayTestCase, self).run(*args, **kwargs)

    def _skip(self, message):
        if hasattr(unittest, 'SkipTest'):
            raise unittest.SkipTest(message)
        print message

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
    
    def get_dummy_billing_address(self):
        return {'phone':'(555) 555-5555',
                'email':'z@z.com',
                'name':'John Smith',
                'address1':'420 South Cedros',
                'city':'Solona Beach',
                'state':'CA',
                'country':'US',
                'zip':'90210',}
    
    def get_dummy_shipping_address(self):
        return {'phone':'(555) 555-5555',
                'email':'z@z.com',
                'name':'John Smith',
                'address1':'420 South Cedros',
                'city':'Solona Beach',
                'state':'CA',
                'country':'US',
                'zip':'90210',}

    def test_successful_card_store(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('card_store'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'card_store'))
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        address = self.get_dummy_billing_address()
        ship_address = self.get_dummy_shipping_address()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.card_store(credit_card, address=address, ship_address=ship_address, ip_address='127.0.0.1')
        self.assertTrue(response.card_store_id)
        self.assertTrue(response.success)
    
    def test_successful_authorize(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('authorize'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'authorize'))
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        address = self.get_dummy_billing_address()
        ship_address = self.get_dummy_shipping_address()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card, address=address, ship_address=ship_address, ip_address='127.0.0.1')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_capture(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('capture'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'capture'))
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.capture(Money(100, 'USD'), 'transaction_ref')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_authorize_with_card_store(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('authorize') or not gateway.CARD_STORE:
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'authorize with card store'))
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_purchase(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('purchase'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'purchase'))
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        address = self.get_dummy_billing_address()
        ship_address = self.get_dummy_shipping_address()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card, address=address, ship_address=ship_address)
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_purchase_with_card_store(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('purchase') or not gateway.CARD_STORE:
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'pruchase with card store'))
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.purchase(Money(100, 'USD'), credit_card=None, card_store_id='12345')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_void(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('void'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'void'))
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.void('999999999')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)
    
    def test_successful_credit(self):
        gateway = self.get_gateway()
        if not gateway.supports_action('credit'):
            return self._skip('%s does not support %s, skipping test' % (type(gateway), 'credit'))
        mock_server = self.get_success_mock()
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.credit(Money(100, 'USD'), '999999999')
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)

