# -*- coding: utf-8 -*-

from gateway import Gateway, default_dict, xStr
from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money

#  TODO  Callaway noticed on the form that was completed that Discover was selected.
#       They no longer accept Discover. This was updated on the form, but please make
#       sure this is carried through to the site.

#  TODO  Also in the UK they want to be able to accept Visa Electron and Delta, both
#       are Visa debit cards. This shouldn’t be any additional work.
#      Please make sure these cards will be accepted. They will be testing these.

#  http://download.chasepaymentech.com/
#  http://www.userhelpguides.com/dotnetcharge/paymentechorbital.php
# http://doc.rhinonet.com/paymentech/Orbital%20Gateway%20Interface%20Specification%202.6.0.pdf
# http://idotmind.com/chase-paymentech-orbital-gateway-phreebooks-payment-module-gotchas/

TEST_URL = 'https://orbitalvar1.paymentech.net/authorize'
LIVE_URL = 'https://orbital1.paymentech.net/authorize'

 #  CONSIDER  also look at orbitalvar2 etc.

class PaymentechOrbital(Gateway):

    def authorize(self, money, creditcard, **options):
        '''
        Request an authorization for an amount from CyberSource

        You must supply an :order_id in the options hash  TODO  complain if it ain't there
        '''

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        self.options.update(options)
        message = self.build_authorization_request(money, creditcard, **self.options)  #  TODO  _authorization_request, everywhere!!
        return self.commit(message, **self.options)

    def purchase(self, money, credit_card, **options):
        '''Purchase is an auth followed by a capture
           You must supply an order_id in the options hash'''

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        self.options = self.setup_address_hash(**self.options)
        message = self.build_purchase_request(money, credit_card, **self.options)
        return self.commit(message, **self.options)

    def build_authorization_request(self, money, credit_card, **options):
        return self.build_request('A', money, credit_card, **options)

    def build_purchase_request(self, money, credit_card, **options):
        return self.build_request('AC', money, credit_card, **options)

    def build_request(self, message_type, money, credit_card, **options):

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'

        fields = default_dict(**self.options)

#                            country='USA',  #  TODO vet this default

        grandTotalAmount = '%.2f' % money.amount  #  CONSIDER  format AMOUNT like this better, everywhere
        grandTotalAmount = grandTotalAmount.replace('.', '')  #  CONSIDER internationalize that and respect the CurrencyExponent
        if options.has_key('billing_address'):  fields.update(options['billing_address'])  #  TODO  what about address?
        fields.update(options)
        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:] #  CONSIDER  credit_card_format
        x = XML
        numeric = money.currency.numeric

        new_order = x.NewOrder(
                        x.IndustryType('EC'),  #  'EC'ommerce - a web buy
                        x.MessageType(message_type),
                            # TODO  hallow A – Authorization request
                            #           AC – Authorization and Mark for Capture
                            #          FC – Force-Capture request
                            #        R – Refund request
                        x.BIN('000001'),
                        x.MerchantID(options['merchant_id']),
                        x.TerminalID('001'),
                        # x.CardBrand(''),

# TODO SW – Switch / Solo ED – European Direct Debit EC – Electronic Check BL – Bill Me Later DP – PINLess Debit [Generic Value Used in Requests]

                        x.AccountNum(credit_card.number),
                        x.Exp(exp_code),
                        x.CurrencyCode(numeric),
                        x.CurrencyExponent('2'),  #  TODO  figure out what this is it's probably important
                        x.CardSecValInd('1'),  #  CONSIDER  visa & discover only - nullify for others
                        x.CardSecVal(credit_card.verification_value),
                        x.AVSzip(fields['zip']),
                        x.AVSaddress1(fields['address1']),  #  TODO  pull an AVSresponse?
                        x.AVSaddress2(fields['address2']),
                        x.AVScity(fields['city']),
                        x.AVSstate(fields['state']),
                        x.AVSphoneNum(fields['phone']),
                        x.AVSname(credit_card.first_name + ' ' + credit_card.last_name),
                        x.AVScountryCode('US'), #  TODO other countries - and ensure this is ISO-compliant or we get a DTD fault
                        x.CustomerProfileFromOrderInd('A'),
                        x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID('TODO'),
                        x.Amount(grandTotalAmount)
                        )
        return xStr(XML.Request(new_order))

#                        XML.email(fields['email']),
#                      XML.expirationMonth(str(credit_card.month)),
#                      XML.expirationYear(str(credit_card.year)),
#                      XML.cardType('001')  #  TODO

    def parse(self, soap):
        result = {}
        keys  = self.soap_keys()
        doc  = etree.XML(soap)

        for key in keys:
            nodes = doc.xpath('//' + key)
            result[key] = len(nodes) and nodes[0].text or None

        return result

        #  TODO  what's CapMandatory? Need it? Take it out?

    def soap_keys(self):  #   CONSIDER  better name coz it's not always about the SOAP
        return ( 'AccountNum',                'MerchantID',
                 'ApprovalStatus',            'MessageType',
                 'AuthCode',                  'OrderID',
                 'AVSRespCode',               'ProcStatus',
                 'CardBrand',                 'ProfileProcStatus',
                 'CAVVRespCode',              'RecurringAdviceCd',
                 'CustomerName',              'RespCode',
                 'CustomerProfileMessage',    'RespMsg',
                 'CustomerRefNum',            'RespTime',
                 'CVV2RespCode',              'StatusMsg',
                 'HostAVSRespCode',           'TerminalID',
                 'HostCVV2RespCode',          'TxRefIdx',
                 'HostRespCode',              'TxRefNum',
                 'IndustryType', )

    class Response(response.Response):
        pass

    def commit(self, request, **options):
        uri           = self.is_test and TEST_URL or LIVE_URL
        self.request  = request  # CONSIDER  standardize this
        # request       = self.build_request(request, **options)
        headers = self._generate_headers(request, **options)
        self.result   = self.parse(self.post_webservice(uri, request, headers))  #  CONSIDER  no version of post_webservice needs options
        self.success  = self.result['ApprovalStatus'] == '1'  #  TODO  these belong to the response not the gateway
        self.message  = self.result['StatusMsg']
        authorization = self.result['TxRefNum']
        avs_resp_code = self.result.get('AVSRespCode', '') or ''

        r = self.__class__.Response( self.success, self.message, self.result,
                                     is_test=self.is_test,
                                     authorization=authorization,
                                     avs_result=avs_resp_code.strip(),
                                     cvv_result=self.result['CVV2RespCode']  #  CONSIDER  what about the 2?
                                    )
        r.result = self.result  #  TODO  use params for something else
        self.response = r
        return r

    def _generate_headers(self, request, **options):
        return {  #  TODO  TDD these
                  "MIME-Version": "1.0",
                  "Content-Type": "Application/PTI46", #  CONSIDER  why is this code here??
                  "Content-transfer-encoding": "text",
                  "Request-number": "1",
                  "Document-type": "Request",
                  "Content-length": len(request),
                  "Merchant-id": options['merchant_id']  #  TODO  useful error message if it's not there
                  }

