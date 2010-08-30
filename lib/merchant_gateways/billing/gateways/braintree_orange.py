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

#  TODO  rename the other one to BraintreeBlue

class BraintreeOrange(Gateway):

    TEST_URI = 'https://secure.braintreepaymentgateway.com/api/transact.php'  #  TODO  real test url
    LIVE_URI = 'https://secure.braintreepaymentgateway.com/api/transact.php'  #  TODO  put other URIs inside their gateways

    class Response(response.Response):
        pass

    def purchase(self, money, credit_card, **options):
        request = dict(ccnumber=credit_card.number,
                       ccexp='%02i%s' % (credit_card.month, str(credit_card.year)[2:4]) # TODO  real date formatter
                      )
        self.commit(request, **options)

    def parse(self, urlencoded):  #  TODO  dry me
        import cgi
        qsparams = cgi.parse_qs(urlencoded)

        for k,v in qsparams.items():  #  TODO  have we seen this before..?
            if len(v) == 1:
                qsparams[k] = v[0] # easier to manipulate, because most real-life params are singular

        print qsparams
        return qsparams

    def commit(self, request, **options):
        url = BraintreeOrange.TEST_URI  #  TODO  or LIVE_URI

        request['username'] = self.options['login']
        request['password'] = self.options['password']
        #  TODO  action here

        self.result = self.parse(self.post_webservice(url, request))

        message = self.result['responsetext']
        success = self.result['response'] == '1'  #  TODO  what about 2 or 3?

        self.response = BraintreeOrange.Response(success, message, self.result,
                                                  authorization=self.result['authcode'],
                                                  is_test=True,  #  TODO
                                                  transaction='TODO' )
