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

from pprint import pprint

TEST_URI = 'sandbox.braintreegateway.com'  #  uh, where?
LIVE_URI = 'secure.braintreepaymentgateway.com'

#  TODO  rename the other one to BraintreeBlue

class BraintreeOrange(Gateway):

    class Response(response.Response):
        pass

