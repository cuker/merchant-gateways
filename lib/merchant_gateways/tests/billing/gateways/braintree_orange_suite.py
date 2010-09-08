
import datetime
import merchant_gateways

class MerchantGatewaysBraintreeOrangeSuite:

    def mock_webservice(self, returns, lamb):
        from mock import patch
        self.call_args = None

        with patch.object(merchant_gateways.billing.gateways.gateway.Gateway, 'post_webservice') as mock_do:
            mock_do.return_value = returns
            lamb()
            self.call_args = mock_do.call_args[0]

             # TODO https://secure.braintreepaymentgateway.com/api/transact.php

        self.response = getattr(self.gateway, 'response', {})  #  TODO  all web service mockers do this
        return self.call_args  #  CONSIDER  all call_args should be self

    def successful_purchase_response(self):
        return 'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'

    def successful_authorization_response(self):
        return 'response=1&responsetext=SUCCESS&authcode=123456&transactionid=510695343&avsresponse=N&cvvresponse=N&orderid=ea1e0d50dcc8cfc6e4b55650c592097e&type=sale&response_code=100'
         # TODO get a real one!

    def failed_authorization_response(self):
        return 'TODO'