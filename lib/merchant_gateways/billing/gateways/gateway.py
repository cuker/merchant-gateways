
# note:

#   request - the project's outbound message to the gateway, in merchant-gateways format
#   params - TODO the request, translated into a hash ready to send as soap or something
#   result - the gateway's return message, translated from soap or something to a hash
#   response - the gateway's result, translated into merchant-gateways format, with values exposed as members

#  CONSIDER  exception handling, logging, conversation recording, signals for exceptions, success, & fail

from money import Money  #  TODO  add cuker/python-money to the requirements


class Gateway(object):
    DEBIT_CARDS = ('switch', 'solo')  #  TODO  use this
    money_format = 'dollars'
    supported_cardtypes = []
    options = {}

    def __init__(self, **options):
        self.gateway_mode = options.get('gateway_mode', 'live')
        self.is_test = options.get('is_test', False)
        self.options = options

    def supports(self, card_type):
        return (card_type in self.supported_cardtypes)

    def card_brand(self, source):
        return source.card_type
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

    def currency(money):
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

    def authorize(self, money, creditcard, **kwargs):
        raise NotImplementedError

    def purchase(self, money, creditcard, **kwargs):
        raise NotImplementedError

    def capture(self, money, authorization, **kwargs):
        raise NotImplementedError

    def void(self, identification, **kwargs):
        raise NotImplementedError

    def credit(self, money, identification, **kwargs):
        raise NotImplementedError

    def recurring(self, money, creditcard, **kwargs):
        raise NotImplementedError

    def store(self, creditcard, **kwargs):
        raise NotImplementedError

    def unstore(self, indentification, **kwargs):
        raise NotImplementedError

    def require(self, kwargs_hash, *args):
        for arg in args:
            if not kwargs_hash.has_key(arg):
                raise ValueError('%s missing in gateway parameters' % arg)

    def setup_address_hash(self, **options):
        'Create all address hash key value pairs so that we still function if we were only provided with one or two of them'

        self.options = options # or self.options
        options['billing_address'] = options.get('billing_address', options.get('address', {}))
        options['shipping_address'] = options.get('shipping_address', {})
        return self.options  #  TODO options, results, message, param, etc ALL ARE ALWAYS MEMBERS

    def post_webservice(self, url, params):   #  CONSIDER  get a better Mock library and this goes away! (otherwise, put it in the base class)
        return post(url, {})


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
