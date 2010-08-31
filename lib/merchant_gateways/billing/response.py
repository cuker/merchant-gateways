
from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult
from merchant_gateways.billing.gateways.gateway import default_dict


class Response(object):
    def __init__(self, success, message, result={}, **options):
        self.success = success
        self.message = message
        self.result  = result

        self.options     = default_dict(options).set_default(None)
        self.test          = options.setdefault('test', False)
        self.authorization = self.options['authorization']
        self.fraud_review  = self.options['fraud_review']
        self.is_test    = self.options['is_test']
        self.avs_result = self.options['avs_result']
        self.cvv_result = self.options['cvv_result']
        self.transaction = self.options.get('transaction', None)  #  TODO  everyone needs this

        if self.avs_result:  self.avs_result = AVSResult(code=self.avs_result)  #  TODO  document if it was not in the inbound message it's None
        if self.cvv_result:  self.cvv_result = CVVResult(code=self.cvv_result)

    def to_dict(self):  #  TODO  find a use for this
        return {'success': self.success,
                'message': self.message,
                'params': self.result,
                'test': self.test,
                'authorization': self.authorization,
                'fraud_review': self.fraud_review}

