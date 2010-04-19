MESSAGES = dict(
  D='Suspicious transaction',
  I='Failed data validation check',
  M='Match',
  N='No Match',
  P='Not Processed',
  S='Should have been present',
  U='Issuer unable to process request',
  X='Card does not support verification'
)

class CVVResult(object):
    ''' Result of the Card Verification Value check
       http://www.bbbonline.org/eExport/doc/MerchantGuide_cvv2.pdf
      Check additional codes from cybersource website'''

    def __init__(self, code):
        self.code    = None
        self.message = None
        if not code or code == '':  return
        up_code = code.upper()
        self.code = up_code
        self.message = self.messages(up_code) or None
        if self.message:  return
        self.message = 'Unknown code %r' % code
        self.code = code  #  to restore its case
        
    def messages(self, code):
        return MESSAGES.get(code, None)

    def to_hash(self):
        return dict(code=self.code, message=self.message)