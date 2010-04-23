

#  CONSIDER  orbital

class MerchantGatewaysPayflowSuite:

    def assert_webservice_called(self, mock, vendor, amount, currency, card_type, cc_number, exp_date, cv_num,
                                       first_name, last_name, username, password):
        #args = self.gateway.post_webservice.call_args[0]
        args = mock.call_args[0]
        assert 2 == len(self.gateway.post_webservice.call_args), 'should be 1 but either we call twice or the Mock has an issue'
        self.assert_equal('https://pilot-payflowpro.paypal.com', args[0])

        xml = args[1]
        xmlns = 'xmlns="http://www.paypal.com/XMLPay"' # TODO  pass to .xpath() instead of erasing!
        assert xmlns in xml
        xml = xml.replace(xmlns, '')

        self.assert_xml(xml, lambda x:
                x.XMLPayRequest(
                        x.RequestData(
                            x.Vendor('LOGIN'),
                            x.Partner('PayPal'),
                            x.Transactions(
                                x.Transaction(
                                    x.Verbosity('MEDIUM'),
                                    x.Authorization()
                                )
                            )
                        ),
                        x.PayData(
                            x.Invoice(
                                x.TotalAmt('1.00', Currency='USD')
                            ),
                        x.Tender(
                            x.Card(
                                x.CardType('Visa'),
                                x.CardNum('4242424242424242'),
                                x.ExpDate('201109'),
                                x.NameOnCard('Longbob'),
                                x.CVNum('123'),
                                x.ExtData(Name="LASTNAME", Value="Longsen")
                            )
                        )
                    ),
                    x.RequestAuth(
                        x.UserPass(
                            x.User('LOGIN'),
                            x.Password('PASSWORD')
                        )
                    )
                )
            )
