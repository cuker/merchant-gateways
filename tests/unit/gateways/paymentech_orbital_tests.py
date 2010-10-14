# -*- coding: utf-8 -*-

from merchant_gateways.billing.gateways.paymentech_orbital import PaymentechOrbital
from merchant_gateways.tests.billing.gateways.paymentech_orbital_suite import PaymentechOrbitalMockServer
from merchant_gateways.tests.billing.gateways.gateway_suite import GatewayTestCase
from mock import Mock

class PaymentechOrbitalTests(GatewayTestCase):

    def get_gateway(self):
        return PaymentechOrbital(**{'user':'username',
                          'password':'password',
                          'vendor':'VENDORID',
                          'merchant_id':'MYID',})

    def get_success_mock(self):
        return Mock(side_effect=PaymentechOrbitalMockServer())

