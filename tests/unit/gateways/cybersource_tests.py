from merchant_gateways.billing.gateways.cybersource import Cybersource
from merchant_gateways.tests.billing.gateways.cybersource_suite import CybersourceMockServer
from merchant_gateways.tests.billing.gateways.gateway_suite import GatewayTestCase

from mock import Mock

class CybersourceTests(GatewayTestCase):

    def get_gateway(self):
        return Cybersource(merchant_id='infodev', api_key='482046C3A7E94F5')

    def get_success_mock(self):
        return Mock(side_effect=CybersourceMockServer())

