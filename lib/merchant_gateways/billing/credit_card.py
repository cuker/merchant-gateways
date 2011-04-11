import re
from datetime import datetime

from merchant_gateways import MerchantGatewayError

#  CONSIDER the card should raise an error if the type is not understood
    #  CONSIDER  always credit_card never creditcard

class CreditCard(object):
    require_verification_value = True

    def __init__(self,
                 #essential attributes for valid, non-bogus creditcards
                 number, month, year, card_type=None, first_name=None, last_name=None,
                 # TODO required for Switch / Solo cards
                 start_month=None, start_year=None, issue_number=None,
                 #optional verification_value (CVV, CVV2, etc).
                 #Gateways will try to run validation on the passed in value if it is supplied
                 verification_value=None):
        self.number = re.sub('[^\d]', '', str(number))
        self.month = int(month)
        self.year = int(year)    #  CONSIDER  throw the correct error if the year is not a number
        self.first_name = first_name
        self.last_name = last_name
#        self.start_month = start_month
#        self.start_year = start_year
        self.issue_number = issue_number
        self.verification_value = verification_value
        self.card_type = card_type or self._lookup_card_type()  #  TODO  squeak if those two don't match up
        self.errors = dict()

#    #should be in mixin
#    @classmethod
#    def valid_number(cls, number):
#        return CreditCard.valid_test_mode_card_number(number) or \
#               CreditCard.valid_card_number_length(number) and \
#               Creditcard.valid_checksum(number)
#
#    @classmethod
#    def card_companies(cls):
#        return CreditCard.CARD_COMPANIES
#
#    # CONSIDER Refactor this method. We basically need to tighten up the Maestro Regexp.
#    #
#    # Right now the Maestro regexp overlaps with the MasterCard regexp (IIRC). If we can tighten
#    # things up, we can boil this whole thing down to something like...
#    #
#    # def type?(number)
#    # return 'visa' if valid_test_mode_card_number?(number)
#    # card_companies.find([nil]) { |type, regexp| number =~ regexp }.first.dup
#    # end
#    @classmethod
#    def check_card_type(cls, number):
#        '''
#        Returns a string containing the type of card from the list of known information below.
#        Need to check the cards in a particular order, as there is some overlap of the allowable ranges
#        '''
#        if CreditCard.valid_test_mode_card_number(number):
#            return 'bogus'
#
#        for company, pattern in CreditCard.card_companies():
#            if company == 'maestro':
#                continue
#            if re.match(pattern, number):
#                return company
#
#        if re.match(CreditCard.card_companies['maestro'], number):
#            return 'maestro'
#
#        return None
#
#    @classmethod
#    def last_digits(cls, number):
#        if len(str(number)) <= 4:
#            return number
#        return str(number)[-4:]
#
#    @classmethod
#    def mask(number):
#        return "XXXX-XXXX-XXXX-%s" % CreditCard.last_digits(number)
#
#    @classmethod
#    def matching_type(cls, number, given_type):
#        return CreditCard.check_card_type(number == given_type)
#
#    @classmethod
#    def valid_card_number_length(cls, number):
#        return len(str(number)) >= 12
#
#    @classmethod
#    def valid_test_mode_card_number(cls, number):
#        #ActiveMerchant::Billing::Base.test? &&   #not sure how to do this test yet...
#        return str(number) in ['1', '2', '3', 'success', 'failure', 'error']
#
#    @classmethod
#    def valid_checksum(cls, number):
#        sum = 0
#        for i in range(0, len(number) + 1):
#            weight = int(number[-1 * (i + 2)]) * (2 - (i %2))
#            if weight < 10:
#                sum += weight
#            else:
#                sum += weight - 9
#        return (int(number[-1]) == (10 - sum % 10) % 10)
#
#    def valid_month(self, month):
#        return month in range(1,13)
#
#    def valid_expiry_year(self, year):
#        return year in range(datetime.now().year, datetime.now().year + 21)
#
#    def valid_start_year(self, year):
#        return re.match(r'^\d{4}$', str(year)) and int(year) > 1987
#
#    def valid_issue_number(self, number):
#        if re.match(r'^\d{1,2}$', str(number)):
#            return True
#        return False
#    #end mixin
#
#    def expiry_date(self):
#        return ExpiryDate(self.month, self.year)
#
#    def is_expired(self):
#        return self.expiry_date().is_expired()
#
#    def has_name(self):
#        return self.first_name and self.last_name

    def _is_blank(self, svar):  #  TODO tdd this line
        if svar == None:
            return True
        return (not svar.strip() == '')

#    def has_first_name(self):
#        return self._is_blank(self.first_name.strip())
#
#    def has_last_name(self):
#        return self._is_blank(self.last_name.strip())

    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def has_verification_value(self):
        return self._is_blank(self.verification_value)    #  TODO tdd this line

