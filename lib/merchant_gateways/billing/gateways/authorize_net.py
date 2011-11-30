
from gateway import Gateway
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from money import Money  #  CONSIDER  multiple currencies in AuthorizeNet - no exceptions!

from urllib import urlencode
import re

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET  #  CONSIDER  give a darn about this library??

import re
from merchant_gateways.lib.post import post  #  CONSIDER  move me to gateway.py
from merchant_gateways.billing import response
from merchant_gateways.billing.gateways.gateway import default_dict

# TODO learn & steal from bitbucket.org/adroll/authorize

# For more information on the Authorize.Net Gateway please visit their {Integration Center}[http://developer.authorize.net/]

# The login and password are not the username and password you use to
# login to the Authorize.Net Merchant Interface. Instead, you will
# use the API Login ID as the login and Transaction Key as the
# password.
#
# ==== How to Get Your API Login ID and Transaction Key
#
# 1. Log into the Merchant Interface
# 2. Select Settings from the Main Menu
# 3. Click on API Login ID and Transaction Key in the Security section
# 4. Type in the answer to the secret question configured on setup
# 5. Click Submit
#
# ==== Automated Recurring Billing (ARB)
#
# Automated Recurring Billing (ARB) is an optional service for submitting and managing recurring, or
# subscription-based, transactions.
#
# To use recurring, update_recurring, and cancel_recurring ARB must be enabled for your account.
#
# Information about ARB is available on the {Authorize.Net website}[http://www.authorize.net/solutions/merchantsolutions/merchantservices/automatedrecurringbilling/].
# Information about the ARB API is available at the {Authorize.Net Integration Center}[http://developer.authorize.net/]

class AuthorizeNet(Gateway):
    API_VERSION = '3.1'

    APPROVED, DECLINED, ERROR, FRAUD_REVIEW = 1, 2, 3, 4
    RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT = 0, 2, 3
    AVS_RESULT_CODE, TRANSACTION_ID, CARD_CODE_RESPONSE_CODE = 5, 6, 38
    test_url = "https://test.authorize.net/gateway/transact.dll"
    live_url = "https://secure.authorize.net/gateway/transact.dll"

