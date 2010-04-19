from tests.test_helper import *
from merchant_gateways.billing.cvv_result import CVVResult, MESSAGES

class CVVResultTest(MerchantGatewaysUtilitiesTestSuite):

    def test_nil(self):
        result = CVVResult(nil)
        self.assert_none(result.code)
        self.assert_none(result.message)
        result = CVVResult('')
        self.assert_none(result.code)
        self.assert_none(result.message)

    def test_successful_match(self):
        result = CVVResult('M')
        self.assert_equal( 'M', result.code )
        self.assert_equal( MESSAGES['M'], result.message )
        self.assert_equal( result.messages('M'), result.message )

    def test_failed_match(self):
        result = CVVResult('N')
        self.assert_equal('N', result.code)
        self.assert_equal('No Match', result.message)

    def test_lowercase_match(self):
        result = CVVResult('u')
        self.assert_equal( 'U', result.code )
        self.assert_equal( MESSAGES['U'], result.message )
        self.assert_equal( result.messages('U'), result.message )

    def test_unknown_code(self):
        result = CVVResult('Confringo')
        self.assert_equal('Confringo', result.code)
        self.assert_equal("Unknown code 'Confringo'", result.message)

    def test_to_hash(self):
        result = CVVResult('M').to_hash()
        self.assert_equal('M', result['code'])
        self.assert_equal(MESSAGES['M'], result['message'])
