from merchant_gateways.billing.avs_result import AVSResult
from merchant_gateways.billing.cvv_result import CVVResult

class Response(object):
    def __init__(self, success, message, result={}, **options):
        self.success = success
        self.message = message
        self.result  = result

        self.options     = options
        #TODO pick one
        self.test          = options.setdefault('test', False)
        self.is_test    = self.options['is_test']
        
        #CONSIDER what is the difference between authorization and transaction?
        self.authorization = self.options.get('authorization')
        self.transaction = self.options.get('transaction')
        self.card_store_id = self.options.get('card_store_id')
        
        self.fraud_review  = self.options.get('fraud_review')
        self.avs_result = self.options.get('avs_result')
        self.cvv_result = self.options.get('cvv_result')

        if self.avs_result:  self.avs_result = AVSResult(code=self.avs_result)
        if self.cvv_result:  self.cvv_result = CVVResult(code=self.cvv_result)

    def to_dict(self):  #  TODO  find a use for this
        return {'success': self.success,
                'message': self.message,
                'params': self.result,
                'test': self.test,
                'authorization': self.authorization,
                'fraud_review': self.fraud_review}

