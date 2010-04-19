
    # Implements the Address Verification System
    # https://www.wellsfargo.com/downloads/pdf/biz/merchant/visa_avs.pdf
    # http://en.wikipedia.org/wiki/Address_Verification_System
    # http://apps.cybersource.com/library/documentation/dev_guides/CC_Svcs_IG/html/app_avs_cvn_codes.htm#app_AVS_CVN_codes_7891_48375
    # http://imgserver.skipjack.com/imgServer/5293710/AVS%20and%20CVV2.pdf
    # http://www.emsecommerce.net/avs_cvv2_response_codes.htm

class AVSResult():

    def __init__(self, code=None, street_match=None, postal_match=None):
        self.code = code
        self.street_match = street_match or STREET_MATCH_CODE.get(code, None)
        self.postal_match = postal_match or POSTAL_MATCH_CODE.get(code, None)
        self.message = self.messages()

        if not self.message:
            self.code = None
            if code:  self.message = 'AVS Code %r not found' % code

    def to_hash(self):
        return { 'code'         : self.code,
                 'message'      : self.message,
                 'street_match' : self.street_match,
                 'postal_match' : self.postal_match
               }  #  CONSIDER  use a hash.pass() method already!

    def messages(self, code=None):
        return MESSAGES.get(code or self.code, None)

STREET_MATCH_CODE = {'A': 'Y', 'C': 'N', 'B': 'Y', 'E': None, 'D': 'Y', 'G': 'X', 'F': None, 'I': None, 'H': 'Y', 'K': 'N', 'J': 'Y', 'M': 'Y', 'L': 'N', 'O': 'Y', 'N': 'N', 'Q': 'Y', 'P': 'N', 'S': 'X', 'R': None, 'U': None, 'T': 'Y', 'W': 'N', 'V': 'Y', 'Y': 'Y', 'X': 'Y', 'Z': 'N'}
POSTAL_MATCH_CODE = {'A': 'N', 'C': 'N', 'B': None, 'E': None, 'D': 'Y', 'G': 'X', 'F': 'Y', 'I': None, 'H': 'Y', 'K': 'N', 'J': 'Y', 'M': 'Y', 'L': 'Y', 'O': 'N', 'N': 'N', 'Q': 'Y', 'P': 'Y', 'S': 'X', 'R': None, 'U': None, 'T': None, 'W': 'Y', 'V': 'Y', 'Y': 'Y', 'X': 'Y', 'Z': 'Y'}

MESSAGES = {
        'A' : 'Street address matches, but 5-digit and 9-digit postal code do not match.',
        'B' : 'Street address matches, but postal code not verified.',
        'C' : 'Street address and postal code do not match.',
        'D' : 'Street address and postal code match.',
        'E' : 'AVS data is invalid or AVS is not allowed for this card type.',
        'F' : 'Card member\'s name does not match, but billing postal code matches.',
        'G' : 'Non-U.S. issuing bank does not support AVS.',
        'H' : 'Card member\'s name does not match. Street address and postal code match.',
        'I' : 'Address not verified.',
        'J' : 'Card member\'s name, billing address, and postal code match. Shipping information verified and chargeback protection guaranteed through the Fraud Protection Program.',
        'K' : 'Card member\'s name matches but billing address and billing postal code do not match.',
        'L' : 'Card member\'s name and billing postal code match, but billing address does not match.',
        'M' : 'Street address and postal code match.',
        'N' : 'Street address and postal code do not match.',
        'O' : 'Card member\'s name and billing address match, but billing postal code does not match.',
        'P' : 'Postal code matches, but street address not verified.',
        'Q' : 'Card member\'s name, billing address, and postal code match. Shipping information verified but chargeback protection not guaranteed.',
        'R' : 'System unavailable.',
        'S' : 'U.S.-issuing bank does not support AVS.',
        'T' : 'Card member\'s name does not match, but street address matches.',
        'U' : 'Address information unavailable.',
        'V' : 'Card member\'s name, billing address, and billing postal code match.',
        'W' : 'Street address does not match, but 9-digit postal code matches.',
        'X' : 'Street address and 9-digit postal code match.',
        'Y' : 'Street address and 5-digit postal code match.',
        'Z' : 'Street address does not match, but 5-digit postal code matches.'
      }
