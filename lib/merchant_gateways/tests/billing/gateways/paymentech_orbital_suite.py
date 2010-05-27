
from merchant_gateways.tests.test_helper import MerchantGatewaysWebserviceTestSuite
from lxml.builder import ElementMaker
XML = ElementMaker()
from merchant_gateways.billing.gateways.gateway import xStr

class MerchantGatewaysPaymentechOrbitalSuite(MerchantGatewaysWebserviceTestSuite):

    def set_gateway_up(self):
        self.options['merchant_id'] = 'Anglia 105E'

    def successful_purchase_response(self):  #  TODO  get a real one!
        return self.successful_authorization_response()

    def successful_authorization_response(self):

#        response = '''<?xml version="1.0" encoding="UTF-8"?> <Response> <ACResponse> <CommonDataResponse> <CommonMandatoryResponse HcsTcsInd="T" LangInd="00" MessageType="A" TzCode="705" Version="2"> <MerchantID>123456789012</MerchantID> <TerminalID>001</TerminalID> <TxRefNum>128E6C6A4FC6D4119A3700D0B706C51EE26DF570</TxRefNum> <TxRefIdx>0</TxRefIdx> <OrderNumber>1234567890123456</OrderNumber> <RespTime>10012001120003</RespTime> <ProcStatus>0</ProcStatus> <ApprovalStatus>1</ApprovalStatus> <ResponseCodes> <AuthCode>tntC09</AuthCode> <RespCode>00</RespCode> <HostRespCode>00</HostRespCode> <CVV2RespCode>M</CVV2RespCode> <HostCVV2RespCode>M</HostCVV2RespCode> <AVSRespCode>H</AVSRespCode> <HostAVSRespCode>Y</HostAVSRespCode> </ResponseCodes> </CommonMandatoryResponse> <CommonOptionalResponse> <AccountNum>4012888888881</AccountNum> <RespDate>010801</RespDate> <CardType>VI</CardType> <ExpDate>200512</ExpDate> <CurrencyCd>840</CurrencyCd> </CommonOptionalResponse> </CommonDataResponse> <AuthResponse> <AuthMandatoryResponse/> <AuthOptionalResponse> <POSEntryMode>01</POSEntryMode> <MISCData> <ActualRespCd>00 </ActualRespCd> </MISCData> <NetworkData> <AuthNetwkID>01</AuthNetwkID> </NetworkData> <VisaCard> <CPSData> <AuthCharInd>V</AuthCharInd> <ValidationCd>JU9E</ValidationCd> </CPSData> <AuthSource AuthSrc="5"/> <VisaCommCard VCC="S"/> </VisaCard> </AuthOptionalResponse> </AuthResponse> </ACResponse> </Response>'''

        #$print self.convert_xml_to_element_maker(response)

        alternate_TODO = XML.Response(
          XML.ACResponse(
            XML.CommonDataResponse(
              XML.CommonMandatoryResponse(
                XML.MerchantID('123456789012'),
                XML.TerminalID('001'),
                XML.TxRefNum('128E6C6A4FC6D4119A3700D0B706C51EE26DF570'),
                XML.TxRefIdx('0'),
                XML.OrderNumber('1234567890123456'),
                XML.RespTime('10012001120003'),
                XML.ProcStatus('0'),
                XML.ApprovalStatus('1'),
                XML.ResponseCodes(
                  XML.AuthCode('tntC09'),
                  XML.RespCode('00'),
                  XML.HostRespCode('00'),
                  XML.CVV2RespCode('M'),
                  XML.HostCVV2RespCode('M'),
                  XML.AVSRespCode('H'),
                  XML.HostAVSRespCode('Y')), HcsTcsInd='T', LangInd='00', MessageType='A', TzCode='705', Version='2'),
              XML.CommonOptionalResponse(
                XML.AccountNum('4012888888881'),
                XML.RespDate('010801'),
                XML.CardType('VI'),
                XML.ExpDate('200512'),
                XML.CurrencyCd('840'))),
            XML.AuthResponse(
              XML.AuthMandatoryResponse(),
              XML.AuthOptionalResponse(
                XML.POSEntryMode('01'),
                XML.MISCData(
                  XML.ActualRespCd('00 ')),
                XML.NetworkData(
                  XML.AuthNetwkID('01')),
                XML.VisaCard(
                  XML.CPSData(
                    XML.AuthCharInd('V'),
                    XML.ValidationCd('JU9E')),
                  XML.AuthSource(AuthSrc='5'),
                  XML.VisaCommCard(VCC='S'))))))

        return xStr(XML.Response(
                      XML.NewOrderResp(
                        XML.IndustryType(),
                        XML.MessageType('AC'),
                        XML.MerchantID('000000'),
                        XML.TerminalID('000'),
                        XML.CardBrand('MC'),
                        XML.AccountNum('5454545454545454'),
                        XML.OrderID('1'),
                        XML.TxRefNum('4A785F5106CCDC41A936BFF628BF73036FEC5401'),
                        XML.TxRefIdx('1'),
                        XML.ProcStatus('0'),
                        XML.ApprovalStatus('1'),
                        XML.RespCode('00'),
                        XML.AVSRespCode('B '),
                        XML.CVV2RespCode('M'),
                        XML.AuthCode('tst554'),
                        XML.RecurringAdviceCd(),
                        XML.CAVVRespCode(),
                        XML.StatusMsg('Approved'),
                        XML.RespMsg(),
                        XML.HostRespCode('100'),
                        XML.HostAVSRespCode('I3'),
                        XML.HostCVV2RespCode('M'),
                        XML.CustomerRefNum('2145108'),
                        XML.CustomerName('JOE SMITH'),
                        XML.ProfileProcStatus('0'),
                        XML.CustomerProfileMessage('Profile Created'),
                        XML.RespTime('121825'))))

    def failed_authorization_response(self):
        return xStr(XML.Response(
                      XML.QuickResp(
                        XML.ProcStatus('841'),
                        XML.StatusMsg('Error validating card/account number range'),
                        XML.CustomerBin(),
                        XML.CustomerMerchantID(),
                        XML.CustomerName(),
                        XML.CustomerRefNum(),
                        XML.CustomerProfileAction(),
                        XML.ProfileProcStatus('9576'),
                        XML.CustomerProfileMessage('Profile: Unable to Perform Profile Transaction. The Associated Transaction Failed. '),
                        XML.CustomerAddress1(),
                        XML.CustomerAddress2(),
                        XML.CustomerCity(),
                        XML.CustomerState(),
                        XML.CustomerZIP(),
                        XML.CustomerEmail(),
                        XML.CustomerPhone(),
                        XML.CustomerProfileOrderOverrideInd(),
                        XML.OrderDefaultDescription(),
                        XML.OrderDefaultAmount(),
                        XML.CustomerAccountType(),
                        XML.CCAccountNum(),
                        XML.CCExpireDate(),
                        XML.ECPAccountDDA(),
                        XML.ECPAccountType(),
                        XML.ECPAccountRT(),
                        XML.ECPBankPmtDlv(),
                        XML.SwitchSoloStartDate(),
                        XML.SwitchSoloIssueNum())))

