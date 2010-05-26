

class MerchantGatewaysAuthorizeNetSuite:

    def successful_authorization_response(self):
        return ( '$1$,$1$,$1$,$This transaction has been approved.$,$advE7f$,$Y$,$508141794$,$5b3fe66005f3da0ebe51$,$$,$1.00$,' + #  TODO  pass in same delim as we set
                      '$CC$,$auth_only$,$$,$Longbob$,$Longsen$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,' +
                        '$2860A297E0FE804BCB9EF8738599645C$,$P$,$2$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$,$$' )

    #def failed_authorization_response(self):
    #
    #def successful_void_response(self):
    #
    #def successful_credit_response(self):
    #
    #def assert_webservice_called(self, mock, vendor, amount, currency, card_type, cc_number, exp_date, cv_num,
    #                                   first_name, last_name, username, password):
