
from merchant_gateways.billing.gateways.bogus import BogusGateway  #  TODO name the file bogus_gateway.py
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *

class BogusGatewayTests(MerchantGatewaysTestSuite, MerchantGatewaysTestSuite.CommonTests):

    def gateway_type(self):
        return BogusGateway

    def mock_webservice(self, response, lamb):
        pass

    def test_successful_authorization(self):
        '''All gateways authorize with these inputs and outputs'''

    def test_failed_authorization(self):
        pass

    def test_successful_purchase(self):
        pass

'''def setup
    @gateway = BogusGateway.new(
      :login => 'bogus',
      :password => 'bogus'
    )

    @creditcard = credit_card('1')

    @response = ActiveMerchant::Billing::Response.new(true, "Transaction successful", :transid => BogusGateway::AUTHORIZATION)
  end'''

'''  def test_authorize(self):
    @gateway.capture(1000, @creditcard)

  def test_purchase
    @gateway.purchase(1000, @creditcard)
  end

  def test_credit
    @gateway.credit(1000, @response.params["transid"])
  end

  def test_void
    @gateway.void(@response.params["transid"])
  end

  def  test_store
    @gateway.card_store(@creditcard)
  end

  def test_unstore
    @gateway.unstore('1')
  end

  def test_supported_countries
    assert_equal ['US'], BogusGateway.supported_countries
  end

  def test_supported_card_types
    assert_equal [:bogus], BogusGateway.supported_cardtypes
  end
end
'''