#    def display_number(self):
#        return CreditCard.mask(self.number)
#
#    def last_digits(self):
#        return Creditcard.last_digits(self.number)
#
#    def validate(self):
#        self.validate_essential_attributes()
#
#        if self.card_type == 'bogus':
#            return
#
#        self.validate_card_type()
#        self.validate_card_number()
#        self.validate_verification_value()
#        self.validate_switch_or_solo_attributes()
#
#    def assert_attr(self, attr, errormsg, errorlist):
#        try:
#            assert attr,  errormsg
#        except AssertionError, msg:
#            errorlist.append(msg)
#
#    def mass_validation(self, attrs):
#        errors = []
#        for attr, errormsg in attrs:
#            self.assert_attr(attr, errormsg, errors)
#        if errors:
#            raise AssertionError, ', '.join(errors)
#
#    def validate_essential_attributes(self, errorlist):
#        self.mass_validation((
#            (self.has_first_name(), 'first name cannot be empty'),
#            (self.has_last_name(), 'last name cannot be empty'),
#            (self.has_valid_month(), '%s is not a valid month' % str(self.month)),
#            (self.is_expired(), 'card expired'),
#            (self.valid_expiry_year(), '%s is not a valid year' % self.year)
#        ))
#
#    def validate_card_number(self):
#        errors = []
#        self.assert_attr(self.has_valid_number(),
#                         "%s is not a valid credit card number" % str(self.number),
#                         errors)
#        if not errors:
#            self.assert_attr(self.matching_type(),
#                             "% sis not the correct card type" % str(self.card_type),
#                             errors)
#        if errors:
#            raise AssertionError, ', '.join(errors)
#
#    def validate_card_type(self):
#        self.mass_validation((
#            (self._is_blank(self.card_type()), "card type is required"),
#            (self.card_companies.has_key(self.card_type()), "card type is invalid")
#        ))
#
#    def validate_switch_or_solo_attributes(self):
#        if not self.card_type in ['switch', 'solo']:
#            return
#
#        self.mass_validation((
#            (CreditCard.valid_start_month(self.start_month),
#             "start month is invalid" % str(self.start_month)),
#            (CreditCard.valid_start_year(self.start_year),
#             "start year is invalid" % str(self.start_year)),
#            (Creditcard.valid_issue_number(self.number),
#             "issue number cannot be empty" % str(self.issue_number)),
#        ))
#
#    def validate_verification_value(self):
#        if self.does_require_verification_value():
#            self.mass_validation((
#                (self.has_verification_value(), "verification value is required"),
#            ))
#
#    def does_require_verification_value(self):
#        return self.require_verification_value

    def is_valid(self):  #  TODO  test each reason
        self.errors = dict()
        required = 'this field is required' #  TODO  translate me; use real Django validators
        if 0 == len(self.first_name):  self.errors['first_name'] = required
        if 0 == len(self.last_name) :  self.errors['last_name']  = required
        if not self.type_name():  self.errors['card_type'] = required
        return self.errors.values() == []
#
#        '''def valid_number(cls, number): TODO  pass self.number by default
#        def valid_card_number_length(cls, number):
#        def valid_test_mode_card_number(cls, number):
#        def valid_checksum(cls, number):
#        def valid_month(self, month):
#        def valid_expiry_year(self, year):
#        def valid_start_year(self, year):
#        def valid_issue_number(self, number):'''
#
#        '''  valid_month?(month)   TODO  vet against original Ruby methods
#             valid_expiry_year?(year)
#             valid_start_year?(year)
#             valid_issue_number?(number)
#             valid_number?(number)
#             valid_card_number_length?(number) #:nodoc:
#             valid_test_mode_card_number?(number) #:nodoc:
#             valid_checksum?(number) '''
#

    def type_name(self):
        types = dict(m='MasterCard',
                     v='Visa',
                     visa='Visa',
                     solo='Solo'
                    )
        return types.get(self.card_type.lower(), None)  #  TODO  handle rogue types correctly, etc.!

    def _lookup_card_type(self):
        for name, matcher in CARD_COMPANIES.items():
            if re.search(matcher, self.number):
                return name
        raise MerchantGatewayError, 'Unrecognized card type'

CARD_COMPANIES = {
    'visa': '^4\d{12}(\d{3})?$',
    'master': '^(5[1-5]\d{4}|677189)\d{10}$',
    'discover': '^(6011|65\d{2})\d{12}$',
    'american_express': '^3[47]\d{13}$',
    'diners_club': '^3(0[0-5]|[68]\d)\d{11}$',
    'jcb': '^3528\d{12}$',
    'switch': '^6759\d{12}(\d{2,3})?$',
    'solo': '^6767\d{12}(\d{2,3})?$',
    'dankort': '^5019\d{12}$',
    'maestro': '^(5[06-8]|6\d)\d{10,17}$',
    'forbrugsforeningen': '^600722\d{10}$',
    'laser': '^(6304[89]\d{11}(\d{2,3})?|670695\d{13})$'
}

