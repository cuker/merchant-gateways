# -*- coding: utf-8 -*-
from __future__ import with_statement
import datetime
import merchant_gateways


class MerchantGatewaysBraintreeOrangeSuite:

    def mock_gateway_webservice(self, returns, lamb, **assert_params):
        from mock import patch
        self.call_args = None

        with patch.object(merchant_gateways.billing.gateways.gateway.Gateway, 'post_webservice') as mock_do:
            mock_do.return_value = returns
            lamb()
            self.call_args = mock_do.call_args[0]

             # TODO https://secure.braintreepaymentgateway.com/api/transact.php

        try:
            self.response = getattr(self.gateway, 'response', {})  #  TODO  all web service mockers do all these things!
        except AttributeError:  pass

        params = self.call_args[1]

        for key, reference in assert_params.items():
            self.assert_equal(reference, params[key])

        return self.call_args  #  CONSIDER  all call_args should be self

    def successful_card_store_response(self):
        return 'response=1&responsetext=Customer Added&authcode=&transactionid=&avsresponse=&cvvresponse=&orderid=1&type=&response_code=100&customer_vault_id=463260156'

    def failed_card_store_response(self):
        return 'response=3&responsetext=Authentication Failed&authcode=&transactionid=&avsresponse=&cvvresponse=&orderid=1&type=&response_code=300'

    def successful_purchase_response(self):
        return 'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'

#    def successful_authorization_response(self):
#        return 'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'
#         # TODO get a real one!

    def successful_authorization_response(self):
        return "response=1&responsetext=SUCCESS&authcode=123456&transactionid=1274650052&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=100"

    def failed_authorization_response(self):
        return "response=2&responsetext=DECLINE&authcode=&transactionid=1274647575&avsresponse=&cvvresponse=N&orderid=1&type=auth&response_code=200"

    def successful_capture_response(self):  return self.successful_authorization_response()  #  FIXME  get a real one!
    def failed_capture_response(self):      return self.failed_authorization_response()  #  FIXME  get a real one!

import urlparse
import urllib
import cgi

class BrainTreeOrangeMockServer(object):
    def __init__(self, failure=None):
        self.failure = failure

    def __call__(self, url, msg):
        return self.receive(urllib.urlencode(msg))

    def receive(self, msg):
        if self.failure:
            return self.failure
        if hasattr(urlparse, 'parse_qsl'):
            data = dict(urlparse.parse_qsl(msg))
        else:
            data = dict(cgi.parse_qsl(msg))
        assert data['username']
        assert data['password']
        if 'type' not in data and data.get('customer_vault', None) == 'add_customer':
            self.validate_payment_info(data)
            return self.simple_vault_store(data)
        try:
            assert data['type'] in ('auth', 'sale', 'capture', 'void', 'refund')
        except:
            print data
            raise
        return getattr(self, data['type'])(data)
    
    def failure_message(self):
        return {'response':'2',
                'responsetext':'DECLINE',
                'response_code':'200',}
    
    def success_message(self):
        return {'response':'1',
                'responsetext':'SUCCESS',
                'authcode':'123456',
                'transactionid':'123456789',
                'response_code':'100',}
    
    def send(self, data):
        return urllib.urlencode(data)
    
    def validate_payment_info(self, data):
        assert ('customer_vault_id' in data or
                    ('ccnumber' in data and
                     'ccexp' in data))
    
    def simple_vault_store(self, data):
        return self.send({'response':'1', 
                          'responsetext':'Customer Added',
                          'response_code':'100',
                          'customer_vault_id': '99999999'})
    
    def auth(self, data):
        response = self.success_message()
        if data.get('customer_vault', None) == 'add_customer':
            response.update(self.card_store(data))
        self.validate_payment_info(data)
        assert 'amount' in data
        return self.send(response)
    
    def sale(self, data):
        response = self.success_message()
        if data.get('customer_vault', None) == 'add_customer':
            response.update(self.card_store(data))
        self.validate_payment_info(data)
        assert 'amount' in data
        return self.send(response)
    
    def capture(self, data):
        assert 'transactionid' in data
        response = self.success_message()
        return self.send(response)
    
    def void(self, data):
        assert 'transactionid' in data
        response = self.success_message()
        return self.send(response)
    
    def refund(self, data):
        assert 'transactionid' in data
        response = self.success_message()
        return self.send(response)
    
    def card_store(self, data):
        return {'customer_vault_id':'999999'}

