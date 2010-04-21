
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult

# note:

#   request - the project's outbound message to the gateway, in merchant-gateways format
#   params - TODO the request, translated into a hash ready to send as soap or something
#   result - the gateway's return message, translated from soap or something to a hash
#   response - the gateway's result, translated into merchant-gateways format, with values exposed as members

class Response(object):
    def __init__(self, success, message, params={}, **options):
        self.success = success
        self.message = message
        self.params  = params
        self.options = options
        self.test = options.setdefault('test', False)
        self.authorization = options.get('authorization', None)  #  TODO  just jam them in??
        self.fraud_review = options.get('fraud_review', None)
        self.is_test = options['is_test']
        self.avs_result = options.get('avs_result', None)
        self.cvv_result = options.get('cvv_result', None)

        if self.avs_result:  self.avs_result = AVSResult(code=self.avs_result)  #  TODO  document if it was not in the inbound message it's None
        if self.cvv_result:  self.cvv_result = CVVResult(code=self.cvv_result)

    def to_dict(self):
        return {'success': self.success,
                'message': self.message,
                'params': self.params,
                'test': self.test,
                'authorization': self.authorization,
                'fraud_review': self.fraud_review}

