from tests.test_helper import *
from merchant_gateways.billing.credit_card import CreditCard


class CreditCardTest(MerchantGatewaysUtilitiesTestSuite):

    def setUp(self):
        CreditCard.require_verification_value = False
        self.visa = self.credit_card("4779139500118580",   card_type="visa")
        self.solo = self.credit_card("676700000000000000", card_type="solo", issue_number='01')

    def credit_card(self, number = '4242424242424242', **options):  #  TODO  reformat


       #  TODO  use this in every test that whips out a credit card
       import datetime
       one_year_hence = datetime.datetime.now() - datetime.timedelta(days=366)

       defaults = dict(
                number=number,
                month=9,
                #year='2090',
                year=one_year_hence.year,
                first_name='Longbob',
                last_name='Longsen',
                verification_value='123',
                card_type='visa'
                )
       defaults.update(options)

       return CreditCard(**defaults)

    def assert_valid(self, validateable):
         self.assertTrue(validateable.is_valid())  #  uh...

    def deny_valid(self, validateable):
         self.assertFalse(validateable.is_valid())  #  uh...

    def test_constructor_should_properly_assign_values(self):
        c = self.credit_card()

        self.assert_equal( "4242424242424242", c.number)
        self.assert_equal( 9, c.month)
     # TODO   self.assert_equal( Time.now.year + 1, c.year)
        self.assert_equal( "Longbob Longsen", c.name())  # TODO  fullname
        self.assert_equal("visa", c.card_type)
        self.assert_valid(c)

    '''def test_new_credit_card_should_not_be_valid
    c = CreditCard.new

    assert_not_valid c
    assert_false     c.errors.empty?'''

    def test_sample_cards_are_valid(self):
        self.assert_valid(self.visa)
        self.assert_equal({}, self.visa.errors)
        self.assert_valid(self.solo)
        self.assert_equal({}, self.solo.errors)  #  TODO  match Django errorizers

    def test_cards_with_empty_names_should_not_be_valid(self):
        self.visa.first_name = ''
        self.visa.last_name  = ''

        self.deny_valid(self.visa)
        reference = dict(first_name='this field is required', last_name='this field is required')  #  CONSIDER  match this to Django model-land
        self.assert_match_hash(reference, self.visa.errors)

    '''

  def test_should_be_able_to_access_errors_indifferently
    self.visa.first_name = ''

    assert_not_valid self.visa
    assert self.visa.errors.on(:first_name)
    assert self.visa.errors.on("first_name")
  end

  def test_should_be_able_to_liberate_a_bogus_card
    c = credit_card('', :type='bogus')
    assert_valid c

    c.type = 'visa'
    assert_not_valid c
  end

  def test_should_be_able_to_identify_invalid_card_numbers
    self.visa.number = nil
    assert_not_valid self.visa

    self.visa.number = "11112222333344ff"
    assert_not_valid self.visa
    assert_false self.visa.errors.on(:type)
    assert       self.visa.errors.on(:number)

    self.visa.number = "111122223333444"
    assert_not_valid self.visa
    assert_false self.visa.errors.on(:type)
    assert       self.visa.errors.on(:number)

    self.visa.number = "11112222333344444"
    assert_not_valid self.visa
    assert_false self.visa.errors.on(:type)
    assert       self.visa.errors.on(:number)
  end

  def test_should_have_errors_with_invalid_card_type_for_otherwise_correct_number
    self.visa.type = 'master'

    assert_not_valid self.visa
    assert_not_equal self.visa.errors.on(:number), self.visa.errors.on(:type)
  end

  def test_should_be_invalid_when_type_cannot_be_detected
    self.visa.number = nil
    self.visa.type = nil

    assert_not_valid self.visa
    assert_match /is required/, self.visa.errors.on(:type)
    assert  self.visa.errors.on(:type)
  end

  def test_should_be_a_valid_card_number
    self.visa.number = "4242424242424242"

    assert_valid self.visa
  end

  def test_should_require_a_valid_card_month
    self.visa.month  = Time.now.month
    self.visa.year   = Time.now.year

    assert_valid self.visa
  end

  def test_should_not_be_valid_with_empty_month
    self.visa.month = ''

    assert_not_valid self.visa
    assert self.visa.errors.on('month')
  end

  def test_should_not_be_valid_for_edge_month_cases
    self.visa.month = 13
    self.visa.year = Time.now.year
    assert_not_valid self.visa
    assert self.visa.errors.on('month')

    self.visa.month = 0
    self.visa.year = Time.now.year
    assert_not_valid self.visa
    assert self.visa.errors.on('month')
  end

  def test_should_be_invalid_with_empty_year
    self.visa.year = ''
    assert_not_valid self.visa
    assert self.visa.errors.on('year')
  end

  def test_should_not_be_valid_for_edge_year_cases
    self.visa.year  = Time.now.year - 1
    assert_not_valid self.visa
    assert self.visa.errors.on('year')

    self.visa.year  = Time.now.year + 21
    assert_not_valid self.visa
    assert self.visa.errors.on('year')
  end

  def test_should_be_a_valid_future_year
    self.visa.year = Time.now.year + 1
    assert_valid self.visa
  end


  def test_should_be_valid_with_start_month_and_year_as_string
    self.solo.start_month = '2'
    self.solo.start_year = '2007'
    assert_valid self.solo
  end

  def test_should_identify_wrong_cardtype
    c = credit_card(:type='master')
    assert_not_valid c
  end

  def test_should_display_number
    assert_equal 'XXXX-XXXX-XXXX-1234', CreditCard.new(:number='1111222233331234').display_number
    assert_equal 'XXXX-XXXX-XXXX-1234', CreditCard.new(:number='111222233331234').display_number
    assert_equal 'XXXX-XXXX-XXXX-1234', CreditCard.new(:number='1112223331234').display_number

    assert_equal 'XXXX-XXXX-XXXX-', CreditCard.new(:number=nil).display_number
    assert_equal 'XXXX-XXXX-XXXX-', CreditCard.new(:number='').display_number
    assert_equal 'XXXX-XXXX-XXXX-123', CreditCard.new(:number='123').display_number
    assert_equal 'XXXX-XXXX-XXXX-1234', CreditCard.new(:number='1234').display_number
    assert_equal 'XXXX-XXXX-XXXX-1234', CreditCard.new(:number='01234').display_number
  end

  def test_should_correctly_identify_card_type
    assert_equal 'visa',             CreditCard.type?('4242424242424242')
    assert_equal 'american_express', CreditCard.type?('341111111111111')
    assert_nil CreditCard.type?('')
  end

  def test_should_be_able_to_require_a_verification_value
    CreditCard.require_verification_value = true
    assert CreditCard.requires_verification_value?
  end

  def test_should_not_be_valid_when_requiring_a_verification_value
    CreditCard.require_verification_value = true
    card = credit_card('4242424242424242', :verification_value=nil)
    assert_not_valid card

    card.verification_value = '123'
    assert_valid card
  end

  def test_should_require_valid_start_date_for_solo_or_switch
    self.solo.start_month  = nil
    self.solo.start_year   = nil
    self.solo.issue_number = nil

    assert_not_valid self.solo
    assert self.solo.errors.on('start_month')
    assert self.solo.errors.on('start_year')
    assert self.solo.errors.on('issue_number')

    self.solo.start_month = 2
    self.solo.start_year  = 2007
    assert_valid self.solo
  end

  def test_should_require_a_valid_issue_number_for_solo_or_switch
    self.solo.start_month  = nil
    self.solo.start_year   = 2005
    self.solo.issue_number = nil

    assert_not_valid self.solo
    assert self.solo.errors.on('start_month')
    assert self.solo.errors.on('issue_number')

    self.solo.issue_number = 3
    assert_valid self.solo
  end

  def test_should_return_last_four_digits_of_card_number
    ccn = CreditCard.new(:number="4779139500118580")
    assert_equal "8580", ccn.last_digits
  end

  def test_bogus_last_digits
    ccn = CreditCard.new(:number="1")
    assert_equal "1", ccn.last_digits
  end

  def test_should_be_true_when_credit_card_has_a_first_name
    c = CreditCard.new
    assert_false c.first_name?

    c = CreditCard.new(:first_name='James')
    assert c.first_name?
  end

  def test_should_be_true_when_credit_card_has_a_last_name
    c = CreditCard.new
    assert_false c.last_name?

    c = CreditCard.new(:last_name='Herdman')
    assert c.last_name?
  end

  def test_should_test_for_a_full_name
    c = CreditCard.new
    assert_false c.name?

    c = CreditCard.new(:first_name='James', :last_name='Herdman')
    assert c.name?
  end

  # The following is a regression for a bug that raised an exception when
  # a new credit card was validated
  def test_validate_new_card
    credit_card = CreditCard.new

    assert_nothing_raised do
      credit_card.validate
    end
  end

  # The following is a regression for a bug where the keys of the
  # credit card card_companies hash were not duped when detecting the type
  def test_create_and_validate_credit_card_from_type
    credit_card = CreditCard.new(:type=CreditCard.type?('4242424242424242'))
    assert_nothing_raised do
      credit_card.valid?
    end
  end

  def test_autodetection_of_credit_card_type
    credit_card = CreditCard.new(:number='4242424242424242')
    credit_card.valid?
    assert_equal 'visa', credit_card.type
  end

  def test_card_type_should_not_be_autodetected_when_provided
    credit_card = CreditCard.new(:number='4242424242424242', :type='master')
    credit_card.valid?
    assert_equal 'master', credit_card.type
  end

  def test_detecting_bogus_card
    credit_card = CreditCard.new(:number='1')
    credit_card.valid?
    assert_equal 'bogus', credit_card.type
  end

  def test_validating_bogus_card
    credit_card = credit_card('1', :type=nil)
    assert credit_card.valid?
  end

  def test_mask_number
    assert_equal 'XXXX-XXXX-XXXX-5100', CreditCard.mask('5105105105105100')
  end

  def test_strip_non_digit_characters
    card = credit_card('4242-4242      %%%%%%4242......4242')
    assert card.valid?
    assert_equal "4242424242424242", card.number
  end

  def test_before_validate_handles_blank_number
    card = credit_card(nil)
    assert !card.valid?
    assert_equal "", card.number
  end
end
'''

    def tearDown(self):
        CreditCard.require_verification_value = False  #  TODO  give a darn about this
