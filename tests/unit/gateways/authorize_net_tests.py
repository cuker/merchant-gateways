
from merchant_gateways.billing.gateways.authorize_net import AuthorizeNet  #  test target is _always_ first line!
from merchant_gateways.billing.credit_card import CreditCard
from merchant_gateways.tests.test_helper import *
from merchant_gateways.tests.billing.gateways.authorize_net_suite import MerchantGatewaysAuthorizeNetSuite

#  TODO  all them options gotta be... OPTIONAL!!

#  TODO  require all required parameters

class AuthorizeNetTests(MerchantGatewaysTestSuite,
                        MerchantGatewaysAuthorizeNetSuite,
                        MerchantGatewaysTestSuite.CommonTests):

    def gateway_type(self):
        return AuthorizeNet

    def assert_successful_authorization(self):

        # TODO  assert the response is None if we epic-fail (oh, and trap exceptions)

        self.gateway.post_webservice.assert_called_with(
                ('https://test.authorize.net/gateway/transact.dll?x_login=X&x_invoice_num=%i&' % self.options['order_id']) +
                'x_last_name=Granger&x_card_code=456&x_card_num=4242424242424242&x_amount=100.00&x_delim_char=%2C&x_tran_key=Y&' +
                'x_encap_char=%24&x_version=3.1&x_first_name=Hermione&x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&' +
                'x_type=AUTH_ONLY&x_description=Chamber+of+Secrets&x_test_request=TRUE', {}
                )  #  TODO  beautify the response, via assert_params

        #~ assert response = self.gateway.authorize(self.amount, self.credit_card)

        reference = { 'response_reason_code': '1', 'card_code': 'P', 'response_reason_text': 'This transaction has been approved.',
                      'avs_result_code': 'Y', 'response_code': 1, 'transaction_id': '508141794' }

        self.assert_match_dict(reference, self.response.result)
        #        self.assertEqual('508141794', self.response.params['authorization'])  #  TODO  also self.response.authorization
        self.assert_equal('This transaction has been approved', self.response.message)
        self.assert_equal('508141794', self.response.authorization)

    def assert_failed_authorization(self):
        reference = { 'response_reason_code': '1', 'card_code': 'P', 'response_reason_text': 'This transaction was declined.',
                      'avs_result_code': 'Y', 'response_code': 2, 'transaction_id': '508141794' }
        self.assert_match_dict(reference, self.response.result)
        self.assert_equal('This transaction was declined', self.response.message)
        self.assert_equal('508141794', self.response.authorization)  # uh, we authorize failure around here?

    def assert_successful_purchase(self):
        reference = { 'response_reason_code': '1', 'card_code': 'P', 'response_reason_text': 'This transaction has been approved.',
                      'avs_result_code': 'Y', 'response_code': 1, 'transaction_id': '508141795' }

        self.assert_match_dict(reference, self.response.result)

         #  TODO  what's in the response? and why a PayflowRequest inherits Request but a AuthorizeNet Response IS a Response?

        #  CONSIDER  test u can vary the x_amount

        self.gateway.post_webservice.assert_called_with(
                ('https://test.authorize.net/gateway/transact.dll?x_login=X&x_invoice_num=%i&x_trans_id=Y&' % self.options['order_id']) + \
                  'x_last_name=Granger&x_card_code=456&x_card_num=4242424242424242&x_amount=100.00&' + \
                  'x_delim_char=%2C&x_tran_key=Y&x_encap_char=%24&x_version=3.1&x_first_name=Hermione&' + \
                  'x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&x_type=AUTH_CAPTURE&' + \
                  'x_description=&x_test_request=TRUE', {}
                )  #  TODO  beautify the response, and constrain the order of the params

    def test_add_description(self):
        result = {}
        self.gateway.order_id = 42
        self.gateway.add_invoice(result, description='Cornish Pixies')
        self.assertEqual('Cornish Pixies', result['description'])


    def successful_purchase_response(self):
        return '$1$,$1$,$1$,$This transaction has been approved.$,$d1GENk$,$Y$,$508141795$,$32968c18334f16525227$,' + \
                      '$Store purchase$,$1.00$,$CC$,$auth_capture$,$$,$Longbob$,$Longsen$,' + \
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,' + \
                      '$269862C030129C1173727CC10B1935ED$,$P$,$2$,' + \
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$'

    def test_avs_result(self):
        self.test_successful_authorization()
        avs = self.response.avs_result
        self.assert_equal( 'Y', avs.code )
        self.assert_equal( 'Y', avs.street_match )
        self.assert_equal( 'Y', avs.postal_match )

    def test_fraudulent_avs_result(self):
        self.mock_webservice(self.fraud_review_response(),  #  TODO  abstract test on this
            lambda: self.gateway.authorize(self.amount, self.credit_card, **self.options) )
        self.response = self.gateway.response
        avs = self.response.avs_result
        self.assert_equal( 'X', avs.code )
        self.assert_equal( 'Y', avs.street_match )
        self.assert_equal( 'Y', avs.postal_match )

    def fraud_review_response(self):
        return ( "$4$,$$,$253$,$Thank you! For security reasons your order is currently being reviewed.$,$$,$X$,$0$,$$," +
                 "$$,$1.00$,$$,$auth_capture$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$," +
                 "$$,$207BCBBF78E85CF174C87AE286B472D2$,$M$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$," +
                 "$$,$$,$$,$$,$$,$$,$$,$$,$$,$$" )

    def test_cvv_result(self):
        self.test_successful_authorization()
        cvv = self.response.cvv_result
        self.assert_equal( 'P', cvv.code )
        self.assert_equal( 'Not Processed', cvv.message )  #  TODO  huh?

    def test_fraudulent_cvv_result(self):
        self.mock_webservice(self.fraud_review_response(),
                             lambda: self.gateway.authorize(self.amount, self.credit_card, **self.options) )
        self.response = self.gateway.response
        cvv = self.response.cvv_result
        self.assert_equal( 'M', cvv.code )
        self.assert_equal( 'Match', cvv.message )  #  TODO  huh??

 ## TODO  put low-level methods into chrono order

    def test_post_data(self):
        action = 'AUTH_ONLY'
        parameters = {'first_name': 'Hermione', 'card_num': '4242424242424242', 'description': 'Chamber of Secrets', 'card_code': None, 'invoice_num': 1, 'test_request': 'TRUE', 'amount': '1.00', 'last_name': 'Granger', 'exp_date': '1290'}
        reference = '?x_login=X&x_invoice_num=1&x_last_name=Granger&x_card_code=None&x_card_num=4242424242424242&x_amount=1.00&x_delim_char=%2C&x_tran_key=Y&x_encap_char=%24&x_version=3.1&x_first_name=Hermione&x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&x_type=AUTH_ONLY&x_description=Chamber+of+Secrets&x_test_request=TRUE'
        self.assert_equal(reference, self.gateway.post_data(action, parameters))
        action = 'AUTH_CAPTURE'
        parameters = {'first_name': 'Hermione', 'card_num': '4242424242424242', 'description': '', 'card_code': None, 'invoice_num': 1, 'test_request': 'TRUE', 'amount': '1.00', 'last_name': 'Granger', 'exp_date': '1290', 'login': 'X', 'trans_id': 'Y'}
        reference = '?x_login=X&x_invoice_num=1&x_trans_id=Y&x_last_name=Granger&x_card_code=None&x_card_num=4242424242424242&x_amount=1.00&x_delim_char=%2C&x_tran_key=Y&x_encap_char=%24&x_version=3.1&x_first_name=Hermione&x_exp_date=1290&x_delim_data=TRUE&x_relay_response=FALSE&x_type=AUTH_CAPTURE&x_description=&x_test_request=TRUE'
        self.assert_equal(reference, self.gateway.post_data(action, parameters))

    # TODO  fun with print self.assert_params(params)!

    def test_parse(self):
        reference = { 'response_reason_code': '1', 'card_code': 'P', 'response_reason_text': 'This transaction has been approved.',
                      'avs_result_code': 'Y', 'response_code': 1, 'transaction_id': '508141794' }

        self.assert_match_hash(reference, self.gateway.parse(self.successful_authorization_response()))

        reference = { 'response_reason_code': '1', 'card_code': 'P', 'response_reason_text': 'This transaction was declined.',
                      'avs_result_code': 'Y', 'response_code': 2, 'transaction_id': '508141794' }

        self.assert_match_dict(reference, self.gateway.parse(self.failed_authorization_response()))

        reference = { 'card_code': 'P', 'response_reason_text': 'This transaction has been approved.', 'response_reason_code': '1',
                      'avs_result_code': 'Y', 'response_code': 1, 'transaction_id': '508141795' }

        self.assert_match_hash(reference, self.gateway.parse(self.successful_purchase_response()))

        reference = { 'response_reason_code': '253', 'card_code': 'M',
                      'response_reason_text': 'Thank you! For security reasons your order is currently being reviewed.',
                      'avs_result_code': 'X', 'response_code': 4, 'transaction_id': '0' }

        self.assert_match_hash(reference, self.gateway.parse(self.fraud_review_response()))

