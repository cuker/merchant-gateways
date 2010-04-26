

#  CONSIDER  orbital

class MerchantGatewaysPayflowSuite:

    def successful_authorization_response(self):
        return '''<ResponseData>
                    <Result>0</Result>
                    <Message>Approved</Message>
                    <Partner>verisign</Partner>
                    <HostCode>000</HostCode>
                    <ResponseText>AP</ResponseText>
                    <PnRef>VUJN1A6E11D9</PnRef>
                    <IavsResult>N</IavsResult>
                    <ZipMatch>Match</ZipMatch>
                    <AuthCode>094016</AuthCode>
                    <Vendor>ActiveMerchant</Vendor>
                    <AvsResult>Y</AvsResult>
                    <StreetMatch>Match</StreetMatch>
                    <CvResult>Match</CvResult>
                </ResponseData>'''

    def failed_authorization_response(self):
        return '''<ResponseData>
                    <Result>12</Result>
                    <Message>Declined</Message>
                    <Partner>verisign</Partner>
                    <HostCode>000</HostCode>
                    <ResponseText>AP</ResponseText>
                    <PnRef>VUJN1A6E11D9</PnRef>
                    <IavsResult>N</IavsResult>
                    <ZipMatch>Match</ZipMatch>
                    <AuthCode>094016</AuthCode>
                    <Vendor>ActiveMerchant</Vendor>
                    <AvsResult>Y</AvsResult>
                    <StreetMatch>Match</StreetMatch>
                    <CvResult>Match</CvResult>
                </ResponseData>'''

    def assert_webservice_called(self, mock, vendor, amount, currency, card_type, cc_number, exp_date, cv_num,
                                       first_name, last_name, username, password):
        #args = self.gateway.post_webservice.call_args[0]
        args = mock.call_args[0]
        assert 2 == len(self.gateway.post_webservice.call_args), 'should be 1 but either we call twice or the Mock has an issue'

        if self.gateway.is_test:  #  TODO  ternary
            self.assert_equal('https://pilot-payflowpro.paypal.com', args[0])
        else:
            self.assert_equal('https://payflowpro.paypal.com', args[0])

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
                                x.TotalAmt(amount, Currency='USD')
                            ),
                        x.Tender(
                            x.Card(
                                x.CardType('Visa'),
                                x.CardNum(cc_number),
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
