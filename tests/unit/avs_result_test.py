from merchant_gateways.tests.test_helper import *
from merchant_gateways.billing.avs_result import AVSResult, MESSAGES

class AVSResultTest(MerchantGatewaysUtilitiesTestSuite):

    def test_nil(self):
        result = AVSResult(nil)
        self.assert_none(result.code)
        self.assert_none(result.street_match)
        self.assert_none(result.postal_match)

    def test_no_match(self):
        result = AVSResult(code='N')
        self.assert_equal('N', result.code)
        self.assert_equal('N', result.street_match)
        self.assert_equal('N', result.postal_match)
        self.assert_equal('Street address and postal code do not match.', result.message)
        self.assert_equal(MESSAGES['N'], result.message)

    def test_only_street_match(self):
        result = AVSResult(code='A')
        self.assert_equal('A', result.code)
        self.assert_equal('Y', result.street_match)
        self.assert_equal('N', result.postal_match)
        self.assert_equal(result.messages('A'), result.message)

    def test_only_postal_match(self):
        result = AVSResult(code='W')
        self.assert_equal('W', result.code)
        self.assert_equal('N', result.street_match)
        self.assert_equal('Y', result.postal_match)
        self.assert_equal(result.messages('W'), result.message)
        self.assert_equal(result.messages(), result.message)

    def test_nothing_in_nothing_out(self):
        result = AVSResult(code = nil)
        #print grep('assert', dir(self))
        self.assert_none(result.code)
        self.assert_none(result.message)
        result = AVSResult(code='')
        self.assert_none(result.code)
        self.assert_none(result.message)
        result = AVSResult(code="Philosopher's Stone")
        self.assert_none(result.code)
        self.assert_equal('AVS Code "Philosopher\'s Stone" not found', result.message)

    def test_to_hash(self):
        avs_data = AVSResult(code='X').to_hash()
        self.assert_equal('X', avs_data['code'])
        self.assert_equal(MESSAGES['X'], avs_data['message'])

    def test_street_match(self):
        result = AVSResult(street_match='Y')
        self.assert_equal('Y', result.street_match)

    def test_postal_match(self):
        result = AVSResult(postal_match='Y')
        self.assert_equal('Y', result.postal_match)