#      def test_failure_without_response_reason_text
#      def test_response_under_review_by_fraud_service
#      def failed_credit_response
#      def successful_recurring_response
#      def successful_update_recurring_response
#      def successful_cancel_recurring_response

    def test_add_address_outsite_north_america(self):
        result = {}

        self.gateway.add_address( result, billing_address = {'address1': '164 Waverley Street', 'country': 'DE', 'state': ''} )

        self.assert_equal_set(["address", "city", "company", "country", "phone", "state", "zip"], result.keys())
        self.assert_equal('n/a', result['state'])
        self.assert_equal('164 Waverley Street', result['address'])
        self.assert_equal('DE', result['country'])

    def test_add_address(self):
        result = {}

        self.gateway.add_address( result, billing_address= { 'address1': '164 Waverley Street', 'country': 'US', 'state': 'CO' } )

        self.assert_equal_set(["address", "city", "company", "country", "phone", "state", "zip"], result.keys())
        self.assert_equal('CO', result['state'])
        self.assert_equal('164 Waverley Street', result['address'])
        self.assert_equal('US', result['country'])

    def test_add_invoice(self):
        result = {}
        self.gateway.add_invoice(result, order_id='#1001')
        self.assert_equal('#1001', result['invoice_num'])  #  TODO  now test it actually goes out the wire!

