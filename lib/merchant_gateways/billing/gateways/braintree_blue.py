# -*- coding: utf-8 -*-
from gateway import Gateway

from merchant_gateways.billing import response
import braintree
from braintree.configuration import Configuration
from braintree.braintree_gateway import BraintreeGateway
from braintree.transaction import Transaction

class BraintreeBlue(Gateway):  # CONSIDER most of this belongs in a class SmartPs, which is Braintree's actual implementation
    def get_configured_gateway(self):
        #TODO grab specific options
        configuration = Configuration(**self.options)
        return BraintreeGateway(configuration)

    class Response(response.Response):
        pass

    def generate_payment_info(self, money, credit_card):
        braintree.Configuration.use_unsafe_ssl = True  #  TODO  either remove this, or call it early and often
        exp = '%02i/%i' % (credit_card.month, credit_card.year)
        info = {
                "amount": '%.02f' % money.amount,
                "credit_card": {
                    "number": credit_card.number,  #  TODO  nearby test on this
                    "expiration_date": exp
                }}
        if getattr(credit_card, 'custom_fields', None):
            info["custom_fields"] = credit_card.custom_fields
        return info
    
    def create_address(self, address):
        return {
            'first_name': address['firstname'],
            'last_name': address['lastname'],
            'company': address['company'],
            'street_address': address['street1'],
            'extended_address': address['street2'],
            'locality': address['city'],
            'region': address['state'],
            'postal_code': address['zip'],
            'country_code_alpha2': address['country'],
        }
    
    def create_credit_card(self, credit_card):
        data = {
            "number": credit_card.number,
            "expiration_date": '%02i/%i' % (credit_card.month, credit_card.year),
            'cardholder_name': credit_card.name(),
        }
        if credit_card.verification_value:
            data['cvv'] = credit_card.verification_value
        return data
    
    def wrap_result(self, result):
        return self.Response(result.is_success, result.transaction.processor_response_text, result,
                                 is_test = self.gateway_mode == 'test',
                                 authorization = result.transaction.processor_authorization_code
                                )

    def authorize(self, money, credit_card=None, card_store_id=None, **options):
        gateway = self.get_configured_gateway()
        params = {'amount': money.amount,
                  'type': Transaction.Type.Sale,}
        if credit_card:
            params['credit_card'] = self.create_credit_card(credit_card)
        else:
            params['customer_id'] = card_store_id
        if 'address' in options:
            params['billing'] = self.create_address(options['address'])
        if 'shipping_address' in options:
            params['shipping'] = self.create_address(options['shipping_address'])
        result = gateway.transaction_gateway.create(params)

        return self.wrap_result(result)


    def purchase(self, money, credit_card=None, card_store_id=None, **options):
        options['submit_for_settlement'] = True
        return self.authorize(money, credit_card=credit_card, card_store_id=card_store_id, **options)

    def capture(self, money, authorization, **options):
        gateway = self.get_configured_gateway()
        if money is not None:
            amount = money.amount
        else:
            amount = None
        result = gateway.transaction_gateway.submit_for_settlement(authorization, amount)
        return self.wrap_result(result)

    def void(self, authorization, **options):
        gateway = self.get_configured_gateway()
        result = gateway.transaction_gateway.void(authorization)
        return self.wrap_result(result)

    def credit(self, money, authorization, **options):
        gateway = self.get_configured_gateway()
        params = {'amount': abs(money.amount),
                  'type': Transaction.Type.Credit,
                  "payment_method_token": authorization,}
        result = gateway.transaction_gateway.create(params)

        return self.wrap_result(result)

    #def recurring(self, money, credit_card, **options):
    #    raise NotImplementedError

    #def card_store(self, credit_card, **options):
    #    raise NotImplementedError

    #def unstore(self, card_store_id, **options):
    #    raise NotImplementedError


