
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
#        print options.keys()
 # TODO       print 'cvv_result' in options.keys()
        self.cvv_result = options.get('cvv_result', None)  #   TODO  some gateways do this the wrong way

    def to_dict(self):
        return {'success': self.success,
                'message': self.message,
                'params': self.params,
                'test': self.test,
                'authorization': self.authorization,
                'fraud_review': self.fraud_review}