#      def test_add_duplicate_window_without_duplicate_window  CONSIDER  whut?
#        result = {}
#        ActiveMerchant::Billing::AuthorizeNetGateway.duplicate_window = nil
#        self.gateway.send(:add_duplicate_window, result)
#        assert_nil result[:duplicate_window]
#      end
#
#      def test_add_duplicate_window_with_duplicate_window
#        result = {}
#        ActiveMerchant::Billing::AuthorizeNetGateway.duplicate_window = 0
#        self.gateway.send(:add_duplicate_window, result)
#        assert_equal 0, result[:duplicate_window]
#      end

    def test_purchase_is_valid_csv(self):
       params = { 'amount': '1.01' }

       self.gateway.add_creditcard(params, self.credit_card)
       data = self.gateway.post_data('AUTH_ONLY', params)
       sample = self.assert_params(re.sub(r'^\?', '', data))
       reference = self.assert_params(self.post_data_fixture())
       self.assert_match_dict(reference, sample)

    def post_data_fixture(self):
        return ( 'x_encap_char=%24&x_card_num=4242424242424242&x_exp_date=1290&x_card_code=456&x_type=AUTH_ONLY&' +
                 'x_first_name=Hermione&x_version=3.1&x_login=X&x_last_name=Granger&x_tran_key=Y&x_relay_response=FALSE' +
                 '&x_delim_data=TRUE&x_delim_char=%2C&x_amount=1.01' )

    def test_purchase_meets_minimum_requirements(self):  #  TODO  what was the point of this?
        params = { 'amount': "1.01" }

        self.gateway.add_creditcard(params, self.credit_card)
        data = self.gateway.post_data('AUTH_ONLY', params)  #  TODO  should the ? be there?
        sample = self.assert_params(re.sub(r'^\?', '', data))
    #    print sample  #  TODO  where's the 1.01 ??

#        assert data = self.gateway.send(:post_data, 'AUTH_ONLY', params)
        for key in self.minimum_requirements():
            self.assert_contains('x_' + key, sample.keys())

    def minimum_requirements(self):
        return ['version', 'delim_data', 'relay_response', 'login', 'tran_key', 'amount', 'card_num', 'exp_date', 'type']

    def test_successful_credit(self):
        self.mock_webservice( self.successful_purchase_response(),  #  TODO  shouldn't that be a successful_credit_response()?
                              lambda: self.gateway.credit(self.amount, '123456789', card_number=self.credit_card.number) )
        self.assert_success()
        self.assert_equal('This transaction has been approved', self.response.message)

    def test_failed_credit(self):
        self.mock_webservice( self.failed_credit_response(),  #  TODO  shouldn't that be a successful_credit_response()?
                              lambda: self.gateway.credit(self.amount, '123456789', card_number=self.credit_card.number) )
        self.assert_failure()
        self.assert_equal('The referenced transaction does not meet the criteria for issuing a credit', self.response.message)

    def failed_credit_response(self):
        return '$3$,$2$,$54$,$The referenced transaction does not meet the criteria for issuing a credit.$,$$,$P$,$0$,$$,$$,$1.00$,$CC$,$credit$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$39265D8BA0CDD4F045B5F4129B2AAA01$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$'

    def test_supported_card_types(self):
        '''Consider: These trivial kinds of test should put their money where their mouths are and loop thru them!'''

        self.assert_equal(['visa', 'master', 'american_express', 'discover'], AuthorizeNet.supported_cardtypes)
        self.assert_equal(['US'], AuthorizeNet.supported_countries)

