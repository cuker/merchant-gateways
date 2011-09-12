import re

from gateway import Gateway, default_dict
from merchant_gateways import MerchantGatewayError
from merchant_gateways.billing import response

from merchant_gateways.billing.common import xStr, ElementMaker, gencode
XML = ElementMaker()

# TODO use this      XMLNS = 'http://www.paypal.com/XMLPay'
# TODO  actually write a real post_webservice
# TODO  advise NB that active_merchant has braintree - of course!

def strip_to_numbers(number):
    """ remove spaces from the number """
    return re.sub('[^0-9]+', '', number)

class Payflow(Gateway):
    CARD_STORE = True
    TEST_URL = 'https://pilot-payflowpro.paypal.com'
    LIVE_URL = 'https://payflowpro.paypal.com'

    def authorize(self, money, credit_card=None, card_store_id=None, **options):
        if card_store_id:
            request = self.build_reference_sale_or_authorization_request('authorization', money, card_store_id, **options)
        else:
            request = self.build_credit_card_request('authorization', money, credit_card, **options)
        return self.commit(request)
    
    def purchase(self, money, credit_card=None, card_store_id=None, **options):
        if card_store_id:
            request = self.build_reference_sale_or_authorization_request('purchase', money, card_store_id, **options)
        else:
            request = self.build_credit_card_request('purchase', money, credit_card, **options)
        return self.commit(request)

    def void(self, authorization, **options):
        self.request = self.build_reference_request('void', None, authorization, **options)
        return self.commit(self.request)
    
    def credit(self, money, authorization, **options):
        request = self.build_reference_request('credit', money, authorization, **options)
        return self.commit(request)

    def capture(self, money, authorization, **options):
        request = self.build_reference_request('capture', money, authorization, **options)
        return self.commit(request)

    def commit(self, request_body, request_type = None):
        request = self.build_request(request_body, request_type)
        headers = self.build_headers(len(request))  #  TODO  glyph length or byte length???

        url = (self.gateway_mode == 'live') and self.LIVE_URL or self.TEST_URL
        result = self.parse(self.post_webservice(url, request, headers))

        # self.result = parse(ssl_post(test? ? TEST_URL : LIVE_URL, request, headers))'''

        passed = result['Result'] in ('0', '126')
        message = passed and 'Approved' or 'Declined'

        response = self.Response( passed, message, result,
            is_test=self.is_test,
            fraud_review= (result['Result'] == '126'),
            authorization=result.get('PNRef', result.get('RPRef', None)),  #  TODO  test the RPRef
            cvv_result = CVV_CODE[result.get('CvResult', None)],  #  TODO  default_dict to the rescue!
            avs_result = result.get('AvsResult', None),
            card_store_id = result.get('PNRef', None),
            )
        return response

    def build_headers(self, content_length):
        return {
          "Content-Type" : "text/xml",
          "Content-Length" : str(content_length),
          "X-VPS-Client-Timeout" : '30',  #  TODO  bfd?!
          "X-VPS-VIT-Integration-Product" : "TODO what's my name",
          "X-VPS-VIT-Runtime-Version" : '4.2',  #  TODO  what's my version?
          "X-VPS-Request-ID" : gencode(),
        }

    def build_request(self, request_body, request_type=None):  # TODO  what's the request_type for?
        template = '''<?xml version="1.0" encoding="UTF-8"?>
<XMLPayRequest Timeout="30" version="2.1"
xmlns="http://www.paypal.com/XMLPay">
  <RequestData>
    <Vendor>%(vendor)s</Vendor>
    <Partner>%(partner)s</Partner>
    <Transactions>
      <Transaction>
        <Verbosity>MEDIUM</Verbosity>
        %(request_body)s
      </Transaction>
    </Transactions>
  </RequestData>
  <RequestAuth>
    <UserPass>
      <User>%(user)s</User>
      <Password>%(password)s</Password>
    </UserPass>
  </RequestAuth>
</XMLPayRequest>
'''  #  TODO  vary all this data
        info = self.options.copy()
        info.setdefault('vendor', 'LOGIN')
        info.setdefault('user', 'LOGIN')
        info.setdefault('partner', 'PayPal')
        info.setdefault('password', 'PASSWORD')
        info['request_body'] = request_body
        return template % info

    def build_reference_sale_or_authorization_request(self, action, money, reference, **options): #TODO tdd this
        transaction_type = TRANSACTIONS[action]
        formatted_amount = '%.2f' % money.amount  #  TODO  rename to money; merge with grandTotalAmount system
        return xStr(
            XML(transaction_type,
                XML.PayData(
                    XML.Invoice(
                        XML.TotalAmt(formatted_amount, Currency=str(money.currency.code))
                    ),
                    XML.Tender(
                        XML.Card(
                            XML.ExtData(Name='ORIGID', Value=reference)
                        )
                    )
                )
            )
        )

    def build_credit_card_request(self, action, money, credit_card, **options):
        transaction_type = TRANSACTIONS[action]
          # amount=self.options['amount'] ) # TODO all options in options - no exceptions
        formatted_amount = '%.2f' % money.amount  #  TODO  rename to money; merge with grandTotalAmount system
        
        invoice = list()
        
        ip_address = options.get('ip_address', None)
        if ip_address:
            invoice.append(XML.CustIP(ip_address))
        
        bill_to_address = options.get('address', None)
        if bill_to_address:
            invoice.append(self.add_address('BillTo', **bill_to_address))
        
        ship_to_address = options.get('ship_address', None)
        if ship_to_address:
            invoice.append(self.add_address('ShipTo', **ship_to_address))
        
        invoice.append(XML.TotalAmt(formatted_amount, Currency=str(money.currency.code)))

        request = XML(transaction_type,
                    XML.PayData(
                      XML.Invoice(*invoice),
                      XML.Tender(
                          self.add_credit_card(credit_card)
                      )))
        return xStr(request)

    def add_address(self, _where_to, **address):
        if not address:  return ''
        address = default_dict(address)
        elements = list()
        elements.append(XML.Name(address['name']))
        if address.get('phone','').strip():
            #xxx-xxx-xxxx (US numbers) +xxxxxxxxxxx (international numbers)
            phone = strip_to_numbers(address['phone'])
            if len(phone) == 10 and address['country'] == 'US':
                phone = '%s-%s-%s' % (phone[0:3], phone[3:6], phone[6:10])
            else:
                phone = '+'+phone
            elements.append(XML.Phone(phone))
        if address.get('email', '').strip():
            elements.append(XML.EMail(address.get('email', '').strip()))
        elements.append(XML.Address(
                              XML.Street(address['address1']),
                              XML.City(address['city']),
                              XML.State(address['state']),
                              XML.Country(address['country']),
                              XML.Zip(address['zip'])))
        return XML(_where_to, *elements)

    class Response(response.Response):
        pass

    def parse(self, data):  #  TODO  use self.message
        response = {}
        from lxml import etree
        xml = etree.XML(data)
        namespaces={'paypal':'http://www.paypal.com/XMLPay'}
        root = xml.xpath('..//paypal:TransactionResult', namespaces=namespaces)[0]
        for node in root.xpath('*', namespace='paypal', namespaces=namespaces):
            response[node.tag.split('}')[-1]] = node.text
        if response.get('Result') not in ('0', '126'):
            raise MerchantGatewayError(response.get('Message', 'No error message given'), response)
        '''
        root = REXML::XPath.first(xml, "//ResponseData")

        # REXML::XPath in Ruby 1.8.6 is now unable to match nodes based on their attributes
        tx_result = REXML::XPath.first(root, "//TransactionResult")

        if tx_result && tx_result.attributes['Duplicate'] == "true"
          response[:duplicate] = true
        end

        root.elements.to_a.each do |node|
          parse_element(response, node)  #  TODO  so what?
        end'''

        return response

    def add_credit_card(self, credit_card):

        fields = [  XML.CardType(self.credit_card_type(credit_card)),  #  TODO  test all types
                    XML.CardNum(credit_card.number),
                    XML.ExpDate(self.expdate(credit_card)),
                    XML.NameOnCard(credit_card.name()),
                    XML.CVNum(credit_card.verification_value), # TODO if credit_card.verification_value?
                    XML.ExtData(Name='LASTNAME', Value=credit_card.last_name) ]

        if self.requires_start_date_or_issue_number(credit_card):  #  TODO  TDD
            issue = format(credit_card.issue_number, two_digits=True)
            fields.append(XML.ExtData(Name='CardIssue', Value=issue)) # TODO  unless credit_card.start_month.blank? || credit_card.start_year.blank?

                #  TODO  format(credit_card.issue_number, :two_digits))

        return XML.Card(*fields)
