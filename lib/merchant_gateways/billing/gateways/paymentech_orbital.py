# -*- coding: utf-8 -*-
from gateway import Gateway
from merchant_gateways.billing.common import xStr, ElementMaker, ET, gencode, xmltodict
from merchant_gateways.billing import response
import logging
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

 #  CONSIDER  if orbital1 fails, switch to orbital2. And fall back after a while...

class PaymentechOrbital(Gateway):
    CARD_STORE = True
    
    def authorize(self, money, credit_card, **options):
        assert isinstance(money, Money)
        options.update(self.options)
        message = self.build_order_request('A', money=money, credit_card=credit_card, **options)
        return self.commit(message, **self.options)

    def purchase(self, money, credit_card, **options):
        assert isinstance(money, Money)
        options.update(self.options)
        message = self.build_order_request('AC', money=money, credit_card=credit_card, **options)
        return self.commit(message, **self.options)
    
    def capture(self, money, authorization, **options):
        assert isinstance(money, Money)
        options.update(self.options)
        message = self.build_capture_request(money=money, authorization=authorization, **options)
        return self.commit(message, **self.options)
    
    def void(self, authorization, **options):
        options.update(self.options)
        message = self.build_reversal_request(authorization=authorization, **options)
        return self.commit(message, **self.options)
    
    def credit(self, money, authorization, **options):
        assert isinstance(money, Money)
        options.update(self.options)
        message = self.build_order_request('R', money=money, authorization=authorization, **options)
        return self.commit(message, **self.options)
    
    def card_store(self, credit_card, **options):
        options.update(self.options)
        message = self.build_profile_request('C', credit_card=credit_card, **options)
        return self.commit(message, **self.options)
    
    def build_order_credit_card_request(self, credit_card):
        CardSecValInd = ''
        if credit_card._lookup_card_type() in ('visa', 'discover'):
            CardSecValInd = '1'
        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:] #  CONSIDER  credit_card_format
        return {'AccountNum': credit_card.number,
                'Exp': exp_code,
                'CardSecValInd': CardSecValInd,
                'CardSecVal': credit_card.verification_value,
                'AVSname': credit_card.first_name + ' ' + credit_card.last_name,}
    
    def build_order_address_request(self, fields):
        return {'AVSzip': fields['zip'],
                'AVSaddress1': fields['address1'],
                'AVSaddress2': fields.get('address2', ''),
                'AVScity': fields['city'],
                'AVSstate': fields['state'],
                'AVSphoneNum': fields['phone'],
                'AVScountryCode': self.censor_countries(fields)}
    
    def build_order_authorization_request(self, authorization):
        return {'TxRefNum':authorization}
    
    def build_order_money_request(self, money):
        grandTotalAmount = '%.2f' % money.amount  #  CONSIDER  format AMOUNT like this better, everywhere
        grandTotalAmount = grandTotalAmount.replace('.', '')  #  CONSIDER internationalize that and respect the
        return {'CurrencyCode': money.currency.numeric,
                'CurrencyExponent': '2',
                'Amount': grandTotalAmount,}
    
    def build_create_card_store_request(self):
        return {'CustomerProfileFromOrderInd': 'A',
                'CustomerProfileOrderOverrideInd': 'NO',}
    
    def build_reversal_request(self, **kwargs):
        parts = {'BIN': '000001',
                 'MerchantID': kwargs['merchant_id'],
                 'TerminalID': '001',}
        parts.update(self.build_order_authorization_request(kwargs['authorization']))
        parts.update({'OrderID': str(kwargs.get('order_id', gencode()))})
        
        entries = list()
        #XML fields need to be in a certain order
        for key in self.REVERSAL_FIELDS:
            if key in parts:
                entries.append(getattr(XML, key)(parts[key]))
        
        new_order = XML.Reversal(*entries)
        return xStr(XML.Request(new_order))
    
    def build_capture_request(self, **kwargs):
        parts = {'BIN': '000001',
                 'MerchantID': kwargs['merchant_id'],
                 'TerminalID': '001',}
        if 'authorization' in kwargs:
            parts.update(self.build_order_authorization_request(kwargs['authorization']))
        if kwargs.get('credit_card'):
            parts.update(self.build_order_credit_card_request(kwargs['credit_card']))
        if 'address' in kwargs:
            parts.update(self.build_order_address_request(kwargs['address']))
        parts.update({'OrderID': str(kwargs.get('order_id', gencode()))})
        if 'money' in kwargs:
            parts.update(self.build_order_money_request(kwargs['money']))
        if kwargs.get('card_store_id'):
            parts.update({'CustomerRefNum':kwargs['card_store_id']})
        if kwargs.get('register_card_store', False):
            parts.update(self.build_create_card_store_request())
        
        entries = list()
        #XML fields need to be in a certain order
        for key in self.CAPTURE_FIELDS:
            if key in parts:
                entries.append(getattr(XML, key)(parts[key]))
        
        new_order = XML.MarkForCapture(*entries)
        return xStr(XML.Request(new_order))
    
    def build_order_request(self, message_type, **kwargs):
        parts = {'IndustryType': 'EC',  #  'EC'ommerce - a web buy
                 'MessageType': message_type,
                 'BIN': '000001',
                 'MerchantID': kwargs['merchant_id'],
                 'TerminalID': '001',}
        if 'authorization' in kwargs:
            parts.update(self.build_order_authorization_request(kwargs['authorization']))
        if kwargs.get('credit_card'):
            parts.update(self.build_order_credit_card_request(kwargs['credit_card']))
        if 'address' in kwargs:
            parts.update(self.build_order_address_request(kwargs['address']))
        if message_type in ('A', 'AC') or True: #CONSIDER order_id is always needed
            parts.update({'OrderID': str(kwargs.get('order_id', gencode()))})
        if 'money' in kwargs:
            parts.update(self.build_order_money_request(kwargs['money']))
        if kwargs.get('card_store_id'):
            parts.update({'CustomerRefNum':kwargs['card_store_id']})
        if kwargs.get('register_card_store', False):
            parts.update(self.build_create_card_store_request())
        
        entries = list()
        #XML fields need to be in a certain order
        for key in self.NEW_ORDER_FIELDS:
            if key in parts:
                entries.append(getattr(XML, key)(parts[key]))
        
        new_order = XML.NewOrder(*entries)
        return xStr(XML.Request(new_order))
    
    def build_profile_address_request(self, fields):
        return {'CustomerZIP': fields['zip'],
                'CustomerAddress1': fields['address1'],
                'CustomerAddress2': fields.get('address2', ''),
                'CustomerEmail': fields.get('email', ''),
                'CustomerCity': fields['city'],
                'CustomerState': fields['state'],
                'CustomerPhone': fields['phone'],
                'CustomerCountryCode': self.censor_countries(fields)}
    
    def build_profile_credit_card_request(self, credit_card):
        exp_code = ( '%02i' % credit_card.month) + str(credit_card.year)[-2:]
        return {'CCAccountNum': credit_card.number,
                'CCExpireDate': exp_code,
                'CustomerAccountType': 'CC',
                'CustomerName': credit_card.first_name + ' ' + credit_card.last_name,}
    
    def build_profile_request(self, message_type, **kwargs):
        parts = {'CustomerProfileAction': message_type, #CRUD
                 'CustomerBin': '000001',
                 'CustomerMerchantID': kwargs['merchant_id'],}
        if kwargs.get('credit_card'):
            parts.update(self.build_profile_credit_card_request(kwargs['credit_card']))
        if 'address' in kwargs:
            parts.update(self.build_profile_address_request(kwargs['address']))
        if message_type == 'C':
            parts.update(self.build_create_card_store_request())
        if kwargs.get('card_store_id'):
            parts.update({'CustomerRefNum':kwargs['card_store_id']})
        
        entries = list()
        #XML fields need to be in a certain order
        for key in self.PROFILE_FIELDS:
            if key in parts:
                entries.append(getattr(XML, key)(parts[key]))
        
        profile = XML.Profile(*entries)
        return xStr(XML.Request(profile))
    
    REVERSAL_FIELDS = ['OrbitalConnectionUsername',
			        'OrbitalConnectionPassword',
			        'TxRefNum',
			        'TxRefIdx',
			        'AdjustedAmt',
			        'OrderID',
			        'BIN',
			        'MerchantID',
			        'TerminalID',
			        'ReversalRetryNumber',
			        'OnlineReversalInd',]
    
    NEW_ORDER_FIELDS = ['OrbitalConnectionUsername',
			            'OrbitalConnectionPassword',
			            'IndustryType',
			            'MessageType',
			            'BIN',
			            'MerchantID',
			            'TerminalID',
			            'CardBrand',
			            'AccountNum',
			            'Exp',
			            'CurrencyCode',
			            'CurrencyExponent',
			            'CardSecValInd',
			            'CardSecVal',
			            'DebitCardIssueNum',
			            'DebitCardStartDate',
			            'BCRtNum',
			            'CheckDDA',
			            'BankAccountType',
			            'ECPAuthMethod',
			            'BankPmtDelv',
			            'AVSzip',
			            'AVSaddress1',
			            'AVSaddress2',
			            'AVScity',
			            'AVSstate',
			            'AVSphoneNum',
			            'AVSname',
			            'AVScountryCode',
			            'AVSDestzip',
			            'AVSDestaddress1',
			            'AVSDestaddress2',
			            'AVSDestcity',
			            'AVSDeststate',
			            'AVSDestphoneNum',
			            'AVSDestname',
			            'AVSDestcountryCode',
			            'CustomerProfileFromOrderInd',
			            'CustomerRefNum',
			            'CustomerProfileOrderOverrideInd',
			            'Status',
			            'AuthenticationECIInd',
			            'CAVV',
			            'XID',
			            'PriorAuthID',
			            'OrderID',
			            'Amount',
			            'Comments',
			            'ShippingRef',
			            'TaxInd',
			            'Tax',
			            'AMEXTranAdvAddn1',
			            'AMEXTranAdvAddn2',
			            'AMEXTranAdvAddn3',
			            'AMEXTranAdvAddn4',
			            'AAV',
			            'SDMerchantName',
			            'SDProductDescription',
			            'SDMerchantCity',
			            'SDMerchantPhone',
			            'SDMerchantURL',
			            'SDMerchantEmail',
			            'RecurringInd',
			            'EUDDCountryCode',
			            'EUDDBankSortCode',
			            'EUDDRibCode',
			            'BMLCustomerIP',
			            'BMLCustomerEmail',
			            'BMLShippingCost',
			            'BMLTNCVersion',
			            'BMLCustomerRegistrationDate',
			            'BMLCustomerTypeFlag',
			            'BMLItemCategory',
			            'BMLPreapprovalInvitationNum',
			            'BMLMerchantPromotionalCode',
			            'BMLCustomerBirthDate',
			            'BMLCustomerSSN',
			            'BMLCustomerAnnualIncome',
			            'BMLCustomerResidenceStatus',
			            'BMLCustomerCheckingAccount',
			            'BMLCustomerSavingsAccount',
			            'BMLProductDeliveryType',
			            'BillerReferenceNumber',
			            'MBType',
			            'MBOrderIdGenerationMethod',
			            'MBRecurringStartDate',
			            'MBRecurringEndDate',
			            'MBRecurringNoEndDateFlag',
			            'MBRecurringMaxBillings',
			            'MBRecurringFrequency',
			            'MBDeferredBillDate',
			            'MBMicroPaymentMaxDollarValue',
			            'MBMicroPaymentMaxBillingDays',
			            'MBMicroPaymentMaxTransactions',
			            'TxRefNum',
			            'PCOrderNum',
			            'PCDestZip',
			            'PCDestName',
			            'PCDestAddress1',
			            'PCDestAddress2',
			            'PCDestCity',
			            'PCDestState',
			            'PC3FreightAmt',
			            'PC3DutyAmt',
			            'PC3DestCountryCd',
			            'PC3ShipFromZip',
			            'PC3DiscAmt',
			            'PC3VATtaxAmt',
			            'PC3VATtaxRate',
			            'PC3AltTaxInd',
			            'PC3AltTaxAmt',
			            'PC3LineItemCount',
			            'PC3LineItemArray',
			            'PartialAuthInd',]
    
    CAPTURE_FIELDS = ["OrbitalConnectionUsername",
                      "OrbitalConnectionPassword",
                      "OrderID",
                    "Amount",
                    "TaxInd",
                    "Tax",
                    "BIN",
                    "MerchantID",
                    "TerminalID",
                    "TxRefNum",
                    "PCOrderNum",
                    "PCDestZip",
                    "PCDestName",
                    "PCDestAddress1",
                    "PCDestAddress2",
                    "PCDestCity",
                    "PCDestState",
                    "AMEXTranAdvAddn1",
                    "AMEXTranAdvAddn2",
                    "AMEXTranAdvAddn3",
                    "AMEXTranAdvAddn4",
                    "PC3FreightAmt",
                    "PC3DutyAmt",
                    "PC3DestCountryCd",
                    "PC3ShipFromZip",
                    "PC3DiscAmt",
                    "PC3VATtaxAmt",
                    "PC3VATtaxRate",
                    "PC3AltTaxInd",
                    "PC3AltTaxID",
                    "PC3AltTaxAmt",
                    "PC3LineItemCount",
                    "PC3LineItemArray",]
    
    PROFILE_FIELDS = ['OrbitalConnectionUsername',
			        'OrbitalConnectionPassword',
			        'CustomerBin',
			        'CustomerMerchantID',
			        'CustomerName',
			        'CustomerRefNum',
			        'CustomerAddress1',
			        'CustomerAddress2',
			        'CustomerCity',
			        'CustomerState',
			        'CustomerZIP',
			        'CustomerEmail',
			        'CustomerPhone',
			        'CustomerCountryCode',
			        'CustomerProfileAction',
			        'CustomerProfileOrderOverrideInd',
			        'CustomerProfileFromOrderInd',
			        'OrderDefaultDescription',
			        'OrderDefaultAmount',
			        'CustomerAccountType',
			        'Status',
			        'CCAccountNum',
			        'CCExpireDate',
			        'ECPAccountDDA',
			        'ECPAccountType',
			        'ECPAccountRT',
			        'ECPBankPmtDlv',
			        'SwitchSoloStartDate',
			        'SwitchSoloIssueNum',
			        'MBType',
			        'MBOrderIdGenerationMethod',
			        'MBRecurringStartDate',
			        'MBRecurringEndDate',
			        'MBRecurringNoEndDateFlag',
			        'MBRecurringMaxBillings',
			        'MBRecurringFrequency',
			        'MBDeferredBillDate',
			        'MBMicroPaymentMaxDollarValue',
			        'MBMicroPaymentMaxBillingDays',
			        'MBMicroPaymentMaxTransactions',
			        'MBCancelDate',
			        'MBRestoreBillingDate',
			        'MBRemoveFlag',
			        'EUDDCountryCode',
			        'EUDDBankSortCode',
			        'EUDDRibCode',
			        'SDMerchantName',
			        'SDProductDescription',
			        'SDMerchantCity',
			        'SDMerchantPhone',
			        'SDMerchantURL',
			        'SDMerchantEmail',
			        'BillerReferenceNumber',]


    def censor_countries(self, fields):
        permitted_country = fields['country']

        if permitted_country not in ('US', 'CA', 'UK', 'GB', ): # meanwhile, UK is neither United nor a Kingdom! C-;
            return ''

        return permitted_country
    
    def parse(self, soap):
        doc  = xmltodict(ET.fromstring(soap))
        response_type = doc.keys()[0]
        response = doc[response_type]
        response_class = {'NewOrderResp':self.NewOrderResponse,
                          'ProfileResp':self.ProfileResponse,
                          'QuickResp':self.QuickResponse,
                          'ReversalResp':self.ReversalResponse,
                          'MarkForCaptureResp':self.NewOrderResponse,}[response_type]
        return response_class(self, response)

    class NewOrderResponse(response.Response):
        def __init__(self, gateway, result):
            success  = result['ApprovalStatus'] == '1'
            message  = result.get('StatusMsg', '')
            authorization = result['TxRefNum']
            avs_resp_code = result.get('AVSRespCode', '') or ''
            response.Response.__init__(self, success, message, result,
                                       is_test=gateway.is_test,
                                       authorization=authorization,
                                       avs_result=avs_resp_code.strip(),
                                       cvv_result=result.get('CVV2RespCode', None),
                                       card_store_id=result.get('CustomerRefNum', None),)
    
    class ProfileResponse(response.Response):
        def __init__(self, gateway, result):
            success  = result['ProfileProcStatus'] == '0'
            message  = result['CustomerProfileMessage']
            response.Response.__init__(self, success, message, result,
                                       is_test=gateway.is_test,
                                       card_store_id=result.get('CustomerRefNum', None),)
    
    class QuickResponse(response.Response):
        def __init__(self, gateway, result):
            success  = False
            message  = result['StatusMsg']
            response.Response.__init__(self, success, message, result,
                                       is_test=gateway.is_test,)
    
    class ReversalResponse(response.Response):
        def __init__(self, gateway, result):
            success  = result['ProcStatus'] == '0'
            message  = result.get('StatusMsg', '')
            authorization = result['TxRefNum']
            response.Response.__init__(self, success, message, result,
                                       is_test=gateway.is_test,
                                       authorization=authorization,)

    def commit(self, request, **options):
        uri           = self.is_test and TEST_URL or LIVE_URL
        headers = self._generate_headers(request, **options)

        self._log(request)
        return self.parse(self.post_webservice(uri, request, headers))

    def _log(self, request):
        import re

        def replace_account_num_digits(x):
            return r'<AccountNum>%s</AccountNum>' % re.sub('\d', '9', x.groups('num')[0])

        message = re.sub(r'\<AccountNum\>(?P<num>.*)\<\/AccountNum\>', replace_account_num_digits, request)

        def replace_card_sec_val_digits(x):
            return r'<CardSecVal>%s</CardSecVal>' % re.sub('\d', '9', x.groups('num')[0])

        message = re.sub(r'\<CardSecVal\>(?P<num>.*)\<\/CardSecVal\>', replace_card_sec_val_digits, message)
        # print message

        logger = logging.getLogger('MerchantGateways')
        logger.debug(message)

    def _generate_headers(self, request, **options):
        return {
                  "MIME-Version": "1.0",
                  "Content-Type": "Application/PTI49", #  CONSIDER  why is this code here??
                  "Content-transfer-encoding": "text",  #  CONSIDER  nobody tests this, either...
                  "Request-number": "1",
                  "Document-type": "Request",
                  "Content-length": str(len(request)),
                  "Merchant-id": options['merchant_id']  #  CONSIDER  useful error message if it's not there
                  }
