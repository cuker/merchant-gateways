# -*- coding: utf-8 -*-

from gateway import Gateway, default_dict, xStr
from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from lxml.builder import ElementMaker
XML = ElementMaker()

#  TODO  bow before http://www.userhelpguides.com/dotnetcharge/paymentechorbital.php
# http://doc.rhinonet.com/paymentech/Orbital%20Gateway%20Interface%20Specification%202.6.0.pdf
# http://idotmind.com/chase-paymentech-orbital-gateway-phreebooks-payment-module-gotchas/

TEST_URL = 'https://orbitalvar1.paymentech.net/authorize'
LIVE_URL = 'https://orbital1.paymentech.net/authorize'

class PaymentechOrbital(Gateway):

    def authorize(self, money, creditcard, **options):
        '''
        Request an authorization for an amount from CyberSource

        You must supply an :order_id in the options hash
        '''

        self.options.update(options)

        message = self.build_auth_request(money, creditcard, **self.options)
        return self.commit(message, **self.options)

    def purchase(self, money, creditcard, **options):
        '''Purchase is an auth followed by a capture
           You must supply an order_id in the options hash'''

        self.options = self.setup_address_hash(**self.options)

    def build_auth_request(self, money, credit_card, **options):

        fields = default_dict(**self.options)

#                            country='USA',  #  TODO vet this default

        grandTotalAmount = '%.2f' % money  #  CONSIDER  format AMOUNT like this better, everywhere
        fields.update(options['billing_address'])  #  TODO  what about address?
        fields.update(options)

        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:] #  TODO  credit_card_format
        x = XML

        new_order = x.NewOrder(
                        x.OrbitalConnectionUsername(fields['login']),  #  TODO  from configs
                        x.OrbitalConnectionPassword(fields['password']),  #  TODO  ibid
                        x.IndustryType('EC'),  #  'EC'ommerce - a web buy
                        x.MessageType('A'),  #  auth fwt!
                            # TODO  hallow A – Authorization request AC – Authorization and Mark for Capture FC – Force-Capture request R – Refund request
                        x.BIN('1'),
                        x.MerchantID('1'),
                        x.TerminalID('1'),
                        x.CardBrand(''),

# TODO SW – Switch / Solo ED – European Direct Debit EC – Electronic Check BL – Bill Me Later DP – PINLess Debit [Generic Value Used in Requests]

                        x.AccountNum(credit_card.number),
                        x.Exp(exp_code),
                        x.CurrencyCode('840'),   #  CONSIDER  non-US currency
                        x.CurrencyExponent('2'),
                        x.CardSecValInd('1'),  #  CONSIDER  visa & discover only - nullify for others
                        x.CardSecVal(credit_card.verification_value),
                        x.AVSzip(fields['zip']),
                        x.AVSaddress1(fields['address1']),  #  TODO  pull an AVSresponse?
                        x.AVSaddress2(fields['address2']),
                        x.AVScity(fields['city']),
                        x.AVSstate(fields['state']),
                        x.AVSphoneNum(fields['phone']),
                        x.AVSname(credit_card.first_name + ' ' + credit_card.last_name),
                        x.AVScountryCode('840'), #  CONSIDER  other countries
                        x.CustomerProfileFromOrderInd('A'),
                        x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID(''),
                        x.Amount(grandTotalAmount)
                        )
        return xStr(XML.Request(new_order))

#                        XML.email(fields['email']),
#                        XML.currency('USD'),
#
#                      XML.expirationMonth(str(credit_card.month)),
#                      XML.expirationYear(str(credit_card.year)),
#                      XML.cardType('001')  #  TODO

# TODO  question fields in Cybersource        (template_p % fields) )

    def parse(self, soap):
        result = {}
        keys  = self.soap_keys()
        doc  = etree.XML(soap)

        for key in keys:
            nodes = doc.xpath('//' + key)
            result[key] = len(nodes) and nodes[0].text or None

        return result

    def soap_keys(self):  #   TODO  better name coz it's not always about the SOAP
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
                 'IndustryType', )  #  TODO  adjust this for paymentech_orbital

    class Response(response.Response):
        pass

    def commit(self, request, **options):
        url = self.is_test and TEST_URL or LIVE_URL
        request = self.build_request(request, **options)
        self.result = self.parse(self.post_webservice(url, request, **options))
        self.success = self.result['ApprovalStatus'] == '1'
        self.message = self.result['StatusMsg']
        authorization = self.result['TxRefNum']

        return self.__class__.Response( self.success, self.message, self.result,
                                        is_test=self.is_test,
                                        authorization=authorization,
#                                       :avs_result => { :code => response[:avsCode] },
                                # TODO        cvv_result=self.result['cvCode']
                                    )

    def build_request(self, body, **options):
        template = '''<?xml version="1.0" encoding="UTF-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
              <s:Header>
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" s:mustUnderstand="1">
                  <wsse:UsernameToken>
                    <wsse:Username>l</wsse:Username>
                    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">p</wsse:Password>
                  </wsse:UsernameToken>
                </wsse:Security>
              </s:Header>
              <s:Body xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <requestMessage xmlns="urn:schemas-cybersource-com:transaction-data-1.32">
                  <merchantID>l</merchantID>
                  <merchantReferenceCode>1000</merchantReferenceCode>
                  <clientLibrary>Ruby Active Merchant</clientLibrary>
                  <clientLibraryVersion>1.0</clientLibraryVersion>
                  <clientEnvironment>Linux</clientEnvironment>
                    %s
                </requestMessage>
              </s:Body>
            </s:Envelope>
            '''

        return template % body

    def build_purchase_request(self, money, creditcard, **options):

        XML = ElementMaker(
        #        namespace="http://my.de/fault/namespace",
         #        nsmap=dict(s="http://schemas.xmlsoap.org/soap/envelope/",
          #              wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
           #            )
        )

        my_doc = XML.Body(XML.billTo)
        #print(etree.tostring(my_doc, pretty_print=True))

#        xml = Builder::XmlMarkup.new :indent => 2
#        add_address(xml, creditcard, options[:billing_address], options)
#        add_purchase_data(xml, money, true, options)
#        add_creditcard(xml, creditcard)
#        add_purchase_service(xml, options)
#        add_business_rules_data(xml)
#        xml.target!

CREDIT_CARD_CODES = dict( v='001',  #  TODO  convert to Orbital
                          m='002', # TODO  verify
                          a='003',  # TODO  verify
                          d='004' )  # TODO  verify
#        :visa  => '001',
 #       :master => '002',
  #      :american_express => '003',
   #     :discover => '004'