#    arb_test_url = 'https://apitest.authorize.net/xml/v1/request.api'
#    arb_live_url = 'https://api.authorize.net/xml/v1/request.api'
#    RECURRING_ACTIONS = {  CONSIDER
#      u'create': 'ARBCreateSubscription',
#      u'update': 'ARBUpdateSubscription',
#      u'cancel': 'ARBCancelSubscription'
#    }

    supported_countries = ['US']
    supported_cardtypes = ['visa', 'master', 'american_express', 'discover']
    homepage_url = 'http://www.authorize.net/'
    display_name = u'Authorize.Net'

    CARD_CODE_ERRORS = ('N', 'S')
    AVS_ERRORS = ('A', 'E', 'N', 'R', 'W', 'Z')

    AUTHORIZE_NET_ARB_NAMESPACE = 'AnetApi/xml/v1/schema/AnetApiSchema.xsd'

    def __init__(self, gateway_mode='live', **options):
        assert(options.has_key('login'))
        assert(options.has_key('password'))
        super(AuthorizeNet, self).__init__(gateway_mode=gateway_mode, **options)
        assert(self.options.has_key('login'))
        assert(self.options.has_key('password'))

    def authorize(self, money, creditcard, **options):
        """Performs an authorization, which reserves the funds on the customer's credit card, but does not charge the card.

       Parameters
       * money -- The amount to be authorized. Either an Integer value in cents or a Money object.
       * creditcard -- The CreditCard details for the transaction.
       * options-- A hash of optional parameters.
        """

        assert isinstance(money, Money), 'TODO  always pass in a Money object - no exceptions!'
        #self.order_id = options['order_id']  #  TODO put the order_id inside the options and only use it there. The order_id is just to require it
        post = {}
        self.options.update(options)  #  TODO  everyone does it like this
        # TODO self.options = options
        self.add_invoice(post, **options)
        self.add_creditcard(post, creditcard)
        self.add_address(post, **options)
        self.add_customer_data(post,options)
        #  TODO  merge passed options & self.options

        return self.commit('AUTH_ONLY', money, post)

    class Response(response.Response):
        pass

    def purchase(self, money, creditcard, **options):
        """Perform a purchase, which is essentially an authorization and capture in a single operation.

          Parameters

          * money -- The amount to be purchased. Either an Integer value in cents or a Money object.
          * creditcard -- The CreditCard details for the transaction.
          * options -- A hash of optional parameters."""
        #self.order_id = options['order_id']
        post = {
          'login': self.options['login'],
          'trans_id': self.options['password']
        }

        self.add_invoice(post, **options)
        self.add_creditcard(post, creditcard)
        self.add_address(post, **options)
        self.add_customer_data(post, options)

        return self.commit('AUTH_CAPTURE', money, post)

      # Captures the funds from an authorized transaction.
      #
      # ==== Parameters
      #
      # * <tt>money</tt> -- The amount to be captured. Either an Integer value in cents or a Money object.
      # * <tt>authorization</tt> -- The authorization returned from the previous authorize request.
    def capture(self, money, authorization, options = {}, order_id=None): # FIXME  this MUST use **options!!!
        post = {'trans_id': authorization}
        self.add_customer_data(post, options)
        return self.commit('PRIOR_AUTH_CAPTURE', money, post)

      # Void a previous transaction
      #
      # ==== Parameters
      #
      # * <tt>authorization</tt> - The authorization returned from the previous authorize request.
    def void(self, authorization, options = {}):
        post = {'trans_id': authorization}
        return self.commit('VOID', None, post)


      # Credit an account.
      #
      # This transaction is also referred to as a Refund and indicates to the gateway that
      # money should flow from the merchant to the customer.
      #
      # ==== Parameters
      #
      # * <tt>money</tt> -- The amount to be credited to the customer. Either an Integer value in cents or a Money object.
      # * <tt>identification</tt> -- The ID of the original transaction against which the credit is being issued.
      # * <tt>options</tt> -- A hash of parameters.
      #
      # ==== Options
      #
      # * <tt>:card_number</tt> -- The credit card number the credit is being issued to. (REQUIRED)
    def credit(self, money, identification, **options):
        #requires!(options, :card_number)
        assert('card_number' in options)  #  CONSIDER  how to credit a transaction?

        post = dict( trans_id= identification,
                     card_num= options['card_number'] )

        self.add_invoice(post, **options)
        return self.commit('CREDIT', money, post)

    def commit(self, action, money, parameters):
        if not action == 'VOID':
            parameters['amount'] = self.amount(money)

        # Only activate the test_request when the :test option is passed in
        parameters['test_request'] = self.is_test and 'TRUE' or 'FALSE'

        #url = test? ? self.test_url : self.live_url
        url = self.is_test and self.test_url or self.live_url  #  TODO  api_uri()

        url = url + self.post_data(action, parameters)

        # data = post(url, {})
        self.result = self.post_webservice(url, {})  #  TODO  post or get?
        self.response = self.parse(self.result)
        self.message = self.message_from(self.response)

        # Return the response. The authorization can be taken out of the transaction_id
        # Test Mode on/off is something we have to parse from the response text.
        # It usually looks something like this
        #
        # (TESTMODE) Successful Sale

        pattern = re.compile('TESTMODE')

        test_mode = self.is_test or pattern.search(self.message)

        #test_mode = test? || message =~ /TESTMODE/

        r = AuthorizeNet.Response(self.is_success(self.response), self.message, self.response,  #  TODO -> result!!!
                is_test=self.is_test,
                authorization=self.response['transaction_id'],
                fraud_review=self.is_fraud_review(self.response),
                avs_result=self.response['avs_result_code'],
                cvv_result=self.response['card_code']
                )  #  TODO  also pass the options in
        self.response = r
        return r

    def is_success(self, response):
        return response['response_code'] == self.APPROVED

    def is_fraud_review(self, response):
        return response['response_code'] == self.FRAUD_REVIEW

    def parse(self, body):
        fields = [ re.sub(r'^\$', '', re.sub(r'\$$', '', f)) for f in body.split(',') ]

        results = dict(
            response_code=    int(fields[self.RESPONSE_CODE]),
            response_reason_code= fields[self.RESPONSE_REASON_CODE],
            response_reason_text= fields[self.RESPONSE_REASON_TEXT],
            avs_result_code=      fields[self.AVS_RESULT_CODE],
            transaction_id=       fields[self.TRANSACTION_ID],
            card_code=            fields[self.CARD_CODE_RESPONSE_CODE]
            )
        return results

    def post_data(self, action, parameters = {}):  #  TODO  **
        #print repr(action)
        #print repr(parameters)
        post = {}

        post['version'] = self.API_VERSION
        post['login'] = self.options['login']
        post['tran_key'] = self.options['password']
        post['relay_response'] = "FALSE"
        post['type'] = action
        post['delim_data'] = "TRUE"
        post['delim_char'] = ","
        post['encap_char'] = "$"

        post.update(parameters)
        #request = post.merge(parameters).collect { |key, value| "x_#{key}=#{CGI.escape(value.to_s)}" }.join("&")
        request = {}
        [request.setdefault('x_' + key, value) for key, value in post.iteritems()]
        #print '?' + urlencode(request)
        return '?' + urlencode(request)

    def add_invoice(self, post, **options):
        post['invoice_num'] = options.get('order_id', '')
        post['description'] = options.get('description', '')

    def add_creditcard(self, post, creditcard):
        post['card_num'] = creditcard.number
        if creditcard.has_verification_value():
            post['card_code'] = creditcard.verification_value
        post['exp_date'] = self.expdate(creditcard)
        post['first_name'] = creditcard.first_name
        post['last_name'] = creditcard.last_name

    def add_customer_data(self, post, options):
        if 'email' in options:
            post['email'] = options['email']
            post['email_customer'] = false

        if 'customer' in options:
            post['cust_id'] = options['customer']

        if 'ip' in options:
            post['customer_ip'] = options['ip']

    def add_address(self, post, **options):
        address = None
        if 'billing_address' in options:  #  TODO  use get
            address = options['billing_address']
        elif 'address' in options:
            address = options['address']
        if address:
            address = default_dict(address)
            post['address'] = str(address['address1'])
            post['company'] = str(address['company'])
            post['phone'] = str(address['phone'])
            post['zip'] = str(address['zip'])
            post['city'] = str(address['city'])
            post['country'] = str(address['country'])
            if self.is_blank(address['state']):
                post['state'] = 'n/a'
            else:
                post['state'] = address['state']

    def normalize(field):
        'Make a python type out of the response string'
        try:
            return {'true': True,
                    'false': False,
                    '': None,
                    'null': None}[field]
        except KeyError:
            return field

    def message_from(self, results):
        if results['response_code'] == self.DECLINED:
            if results['card_code'] in self.CARD_CODE_ERRORS:
                return CVVResult.messages[ results['card_code'] ]
            if results['avs_result_code'] in self.AVS_ERRORS:
                return AVSResult.messages[ results['avs_result_code'] ]

        if results['response_reason_text'] == None:
            return ''
        else:
            return results['response_reason_text'][0:-1]

    def expdate(self, creditcard):
        year = "%.4d" % creditcard.year
        month = "%.2d" % creditcard.month
        return '%s%s' % (month, year[-2:])

    def recurring(self, money, creditcard, **kwargs):
        '''
        Create a recurring subscription with Authorize.net ARB
        and return a dictionary with keys and values representing
        the elements of the ARB Response.
        '''
        assert(kwargs.has_key('interval') and
               kwargs.has_key('duration') and
               kwargs.has_key('billing_address'))
        assert(kwargs['interval'].has_key('length') and
               kwargs['interval'].has_key('unit'))
        assert(kwargs['interval']['unit'] == 'days' or
               kwargs['interval']['unit'] == 'months')
        assert(kwargs['duration'].has_key('start_date') or
               kwargs['duration'].has_key('occurrences'))
        assert(kwargs['billing_address'].has_key('first_name') or
               kwargs['billing_address'].has_key('last_name'))

        #Create a copy of kwargs and call it options. This is not
        #intended to be self.options. ARB has different options
        #than the standard Authorize.Net payment gateway
        options = kwargs.copy()
        options['credit_card'] = creditcard
        options['amount'] = money

        request = self.build_recurring_request(u'create', options)
        return self.recurring_commit(u'create', request)

    def update_recurring(self, money, creditcard, **kwargs):
        '''
        Update an existing subscription with ARB. This requires
        the subscriptionId for the subscription being updated.
        The subscriptionId is returned after a successful call
        to the "recurring" method.
        '''
        assert(kwargs.has_key('subscription_id'))

        #Create a copy of kwargs and call it options. This is not
        #intended to be self.options. ARB has different options
        #than the standard Authorize.Net payment gateway
        options = kwargs.copy()
        options['credit_card'] = creditcard
        options['amount'] = money

        request = self.build_recurring_request(u'update', options)
        return self.recurring_commit(u'update', request)

    def cancel_recurring(self, subscription_id):
        '''
        Cancel an existing subscription with ARB. This requires
        the subscriptionId for the subscription being canceled.
        The subscriptionId is returned after a successful call
        to the "recurring" method.
        '''
        request = self.build_recurring_request('cancel', {'subscription_id': subscription_id})
        return self.recurring_commit(u'cancel', request)


    def build_recurring_request(self, action, options):
        '''
        Create an XML Request for communication with ARB. This method
        works for all actions: create, update, and cancel.
        '''
        if not self.RECURRING_ACTIONS.has_key(action):
            raise StandardError, u"Invalid Automated Recurring Billing Action: " + unicode(action)

        requestbuff = StringIO()

        requestbuff.write('<?xml version="1.0" encoding="utf-8"?>')
        root = ET.Element(self.RECURRING_ACTIONS[action] + 'Request',
                          attrib={'xmlns': self.AUTHORIZE_NET_ARB_NAMESPACE})
        self.add_arb_merchant_authentication(root)
        if options.has_key('ref_id'):
            refId = ET.SubElement(root, 'refId')
            refId.text = options['ref_id']
        {'create': self.build_arb_create_subscription_request,
         'update': self.build_arb_update_subscription_request,
         'cancel': self.build_arb_cancel_subscription_request
        }[action](root, options)

        tree = ET.ElementTree(root)
        tree.write(requestbuff)

        return requestbuff.getvalue()

    def add_se(self, node, name, text):
        '''
        A helper method for adding a subnode to an ElementTree node
        '''
        subnode = ET.SubElement(node, name)
        subnode.text = text
        return subnode

    def add_arb_merchant_authentication(self, root):
        merch_auth = ET.SubElement(root, 'merchantAuthentication')
        self.add_se(merch_auth, 'name', self.options['login'])
        self.add_se(merch_auth, 'transactionKey', self.options['password'])

    def build_arb_create_subscription_request(self, root, options):
        self.add_arb_subscription(root, options)

    def build_arb_update_subscription_request(self, root, options):
        subscription_id = self.add_se(root, 'subscriptionId', options['subscription_id'])
        self.add_arb_subscription(root, options)

    def build_arb_cancel_subscription_request(self, root, options):
        self.add_se(root, 'subscriptionId', options['subscription_id'])

    def add_arb_subscription(self, root, options):
        subscription = ET.SubElement(root, 'subscription')
        if options.has_key('subscription_name'):
            self.add_se(subscription, 'name', options['subscription_name'])
        self.add_arb_payment_schedule(subscription, options)
        if options.has_key('amount'):
            self.add_se(subscription, 'amount', self.amount(options['amount']))
        if options.setdefault('trial', None) and options['trial'].setdefault('amount', 0):
            self.add_se(subscription, 'trailAmount', options['trial']['amount'])
        self.add_arb_payment(subscription, options)
        self.add_arb_order(subscription, options)
        self.add_arb_customer(subscription, options)
        self.add_arb_address(subscription, 'billTo', options['billing_address'])
        if 'shipping_address' in options.keys():
            self.add_arb_address(subscription, 'shipTo', options['shipping_address'])

    def add_arb_interval(self, payment_schedule, options):
        if not 'interval' in options.keys() or not options['interval']:
            return
        interval = ET.SubElement(payment_schedule, 'interval')
        self.add_se(interval, 'length', options['interval']['length'])
        self.add_se(interval, 'unit', options['interval']['unit'])

    def add_arb_duration(self, payment_schedule, options):
        if not 'duration' in options.keys() or not options['duration']:
            return
        self.add_se(payment_schedule, 'startDate', options['duration']['start_date'])
        self.add_se(payment_schedule, 'totalOccurrences', options['duration']['occurrences'])

    def add_arb_payment_schedule(self, subscription, options):
        if 'interval' in options.keys() or 'duration' in options.keys():
            payment_schedule = ET.SubElement(subscription, 'paymentSchedule')
            self.add_arb_interval(payment_schedule, options)
            self.add_arb_duration(payment_schedule, options)
            if 'trial' in options.keys() and options['trial']:
                self.add_se(payment_schedule, 'trialOccurrences', options['trial']['occurrences'])

    def add_arb_payment(self, subscription, options):
        #if not 'credit_card' in options.keys() or 'bank_account' in options.keys():
        #    return
        payment = ET.SubElement(subscription, 'payment')
        self.add_arb_credit_card(payment, options)
        self.add_arb_bank_account(payment, options)

    def add_arb_credit_card(self, payment, options):
        if not 'credit_card' in options.keys() or not options['credit_card']:
            return
        credit_card = ET.SubElement(payment, 'creditCard')
        self.add_se(credit_card, 'cardNumber', options['credit_card'].number)
        self.add_se(credit_card, 'expirationDate', self.arb_expdate(options['credit_card']))

    def add_arb_bank_account(self, payment, options):
        if not 'bank_account' in options.keys() or not options['bank_account']:
            return
        bank_account = ET.SubElement(payment, 'bankAccount')
        self.add_se(bank_account, 'accountType', options['bank_account']['account_type'])
        self.add_se(bank_account, 'routingNumber', options['bank_account']['routing_number'])
        self.add_se(bank_account, 'accountNumber', options['bank_account']['account_number'])
        self.add_se(bank_account, 'nameOfAccount', options['bank_account']['name_of_account'])
        if 'bank_name' in options['bank_account'].keys():
            self.add_se(bank_account, 'bankName', options['bank_account']['bank_name'])
        self.add_se(bank_account, 'echeckType', options['bank_account']['echeck_type'])

    def add_arb_order(self, root, options):
        if not 'order' in options.keys() or not options['order']:
            return
        order = ET.SubElement(root, 'order')
        self.add_se(order, 'invoiceNumber', options['order']['invoice_number'])
        self.add_se(order, 'description', options['order']['description'])

    def add_arb_customer(self, root, options):
        if not 'customer' in options.keys() or not options['customer']:
            return
        customer = ET.SubElement(root, 'customer')
        if 'type' in options['customer'].keys():
            self.add_se(customer, 'type', options['customer']['type'])
        if 'id' in options['customer'].keys():
            self.add_se(customer, 'id', options['customer']['id'])
        if 'email' in options['customer'].keys():
            self.add_se(customer, 'email', options['customer']['email'])
        if 'phone_number' in options['customer'].keys():
            self.add_se(customer, 'phoneNumber', options['customer']['phone_number'])
        if 'fax_number' in options['customer'].keys():
            self.add_se(customer, 'faxNumber', options['customer']['fax_number'])
        self.add_arb_drivers_license(customer, options)
        if 'tax_id' in options['customer'].keys():
            self.add_se(customer, 'taxId', options['customer']['tax_id'])

    def add_arb_drivers_license(self, customer, options):
        if not 'customer' in options.keys() or not options['customer']:
            return
        if not 'drivers_license' in options['customer'].keys() or not options['customer']['drivers_license']:
            return
        drivers_license = ET.SubElement(customer, 'driversLicense')
        self.add_se(drivers_license, 'number', options['drivers_license']['number'])
        self.add_se(drivers_license, 'state', options['drivers_license']['state'])
        self.add_se(drivers_license, 'dateOfBirth', options['drivers_license']['date_of_birth'])

    def add_arb_address(self, root, container_name, address):
        if not address.keys():
            return
        container = ET.SubElement(root, container_name)
        self.add_se(container, 'firstName', address['first_name'])
        self.add_se(container, 'lastName', address['last_name'])

        if 'company' in address.keys():
            self.add_se(container, 'company', address['company'])
        if 'address1' in address.keys():
            self.add_se(container, 'address', address['address1'])
        if 'city' in address.keys():
            self.add_se(container, 'city', address['city'])
        if 'state' in address.keys():
            self.add_se(container, 'state', address['state'])
        if 'zip' in address.keys():
            self.add_se(container, 'zip', address['zip'])
        if 'country' in address.keys():
            self.add_se(container, 'country', address['country'])

    def arb_expdate(self, credit_card):
        return "%04d-%02d" % (credit_card.year, credit_card.month)

    def recurring_commit(self, action, request):
        if self.is_test:
            url = self.arb_test_url
        else:
            url = self.arb_live_url
        xml = post(url, request, {"Content-Type": "text/xml"})
        response = self.recurring_parse(action, xml)
        return response

    def normalize(self, name):
        if name[0] == "{":
            uri, tag = name[1:].split("}")
            return tag
        else:
            return name

    def recurring_parse(self, action, xml):
        response = {}
        xml = ET.parse(StringIO(xml))
        root = xml.getroot()
        root_tag = self.normalize(root.tag)

        if root_tag == "%sResponse"%(self.RECURRING_ACTIONS[action]) or root_tag == "ErrorResponse":
            response[root_tag] = True
            for child in root.getchildren():
                self.recurring_parse_element(response, child)

        return response

    def recurring_parse_element(self, response, node):
        if node.getchildren():
            for child in node.getchildren():
                self.recurring_parse_element(response, child)
        else:
            response[self.normalize(node.tag)] = node.text