#      def test_failure_without_response_reason_text  CONSIDER wat?
#        assert_nothing_raised do
#          assert_equal '', self.gateway.send(:message_from, {})
#        end
#      end

    def test_response_under_review_by_fraud_service(self):
        self.mock_webservice( self.fraud_review_response(),
                              lambda: self.gateway.purchase(self.amount, self.credit_card) )
        self.assert_failure()
        self.assert_(self.response.fraud_review)
        self.assert_equal("Thank you! For security reasons your order is currently being reviewed", self.response.message)

    '''

      # ARB Unit Tests CONSIDER  we have no mandate for recurrence yet (right?)

      def test_successful_recurring
        self.gateway.expects(:ssl_post).returns(successful_recurring_response)

        response = self.gateway.recurring(self.amount, self.credit_card,
          :billing_address => address.merge(:first_name => 'Jim', :last_name => 'Smith'),
          :interval => {
            :length => 10,
            :unit => :days
          },
          :duration => {
            :start_date => Time.now.strftime("%Y-%m-%d"),
            :occurrences => 30
          }
       )

        assert_instance_of Response, response
        assert response.success?
        assert response.test?
        assert_equal self.subscription_id, response.authorization
      end

      def test_successful_update_recurring
        self.gateway.expects(:ssl_post).returns(successful_update_recurring_response)

        response = self.gateway.update_recurring(:subscription_id => self.subscription_id, :amount => self.amount * 2)

        assert_instance_of Response, response
        assert response.success?
        assert response.test?
        assert_equal self.subscription_id, response.authorization
      end

      def test_successful_cancel_recurring
        self.gateway.expects(:ssl_post).returns(successful_cancel_recurring_response)

        response = self.gateway.cancel_recurring(self.subscription_id)

        assert_instance_of Response, response
        assert response.success?
        assert response.test?
        assert_equal self.subscription_id, response.authorization
      end

      def test_expdate_formatting
        assert_equal '2009-09', self.gateway.send(:arb_expdate, credit_card('4111111111111111', :month => "9", :year => "2009"))
        assert_equal '2013-11', self.gateway.send(:arb_expdate, credit_card('4111111111111111', :month => "11", :year => "2013"))
      end

      private

      def successful_recurring_response
        <<-XML
    <ARBCreateSubscriptionResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
      <refId>Sample</refId>
      <messages>
        <resultCode>Ok</resultCode>
        <message>
          <code>I00001</code>
          <text>Successful.</text>
        </message>
      </messages>
      <subscriptionId>#{self.subscription_id}</subscriptionId>
    </ARBCreateSubscriptionResponse>
        XML
      end

      def successful_update_recurring_response
        <<-XML
    <ARBUpdateSubscriptionResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
      <refId>Sample</refId>
      <messages>
        <resultCode>Ok</resultCode>
        <message>
          <code>I00001</code>
          <text>Successful.</text>
        </message>
      </messages>
      <subscriptionId>#{self.subscription_id}</subscriptionId>
    </ARBUpdateSubscriptionResponse>
        XML
      end

      def successful_cancel_recurring_response
        <<-XML
    <ARBCancelSubscriptionResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
      <refId>Sample</refId>
      <messages>
        <resultCode>Ok</resultCode>
        <message>
          <code>I00001</code>
          <text>Successful.</text>
        </message>
      </messages>
      <subscriptionId>#{self.subscription_id}</subscriptionId>
    </ARBCancelSubscriptionResponse>
        XML
      end
    end
    '''

    def failed_authorization_response(self):
        return '$2$,$1$,$1$,$This transaction was declined.$,$advE7f$,$Y$,$508141794$,$5b3fe66005f3da0ebe51$,' + \
                      '$$,$1.00$,$CC$,$auth_only$,$$,$Longbob$,$Longsen$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,' + \
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$2860A297E0FE804BCB9EF8738599645C$,$P$,$2$,$$,$$,$$,$$,$$,$$,' + \
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$'
