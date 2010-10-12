# -*- coding: utf-8 -*-
from merchant_gateways.billing.gateways.braintree_orange import BraintreeOrange
from merchant_gateways.tests.billing.gateways.braintree_orange_suite import BrainTreeOrangeMockServer
from merchant_gateways.tests.billing.gateways.gateway_suite import GatewayTestCase
from mock import Mock

class BraintreeOrangeTests(GatewayTestCase):

    def get_gateway(self):
        return BraintreeOrange(**{'login':'username',
                                  'password':'password'})

    def get_success_mock(self):
        return Mock(side_effect=BrainTreeOrangeMockServer())

