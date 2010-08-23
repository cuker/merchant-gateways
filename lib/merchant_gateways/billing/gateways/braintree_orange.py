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

TEST_URI = 'sandbox.braintreegateway.com'  #  uh, where?
LIVE_URI = 'secure.braintreepaymentgateway.com'

#  TODO  rename the other one to BraintreeBlue

class BraintreeOrange(Gateway):

    class Response(response.Response):
        pass

    def purchase(self, money, credit_card, **options):
        request = {}
        self.commit(request, **options)

    def parse(self, urlencoded):  #  TODO  dry me
        import cgi
        qsparams = cgi.parse_qs(urlencoded)

        for k,v in qsparams.items():  #  TODO  have we seen this before..?
            if len(v) == 1:
                qsparams[k] = v[0] # easier to manipulate, because most real-life params are singular

        return qsparams

    def commit(self, request, **options):
        url = 'https://TODO'
        self.result = self.parse(self.post_webservice(url, request))
        self.response = BraintreeOrange.Response('TODO', 'TODO', {}, authorization=self.result['authcode'], is_test=True, transaction='TODO')  #  TODO
