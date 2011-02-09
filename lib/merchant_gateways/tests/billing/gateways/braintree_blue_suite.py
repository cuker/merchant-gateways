from __future__ import with_statement
import datetime


class MerchantGatewaysBraintreeBlueSuite:

    def mock_gateway_webservice(self, returns, lamb):
        from mock import patch
        call_args = None

        with patch('braintree.util.http.Http.post') as mock_do:
            mock_do.return_value = returns
            lamb()
            call_args = mock_do.call_args[0]

        self.response = getattr(self.gateway, 'response', {})  #  TODO  all web service mockers do this
        return call_args

    def successful_authorization_response(self):
        return {u'transaction': {u'amount': u'100.00',
                  u'avs_error_response_code': None,
                  u'avs_postal_code_response_code': u'I',
                  u'avs_street_address_response_code': u'I',
                  u'billing': {u'company': None,
                               u'country_name': None,
                               u'extended_address': None,
                               u'first_name': None,
                               u'id': None,
                               u'last_name': None,
                               u'locality': None,
                               u'postal_code': None,
                               u'region': None,
                               u'street_address': None},
                  u'created_at': datetime.datetime(2010, 5, 19, 23, 25, 46),
                  u'credit_card': {u'bin': u'510510',
                                   u'card_type': u'MasterCard',
                                   u'cardholder_name': None,
                                   u'customer_location': u'US',
                                   u'expiration_month': u'05',
                                   u'expiration_year': u'2012',
                                   u'last_4': u'5100',
                                   u'token': None},
                  u'currency': u'USD',
                  u'custom_fields': '',
                  u'customer': {u'company': None,
                                u'email': None,
                                u'fax': None,
                                u'first_name': None,
                                u'id': None,
                                u'last_name': None,
                                u'phone': None,
                                u'website': None},
                  u'cvv_response_code': u'I',
                  u'id': u'fbyrfg',
                  u'merchant_account_id': u'Cyclotronics LLC',
                  u'order_id': None,
                  u'processor_authorization_code': u'54173',
                  u'processor_response_code': u'1000',
                  u'processor_response_text': u'Approved',
                  u'refund_id': None,
                  u'shipping': {u'company': None,
                                u'country_name': None,
                                u'extended_address': None,
                                u'first_name': None,
                                u'id': None,
                                u'last_name': None,
                                u'locality': None,
                                u'postal_code': None,
                                u'region': None,
                                u'street_address': None},
                  u'status': u'authorized',  #  TODO  use me
                  u'status_history': [{u'amount': u'100.00',
                                       u'status': u'authorized',  #  TODO  use me
                                       u'timestamp': datetime.datetime(2010, 5, 19, 23, 25, 47),
                                       u'transaction_source': u'API',
                                       u'user': u'Mongo'}],
                  u'type': u'sale',
                  u'updated_at': datetime.datetime(2010, 5, 19, 23, 25, 47)}}

    def successful_purchase_response(self):  #  TODO  aaand use me!
        return {u'transaction': {u'amount': u'100.00',
                  u'avs_error_response_code': None,
                  u'avs_postal_code_response_code': u'I',
                  u'avs_street_address_response_code': u'I',  #  TODO  put them in the CVVResult and AVSResult objects!
                  u'billing': {u'company': None,
                               u'country_name': None,
                               u'extended_address': None,
                               u'first_name': None,
                               u'id': None,
                               u'last_name': None,
                               u'locality': None,
                               u'postal_code': None,
                               u'region': None,
                               u'street_address': None},
                  u'created_at': datetime.datetime(2010, 5, 19, 22, 38, 42),
                  u'credit_card': {u'bin': u'510510',
                                   u'card_type': u'MasterCard',
                                   u'cardholder_name': None,
                                   u'customer_location': u'US',
                                   u'expiration_month': u'05',
                                   u'expiration_year': u'2012',
                                   u'last_4': u'5100',
                                   u'token': None},
                  u'currency': u'USD',
                  u'custom_fields': '',
                  u'customer': {u'company': None,
                                u'email': None,
                                u'fax': None,
                                u'first_name': None,
                                u'id': None,
                                u'last_name': None,
                                u'phone': None,
                                u'website': None},
                  u'cvv_response_code': u'I',  #  TODO  put them in the CVVResult and AVSResult objects!
                  u'id': u'8y5jn6',
                  u'merchant_account_id': u'Crunchy Frog',
                  u'order_id': None,
                  u'processor_authorization_code': u'54158',
                  u'processor_response_code': u'1000',
                  u'processor_response_text': u'Approved',
                  u'refund_id': None,
                  u'shipping': {u'company': None,
                                u'country_name': None,
                                u'extended_address': None,
                                u'first_name': None,
                                u'id': None,
                                u'last_name': None,
                                u'locality': None,
                                u'postal_code': None,
                                u'region': None,
                                u'street_address': None},
                  u'status': u'submitted_for_settlement',  #  TODO  use me
                  u'status_history': [{u'amount': u'100.00',
                                       u'status': u'authorized',  #  TODO  use me
                                       u'timestamp': datetime.datetime(2010, 5, 19, 22, 38, 44),
                                       u'transaction_source': u'API',
                                       u'user': u'Mongo'},
                                      {u'amount': u'100.00',
                                       u'status': u'submitted_for_settlement',
                                       u'timestamp': datetime.datetime(2010, 5, 19, 22, 38, 44),
                                       u'transaction_source': u'API',
                                       u'user': u'Mongo'}],
                  u'type': u'sale',
                  u'updated_at': datetime.datetime(2010, 5, 19, 22, 38, 44)}}

    def failed_authorization_response(self):
        return {u'api_error_response': {u'errors': {u'errors': ''},
                     u'params': {u'transaction': {u'amount': u'100',
                                                  u'credit_card': {u'expiration_date': u'05/2012'},
                                                  u'type': u'sale'}},
                     u'transaction': {u'amount': u'100.00',
                                      u'avs_error_response_code': None,
                                      u'avs_postal_code_response_code': None,
                                      u'avs_street_address_response_code': None,
                                      u'billing': {u'company': None,
                                                   u'country_name': None,
                                                   u'extended_address': None,
                                                   u'first_name': None,
                                                   u'id': None,
                                                   u'last_name': None,
                                                   u'locality': None,
                                                   u'postal_code': None,
                                                   u'region': None,
                                                   u'street_address': None},
                                      u'created_at': datetime.datetime(2010, 5, 20, 21, 56, 41),
                                      u'credit_card': {u'bin': u'510510',
                                                       u'card_type': u'MasterCard',
                                                       u'cardholder_name': None,
                                                       u'customer_location': u'US',
                                                       u'expiration_month': u'05',
                                                       u'expiration_year': u'2012',
                                                       u'last_4': u'5100',
                                                       u'token': None},
                                      u'currency': u'USD',
                                      u'custom_fields': '',
                                      u'customer': {u'company': None,
                                                    u'email': None,
                                                    u'fax': None,
                                                    u'first_name': None,
                                                    u'id': None,
                                                    u'last_name': None,
                                                    u'phone': None,
                                                    u'website': None},
                                      u'cvv_response_code': None,
                                      u'id': u'kb3k4w',
                                      u'merchant_account_id': u'Spring Surprise',
                                      u'order_id': None,
                                      u'processor_authorization_code': None,
                                      u'processor_response_code': '',
                                      u'processor_response_text': u'Unknown ()',
                                      u'refund_id': None,
                                      u'shipping': {u'company': None,
                                                    u'country_name': None,
                                                    u'extended_address': None,
                                                    u'first_name': None,
                                                    u'id': None,
                                                    u'last_name': None,
                                                    u'locality': None,
                                                    u'postal_code': None,
                                                    u'region': None,
                                                    u'street_address': None},
                                      u'status': u'gateway_rejected',
                                      u'status_history': [{u'amount': u'100.00',
                                                           u'status': u'gateway_rejected',
                                                           u'timestamp': datetime.datetime(2010, 5, 20, 21, 56, 41),
                                                           u'transaction_source': u'API',
                                                           u'user': u'Mongo'}],
                                      u'type': u'sale',
                                      u'updated_at': datetime.datetime(2010, 5, 20, 21, 56, 41)}}}
