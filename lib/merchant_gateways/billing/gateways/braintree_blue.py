# -*- coding: utf-8 -*-
from gateway import Gateway

from merchant_gateways.billing import response
import braintree
from braintree.configuration import Configuration
from braintree.braintree_gateway import BraintreeGateway
from braintree.transaction import Transaction

class BraintreeBlue(Gateway):  # CONSIDER most of this belongs in a class SmartPs, which is Braintree's actual implementation
    CARD_STORE = True
    
    def get_configured_gateway(self):
        options = {'environment':'',
                   'merchant_id':self.options.get('merchant_id'),
                   'public_key':self.options.get('public_key'),
                   'private_key':self.options.get('private_key'),}
        if self.gateway_mode != 'live':
            options['environment'] = braintree.Environment.Sandbox
        else:
            options['environment'] = braintree.Environment.Production
        braintree.Configuration.configure(**options)
        configuration = Configuration(**options)
        return BraintreeGateway(configuration)

    class Response(response.Response):
        pass
    
    def create_address(self, address):
        return {
            'first_name': address['firstname'],
            'last_name': address['lastname'],
            'company': address['company'],
            'street_address': address['address1'],
            'extended_address': address['address2'],
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
        if hasattr(result, 'errors') and result.errors.deep_errors:
            message = ';\n'.join(error.message for error in result.errors.deep_errors)
        else:
            message = result.transaction.processor_response_text
        authorization = None
        if result.transaction:
            authorization = result.transaction.id
        return self.Response(result.is_success, message, result,
                                 is_test = self.gateway_mode == 'test',
                                 authorization = authorization,
                                )

    def authorize(self, money, credit_card=None, card_store_id=None, **options):
        gateway = self.get_configured_gateway()
        params = {'amount': money.amount,
                  'type': Transaction.Type.Sale,}
        if credit_card:
            params['credit_card'] = self.create_credit_card(credit_card)
            if 'address' in options:
                params['billing'] = self.create_address(options.pop('address'))
        else:
            params['payment_method_token'] = card_store_id
            options.pop('address', None)
        if 'ship_address' in options:
            params['shipping'] = self.create_address(options.pop('ship_address'))
        
        #remove unsupported options
        options.pop('order_id', None)
        options.pop('description', None)
        if options:
            params['options'] = options
        result = gateway.transaction.create(params)
        response = self.wrap_result(result)
        return response


    def purchase(self, money, credit_card=None, card_store_id=None, **options):
        options['submit_for_settlement'] = True
        return self.authorize(money, credit_card=credit_card, card_store_id=card_store_id, **options)

    def capture(self, money, authorization, **options):
        gateway = self.get_configured_gateway()
        if money is not None:
            amount = money.amount
        else:
            amount = None
        result = gateway.transaction.submit_for_settlement(authorization, amount)
        return self.wrap_result(result)

    def void(self, authorization, **options):
        gateway = self.get_configured_gateway()
        result = gateway.transaction.void(authorization)
        return self.wrap_result(result)
    
    def refund(self, money, authorization, **options):
        gateway = self.get_configured_gateway()
        result = gateway.transaction.refund(authorization, abs(money.amount))
        return self.wrap_result(result)
    
    def credit(self, money, authorization, **options):
        gateway = self.get_configured_gateway()
        params = {'amount': abs(money.amount),
                  'type': Transaction.Type.Credit,
                  "payment_method_token": authorization,}
        result = gateway.transaction.create(params)

        return self.wrap_result(result)

    #def recurring(self, money, credit_card, **options):
    #    raise NotImplementedError

    #def card_store(self, credit_card, **options):
    #    raise NotImplementedError

    #def unstore(self, card_store_id, **options):
    #    raise NotImplementedError


