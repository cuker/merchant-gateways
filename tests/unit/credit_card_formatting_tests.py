from merchant_gateways.tests.test_helper import *
from merchant_gateways.billing.credit_card import CreditCard


class CreditCardFormattingTest(MerchantGatewaysUtilitiesTestSuite):

    def test_should_format_number_by_rule(self):  #  TODO  use or lose this stuff
        self.assert_equal(2005, format(2005, 'steven_colbert'))

'''require 'test_helper'

class CreditCardFormattingTest < Test::Unit::TestCase
  include ActiveMerchant::Billing::CreditCardFormatting


    assert_equal '0005', format(05, :four_digits)
    assert_equal '2005', format(2005, :four_digits)

    assert_equal '05', format(2005, :two_digits)
    assert_equal '05', format(05, :two_digits)
    assert_equal '08', format(8, :two_digits)

    assert format(nil, :two_digits).blank?
    assert format('', :two_digits).blank?
  end
end
'''
