# -*- coding: utf-8 -*-


from gateway import Gateway, default_dict, xStr

from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult  #  TODO  need all these?
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from urllib import urlencode
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money
import sys
sys.path.insert(0, '/home/phlip/tools/braintree-2.2.1')
from merchant_gateways.lib.post import post  #  CONSIDER  move me to gateway.py

from pprint import pprint

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

    def authorize(self, money, credit_card, **options):
        request = {}

        if credit_card:
            request = dict( ccnumber=credit_card.number,
                            ccexp='%02i%s' % (credit_card.month, str(credit_card.year)[2:4]), # TODO  real date formatter
                            cvv=credit_card.verification_value,
                            firstname=credit_card.first_name,
                            lastname=credit_card.last_name )

        self._add_currency(money, request)
          #  TODO  move more into here
        self.commit('auth', money, request, **options)
        return self.response  #  TODO  more actions need to do this

    def purchase(self, money, credit_card, **options):
        request = dict( ccnumber=credit_card.number,
                        ccexp='%02i%s' % (credit_card.month, str(credit_card.year)[2:4]), # TODO  real date formatter
                        cvv=credit_card.verification_value,
                        firstname=credit_card.first_name,
                        lastname=credit_card.last_name )

        self._add_currency(money, request)
          #  TODO  move more into here
        self.commit('sale', money, request, **options)
        return self.response

    def capture(self, money, authorization, **options):
        post = dict(transactionid=authorization)
        self.commit('capture', money, post, **options)
        return self.response

    def store(self, credit_card, **options):
        ccexp = '%02i%s' % (credit_card.month, str(credit_card.year)[2:4])

        post = dict( customer_vault='add_customer',
                     ccnumber=credit_card.number,
                     ccexp=ccexp )  #  TODO  also some first-and-last-name action

        self.commit(None, None, post, **options)  #  TODO  take out the money if not used
        return self.response

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

    def commit(self, action, money, request, **options):  #  TODO  why we pass money here?
        url = BraintreeOrange.TEST_URI  #  TODO  or LIVE_URI

        request['username'] = self.options['login']  #  TODO  rename request to parameters
        request['password'] = self.options['password']  #  TODO  use the default_dict
        if action:  request['type'] = action
        request['orderid']  = str(options['order_id'])

#        print request  #  TODO
        request['currency'] = 'USD'  #  TODO fix higher up

        for key, value in options.items():
            if 'merchant_defined_field_' in key:  #  FIXME  have we seen this before?
                request[key] = value

        raw_result = self.post_webservice(url, request)
#        print repr(raw_result)
        self.result = self.parse(raw_result)
        print self.result

        message  = self.result.get('responsetext', '')  #  TODO  what is this for auth? (And use a default_dict already)
        success  = self.result.get('response', '') == '1'  #  TODO  what about 2 or 3?
        trans_id = self.result.get('transactionid', '')

        self.response = BraintreeOrange.Response( success, message, self.result,
                                                  authorization=trans_id,
                                                  is_test=True,  #  TODO
                                                  transaction=trans_id )

    def _add_currency(self, money, request):  #  TODO  all internal methods should use _
        if money:
            request['amount'] = '%.02f' % money.amount  #  TODO  less floating point error risk
            request['currency'] = money.currency.code