#          xml.tag! 'ExpDate', expdate(credit_card)
#          xml.tag! 'NameOnCard', credit_card.first_name
#          xml.tag! 'CVNum', credit_card.verification_value if credit_card.verification_value?
#
#          if requires_start_date_or_issue_number?(credit_card)
#            xml.tag!('ExtData', 'Name' => 'CardStart', 'Value' => startdate(credit_card)) unless credit_card.start_month.blank? || credit_card.start_year.blank?
#            xml.tag!('ExtData', 'Name' => 'CardIssue', 'Value' => format(credit_card.issue_number, :two_digits)) unless credit_card.issue_number.blank?
#          end
#          xml.tag! 'ExtData', 'Name' => 'LASTNAME', 'Value' =>  credit_card.last_name

    def credit_card_type(self, credit_card):
        if self.card_brand(credit_card) in [None, '']:  return ''
        return CARD_MAPPING.get(self.card_brand(credit_card), '')

    def expdate(self, credit_card):
        year  = "%.4i" % credit_card.year
        month = "%.2i" % credit_card.month
        return year + month

    def build_reference_request(self, action, money, authorization):
        return xStr(
            XML(TRANSACTIONS[action],
                XML.PNRef(authorization),
                *self.invoice_total_amt(money)
                )
            )

    def invoice_total_amt(self, money):
        if not money:  return []

        return [
                XML.Invoice(
                        XML.TotalAmt( '%.2f' % money.amount, #  TODO currency-specific template!
                                      Currency=str(money.currency.code) ) )
        ]

TRANSACTIONS = dict(
        purchase       = 'Sale',
        authorization  = 'Authorization',
        capture        = 'Capture',
        void           = 'Void',
        credit         = 'Credit'
      )

CARD_MAPPING = dict(
        visa='Visa',
        master='MasterCard',
        discover='Discover',
        american_express='Amex',
        jcb='JCB',
        diners_club='DinersClub',
        switch='Switch',
        solo='Solo',
        v='Visa',
        m='MasterCard',
        d='Discover',
        ax='Amex',
        dx='DinersClub',
        sw='Switch',
        s='Solo',
      )

CVV_CODE = {
        'Match'                 : 'M',
        'No Match'              : 'N',
        'Service Not Available' : 'U',
        'Service not Requested' : 'P',
        None: None
      }  #  TODO  test all these!

def format(number, **options):  #  TODO  move to credit_card_formatting!
    if number in [None, '']:  return ''
    last = ('000000000000000000000000000000' + str(number))[-2:]
    return last

