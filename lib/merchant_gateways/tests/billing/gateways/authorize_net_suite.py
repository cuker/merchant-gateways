

#  TODO  also publish a generic test suite that works for any gateway

class MerchantGatewaysAuthorizeNetSuite:

    # TODO  mock_gateway_webservice here!

    def successful_authorization_response(self):
        return ( '$1$,$1$,$1$,$This transaction has been approved.$,$advE7f$,$Y$,$508141794$,$5b3fe66005f3da0ebe51$,$$,$1.00$,' + #  TODO  pass in same delim as we set
                      '$CC$,$auth_only$,$$,$Longbob$,$Longsen$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,' +
                        '$2860A297E0FE804BCB9EF8738599645C$,$P$,$2$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$' )

    def successful_purchase_response(self):
        return ( '$1$,$1$,$1$,$This transaction has been approved.$,$d1GENk$,$Y$,$508141795$,$32968c18334f16525227$,' +
                      '$Store purchase$,$1.00$,$CC$,$auth_capture$,$$,$Longbob$,$Longsen$,' +
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,' +
                      '$269862C030129C1173727CC10B1935ED$,$P$,$2$,' +
                      '$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$' )

    #def failed_authorization_response(self):
    #
    #def successful_void_response(self):
    #
    #def successful_credit_response(self):
    #
    #def assert_webservice_called(self, mock, vendor, amount, currency, card_type, cc_number, exp_date, cv_num,
    #                                   first_name, last_name, username, password):
