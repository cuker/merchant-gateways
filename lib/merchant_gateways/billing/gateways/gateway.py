
# note:

#   request - the project's outbound message to the gateway, in merchant-gateways format
#   params - TODO the request, translated into a hash ready to send as soap or something
#   result - the gateway's return message, translated from soap or something to a hash
#   response - the gateway's result, translated into merchant-gateways format, with values exposed as members

#  CONSIDER  exception handling, logging, conversation recording, signals for exceptions, success, & fail

from merchant_gateways.lib.post import post  #  CONSIDER  move me to gateway.py

class Gateway(object):
    DEBIT_CARDS = ('switch', 'solo')  #  TODO  use this
    CARD_STORE = False
    money_format = 'dollars'
    supported_cardtypes = []
    options = {}

    def __init__(self, **options):
        self.gateway_mode = options.get('gateway_mode', 'live') #the gateway we point to
        self.is_test = options.get('is_test', False) #the nature of the individual transactions
        self.options = options

    def supports(self, card_type):
        return (card_type in self.supported_cardtypes)

    def card_brand(self, source):
        return str(source.card_type).lower()
        try:
            result = source.brand  # TODO  use or lose all this
        except AttributeError:
            result = type(source)

        return str(result).lower()

#    def is_test(self):
 #       return self.gateway_mode == 'test'  TODO  also permit toast-tests

    def is_blank(self, val):
        if type(val) != type(''):
            return None
        return len(val.strip()) == 0

    def amount(self, money):
        if money is None:
            return None

        return '%.2f' % money.amount

    def currency(self, money):
        try:
            return money.currency
        except AttributeError:
            return self.default_currency

    def requires_start_date_or_issue_number(self, credit_card):  # TODO fully test this thing!
        if self.card_brand(credit_card).strip() == '':
            return False
        if self.card_brand(credit_card) in self.DEBIT_CARDS:
            return True
        return False
    
    def supports_action(self, action):
        if not hasattr(self, action): return False
        return getattr(getattr(self, action), 'supported', True)

    def authorize(self, money, credit_card, **kwargs):
        raise NotImplementedError
    authorize.supported = False

    def purchase(self, money, credit_card, **kwargs):
        raise NotImplementedError
    purchase.supported = False

    def capture(self, money, authorization, **kwargs):
        raise NotImplementedError
    capture.supported = False

    def void(self, authorization, **kwargs):
        raise NotImplementedError
    void.supported = False

    def credit(self, money, authorization, **kwargs):
        raise NotImplementedError
    credit.supported = False

    def recurring(self, money, credit_card, **kwargs):
        raise NotImplementedError
    recurring.supported = False

    def card_store(self, credit_card, **kwargs):
        raise NotImplementedError
    card_store.supported = False

    def unstore(self, indentification, **kwargs):
        raise NotImplementedError
    unstore.supported = False

    def require(self, kwargs_hash, *args):
        for arg in args:
            if not kwargs_hash.has_key(arg):
                raise ValueError('%s missing in gateway parameters' % arg)

    def setup_address_hash(self, **options):
        'Create all address hash key value pairs so that we still function if we were only provided with one or two of them'
        #TODO deprecate this as it only serves to allow people to be ambigious
        self.options = options # or self.options
        options['billing_address'] = options.get('billing_address', options.get('address', {}))
        options['shipping_address'] = options.get('shipping_address', {})
        return self.options  #  TODO options, results, message, param, etc ALL ARE ALWAYS MEMBERS

    def post_webservice(self, url, params, headers={}):   #  CONSIDER  get a better Mock library and this goes away! (otherwise, put it in the base class)
        got = post(url, params, headers)
        #  TODO  log(got) here!
        #print got
        return got
    
    def parse_address_from_post(self, post_data, prefix='bill'):
        address = {}
        value_found = False
        for key in ('first_name', 'last_name', 'address1', 'address2', 'city', 'state', 'country', 'zip', 'email'):
            f_key = prefix+"_"+key
            if f_key in post_data:
                value_found = True
            address[key] = post_data.get(f_key, None)
        if value_found:
            return address
        else:
            return None
    
    def process_direct_post(self, post_data, decrypted_data):
        #should return dict containing: response, credit_card, passthrough, amount, currency_code
        from merchant_gateways.billing.credit_card import CreditCard
        from money import Money
        
        amount = decrypted_data['amount']
        currency_code = decrypted_data['currency_code']
        money = Money(amount, currency_code)
        credit_card = CreditCard(number=post_data['cc_number'],
                                 month=post_data['cc_exp_month'],
                                 year=post_data['cc_exp_year'],
                                 first_name=post_data['bill_first_name'],
                                 last_name=post_data['bill_last_name'],
                                 verification_value=post_data['cc_ccv'],)
        options = decrypted_data.get('options', {})
        func = getattr(self, decrypted_data['action'])
        
        address = self.parse_address_from_post(post_data)
        if address:
            options['address'] = address
        ship_address = self.parse_address_from_post(post_data, prefix='ship')
        if ship_address:
            options['ship_address'] = ship_address
        
        response = func(money=money, credit_card=credit_card, **options)
        
        passthrough_fields = decrypted_data.get('passthrough', [])
        passthrough = {}
        for key in passthrough_fields:
            if key.startswith('cc_'):
                continue
            if key in post_data:
                passthrough[key] = post_data[key]
        
        return {'response':response,
                'credit_card':credit_card,
                'amount':amount,
                'currency_code':currency_code,
                'passthrough':passthrough,}

class default_dict(dict):  #  TODO  move to utils
    """
    A subclass of dictionary that returns '' instead of feebly
    attempting to spank the programmer if (shocked gasp) the key is not found
    """

    def set_default(self, default):
        self.default = default
        return self  #  for construction like default_dict(**dict).set_default(None)

    def __getitem__(self, key):
        default = getattr(self, 'default', '')  #  the irony IS lost on us...
        return self.get(key, default)


def xStr(doc):
    from lxml import etree
    return etree.tostring(doc, pretty_print=True)  #  TODO  take out pretty_print to go out wire!
