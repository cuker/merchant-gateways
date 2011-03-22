# -*- coding: utf-8 -*-
from gateway import Gateway

from merchant_gateways.billing import response

#  TODO  bake all this:
'''
Test transactions can be submitted with the following information:

Visa 4111111111111111
MasterCard 5431111111111111
DiscoverCard 6011601160116611
American Express 341111111111111
Credit Card Expiration 10/10
eCheck Acct & Routing 123123123
Amount >1.00

Triggering Matches, Failures and Errors in Test Mode

To cause a transaction to decline, pass an amount less than 1.00. This only applies to test mode. In live mode, all transaction amounts are allowed.

To trigger a fatal error, pass an invalid card number.

To simulate a CVV Match, pass 999 in the cvv field. Anything else will simulate a mismatch.

To simulate an AVS Match
- Pass 77777 in the zip field for a ‘Z – 5 Character Zip match only’.
- Pass 888 in the address1 field to generate an ‘A – Address match only’.
- Pass both of the above for a ‘Y – Exact match, 5-character numeric ZIP’ match.
- Anything else will simulate a AVS mismatch.

Note specifically configured AVS and CVV settings in a test environment do not work. Use the above information to trigger the desired match or mismatch.

Test Mode Limitations

The test mode allows you to test nearly all of the capabilities of the API. However, since test mode never communicates with the bank, there are some things that you are not able to test:


Recurring billing

You can test the API to add the customer to a plan (using "plantest"), but it will not run the subsequent transactions in that plan.

AVS/CVV

Since you are not actually connecting with the issuing bank, you will not be able to test real AVS/CVV restrictions with real cards. All test transactions will go through regardless of your AVS/CVV rules, though you can test AVS/CVV responses using the above values.

When issuing a transaction while adding the customer to the vault in live mode, the vault record will not be created if the transaction is rejected based on AVS or CVV rules. However, in test mode, the vault record will be created regardless of AVS/CVV response.

'''


class BraintreeOrange(Gateway):

    TEST_URI = 'https://secure.braintreepaymentgateway.com/api/transact.php'  #  TODO  real test url
    LIVE_URI = 'https://secure.braintreepaymentgateway.com/api/transact.php'  #  TODO  put other URIs inside their gateways
    CARD_STORE = True

    class Response(response.Response):
        pass

    def adapt_credit_card(self, credit_card):
        if credit_card:
            return {'ccnumber':credit_card.number,
                    'ccexp':'%02i%s' % (credit_card.month, str(credit_card.year)[2:4]), # TODO  real date formatter
                    'cvv':credit_card.verification_value,
                    'firstname':credit_card.first_name,
                    'lastname':credit_card.last_name}
        return {}
    
    def adapt_currency(self, money):
        if money is not None:
            return {'amount': '%.02f' % money.amount,  #  TODO  less floating point error risk
                    'currency': money.currency.code}
        return {}

    def authorize(self, money, credit_card, **options):
        request = self.adapt_credit_card(credit_card)
        request.update(self.adapt_currency(money))
        return self.commit('auth', request, **options)

    def purchase(self, money, credit_card, **options):
        request = self.adapt_credit_card(credit_card)
        request.update(self.adapt_currency(money))
        return self.commit('sale', request, **options)

    def capture(self, money, authorization, **options):
        request = {'transactionid':authorization}
        return self.commit('capture', request, **options)

    def card_store(self, credit_card, **options):
        request = self.adapt_credit_card(credit_card)
        request['customer_vault'] = 'add_customer'
        response = self.commit(None, request, **options)
        response.card_store_id = response.result.get('customer_vault_id', '')  #  FIXME  me should be a default_dict
        return response

    def void(self, authorization, **options):
        request = {'transactionid':authorization}
        return self.commit('void', request, **options)
    
    def credit(self, money, authorization, **options):
        request = {'transactionid':authorization}
        request.update(self.adapt_currency(money))
        return self.commit('refund', request, **options)

    def parse(self, urlencoded):  #  TODO  dry me
        import cgi
        qsparams = cgi.parse_qs(urlencoded, keep_blank_values=True)

        for k,v in qsparams.items():  #  TODO  have we seen this before..?
            if len(v) == 1:
                qsparams[k] = v[0] # easier to manipulate, because most real-life params are singular
            else:
                qsparams[k] = v

        # print qsparams
        return qsparams

    def commit(self, action, request, **options):
        url = BraintreeOrange.LIVE_URI  #  TODO  or LIVE_URI

        request['username'] = self.options['login']  #  TODO  rename request to parameters
        request['password'] = self.options['password']  #  TODO  use the default_dict
        if action:  request['type'] = action

        if 'processor_id' in options and options['processor_id'] != '':
            request['processor_id'] = options['processor_id']

        for key, value in options.items():
            if 'merchant_defined_field_' in key:  #  CONSIDER  have we seen this before?
                request[key] = value

        if options.get('card_store_id', None):  #  FIXME  make me more standard and generic
            request['customer_vault_id'] = options['card_store_id']

        raw_result = self.post_webservice(url, request)
        result = self.parse(raw_result)
        message  = result.get('responsetext', '')  #  TODO  what is this for auth? (And use a default_dict already)
        success  = result.get('response', '') == '1'  #  TODO  what about 2 or 3?
        trans_id = result.get('transactionid', '')

        return BraintreeOrange.Response(success, message, result,
                                        authorization=trans_id,
                                        is_test=False,  #  TODO
                                        transaction=trans_id )
