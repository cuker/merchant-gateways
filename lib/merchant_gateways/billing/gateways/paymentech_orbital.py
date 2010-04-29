# -*- coding: utf-8 -*-

from gateway import Gateway, default_dict, xStr
from merchant_gateways.billing import response
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from lxml import etree
from lxml.builder import ElementMaker
XML = ElementMaker()
from money import Money

#  TODO  bow before http://www.userhelpguides.com/dotnetcharge/paymentechorbital.php
# http://doc.rhinonet.com/paymentech/Orbital%20Gateway%20Interface%20Specification%202.6.0.pdf
# http://idotmind.com/chase-paymentech-orbital-gateway-phreebooks-payment-module-gotchas/

#    Paymentech Orbital
#        Return to Introduction  Previous page  Next page
#    PaymentTechOrbital: http://www.paymentech.net
#
#    Supported Properties:
#    Amount    Required

#    AuthCode    Optional
#    Address    Optional
#    AvsCode    Optional

#    BankCode    Not Used
#    BankName    Not Used

#    Certificate    Not Used
#    City       Optional
#    Code       Optional
#    Country    Not Used
#    CustomerID    Not Used
#    Email       Not Used
#    Description    Optional
#    Server       Optional
#    ErrorCode    Optional
#    ErrorMessage    Optional

#    Login       Required
#    Password    Optional  uh...

#    Month       Required
#    FirstName    Optional
#    LastName    Optional
#    CardName    Optional
#    Number    Required
#    OrderID    Optional
#    Phone       Not Used
#    Setting       Not Used
#    StateProvince    Optional
#    TestMode    Optional
#    Timeout    Optional
#    TransactionID    Optional
#    TransactionType Optional
#    Year       Required
#    ZipPostal    Optional
#
#    Note: You must configure your account with Paymentech Orbital for "End of Day Autosettle" to work with .netCHARGE.
#
#    Transaction Types: Authorize, sale, refund, void, force and postauthorize.
#    Login: property is your merchant id.
#    Password: This field is used to set platform's bin number. Salem Platform is "000001" and Tampa platform is "000002", default is "000002".
#    TerminalID: Merchant Terminal ID assigned by Paymentech. If not set, it is set to "001".
#    AuthCode: property only set for force transaction type.
#    Amount: should not set for full amount void transaction.
#    TransactionID: set from the original transaction value returned if processing a void or postauthorize.
#    CardName:For setting the name on the credit card for this company, use the CardName property (for the full name provided by the customer) in place of FirstName and LastName.
#    Currency: One of these 2 CurrencyCodes. CAD or USD currency code, default is USD.
#    TimeZone: Set to one of the TimeZone enumeration values e.g. obj.TimeZone=TimeZone.PST
#    Complete list of options:
#    AST,EST,CST,MST,PST,AKST,HAST,Indiana, and Arizona.
#    MerchantName: The Merchant Name field should be what is most recognizable to the cardholder [Company name or trade name]. See credit card statement message customization below for more information on accepted values and size limitations.
#
#    Paymentech Orbital Echeck:
#    PaymentType = PaymentType.Echeck
#    BankCode: Bank routing and transit number for the customer. All US Bank Routing Numbers are 9 digits and All Canadian Bank Routing Numbers are 8 Digits.
#
#    BankAccountType: Default is "C". Other options are:
#    C - Consumer Checking [US or Canadian]
#    S - Consumer Savings [US Only]
#    X - Commercial Checking [US Only]
#
#    Number: Customer DDA account number
#
#    Common error and resolution:
#    ErrorCode:protocolerror
#    ErrorMessage: remote server returned an error (412) precondition failed
#
#    Resolution: Add your servers IP address to the Paymentech gateway. This is required before it will accept communication from it.
#
#    Credit card statement message customization (advanced):
#    Salem:
#    - CREDIT - Three options, which conditionally affects the Description [see below]:
#    Max 3 bytes, Max 7 bytes or Max 12 bytes
#    - ECheck: Max 15 bytes
#
#    Tampa: Max 25 bytes.
#    Description: Product description.
#    Salem:
#    - CREDIT:
#    If MerchantName = 3 bytes - then Max = 18 bytes
#    If MerchantName = 7 bytes - then Max = 14 bytes
#    If MerchantName = 12 bytes - then Max = 9 bytes
#    - ECheck: 10 bytes Max
#    Tampa:
#    - This field will not show on Cardholder statements for Tampa Merchants.
#
#    If MerchantName is set, one of the following propreties (MerchantPhone, MerchantEmail or MerchantUrl) must be set.
#    MerchantPhone: Customer Service Phone Number in this format: xxx-xxxxxxx or xxx-xxx-xxxx
#    MerchantEmail: Merchant email.
#    MerchantUrl: Merchant Url.

TEST_URL = 'https://orbitalvar1.paymentech.net/authorize'
LIVE_URL = 'https://orbital1.paymentech.net/authorize'

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

    def purchase(self, amount, credit_card, **options):
        '''Purchase is an auth followed by a capture
           You must supply an order_id in the options hash'''

        money = amount
        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        self.options = self.setup_address_hash(**self.options)
        message = self.build_purchase_request(amount, credit_card, **self.options)
        return self.commit(message, **self.options)

    def build_authorization_request(self, money, credit_card, **options):

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'

        fields = default_dict(**self.options)

#                            country='USA',  #  TODO vet this default

        grandTotalAmount = '%.2f' % money.amount  #  CONSIDER  format AMOUNT like this better, everywhere
        fields.update(options['billing_address'])  #  TODO  what about address?
        fields.update(options)

        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:] #  CONSIDER  credit_card_format
        x = XML

        from money.Money import CURRENCY
        numeric = CURRENCY[str(money.currency)].numeric  #  TODO  this should be an accessor

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
                        x.AVScountryCode('840'), #  CONSIDER  other countries
                        x.CustomerProfileFromOrderInd('A'),
                        x.CustomerProfileOrderOverrideInd('NO'),
                        x.OrderID(''),  #  TODO
                        x.Amount(grandTotalAmount)
                        )
        return xStr(XML.Request(new_order))

#                        XML.email(fields['email']),
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
        url           = self.is_test and TEST_URL or LIVE_URL
        self.request  = request  # CONSIDER  standardize this
        request       = self.build_request(request, **options)
        self.result   = self.parse(self.post_webservice(url, request))  #  CONSIDER  no version of post_webservice needs options
        self.success  = self.result['ApprovalStatus'] == '1'
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
        return r

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

