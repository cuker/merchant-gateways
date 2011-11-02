from merchant_gateways.billing.gateways.cybersource import Cybersource
from merchant_gateways.tests.billing.gateways.cybersource_suite import CybersourceMockServer
from merchant_gateways.tests.billing.gateways.gateway_suite import GatewayTestCase

from mock import Mock, patch
from money import Money

class CybersourceTests(GatewayTestCase):

    def get_gateway(self):
        return Cybersource(merchant_id='infodev', api_key='482046C3A7E94F5')

    def get_success_mock(self):
        return Mock(side_effect=CybersourceMockServer())
    
    def test_cybersource_options(self):
        gateway = self.get_gateway()
        assert gateway.supports_action('authorize')
        mock_server = self.get_success_mock()
        credit_card = self.get_dummy_credit_card()
        address = self.get_dummy_billing_address()
        ship_address = self.get_dummy_shipping_address()
        #'ignoreAVSResult', 'ignoreCVResult', 'ignoreDAVResult', 'ignoreExportResult', 'ignoreValidateResult', 'declineAVSFlags', 'scoreThreshold']
        with patch.object(gateway, 'post_webservice', mock_server) as mock_do:
            response = gateway.authorize(Money(100, 'USD'), credit_card, address=address, ship_address=ship_address, ip_address='127.0.0.1',
                                         ignoreAVSResult=True, ignoreCVResult=True, ignoreDAVResult=True, ignoreExportResult=True, ignoreValidateResult=True,
                                         declineAVSFlags="N", scoreThreshold=0)
        #TODO inspect generated request
        self.assertTrue(response.authorization)
        self.assertTrue(response.success)

