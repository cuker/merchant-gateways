from cgi import parse_qs
from urlib import urlencode

def get_first_or_none(post_data, key):
    val = post_data.get(key, [])
    if len(val):
        return val[0]
    return None

def flatten_dictionary(dictionary):
    new_dict = dict()
    for key, values in dictionary.items():
        new_dict[key] = values[0]
    return new_dict

class BaseDirectPostApplication(object):
    encrypted_field = 'payload'
    protected_fields = ['currency', 'amount', 'gateway', 'action', 'passthrough']
    
    def __init__(self, redirect_to):
        self.redirect_to = redirect_to
        self.gateways = self.load_gateways()
    
    def load_gateways(self):
        """
        Returns a dictionary of gateway objects
        """
        raise NotImplementedError
    
    def decrypt_data(self, encrypted_data):
        """
        Takes an encoded string and returns a dictionary
        """
        raise NotImplementedError
    
    def encrypt_data(self, params):
        """
        Takes a dictionary and returns a string
        """
        raise NotImplementedError
    
    def process_direct_post(self, post_data):
        post_data = flatten_dictionary(post_data)
        #encrypted data gives us our necessary sensitive variables: currency, amount, gateway, etc
        encrypted_data = post_data[self.encrypted_field]
        decrypted_data = self.decrypt_data(encrypted_data)
        gateway_key = decrypted_data['gateway']
        gateway = self.gateways[gateway_key]
        action = decrypted_data['action']
        assert gateway.supports_action(action)
        #should return dict containing: response, credit_card, passthrough, amount, currency_code
        expanded_response = gateway.process_direct_post(post_data, decrypted_data)
        response = expanded_response['response']
        response_params = expanded_response.get('passthrough', {})
        response_params.update({
            'action': action,
            'gateway': decrypted_data['gateway'],
            'success': response.success,
            'fraud_review': response.fraud_review,
            'message': response.message,
            'result': response.result,
            'card_store_id': response.card_store_id,
            'authorization': response.authorization,
            'avs': response.avs_code,
            'cvv': response.cvv_code,
        })
        if 'credit_card' in expanded_response:
            credit_card = expanded_response['credit_card']
            response_params['cc_last4'] = credit_card.number[-4:]
            response_params['cc_exp_month'] = credit_card.month
            response_params['cc_exp_year'] = credit_card.year
            response_params['cc_type'] = credit_card.card_type
        if 'amount' in expanded_response:
            response_params['amount'] = expanded_response['amount']
        if 'currency_code' in expanded_response:
            response_params['currency_code'] = expanded_response['currency_code']
        return response_params
    
    def render_bad_request(self, environ, start_response, response_body):
        status = '405 METHOD NOT ALLOWED'
        
        response_headers = [('Content-Type', 'text/html'),
                      ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        
        return [response_body]
    
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'].upper() != 'POST':
            return self.render_bad_request(environ, start_response, "Request method must me a post")
        
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        
        # When the method is POST the query string will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        #dictionary of arrays:
        post_data = parse_qs(request_body)
        
        response_params = self.process_direct_post(post_data)
        params = {self.encrypted_field: self.encrypt_data(response_params)}
        
        response_body = '%s?%s' % (self.redirect_to, urlencode(params))
        
        status = '303 SEE OTHER'
        
        response_headers = [('Content-Type', 'text/html'),
                      ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        
        return [response_body]

class DjangoDirectPostApplication(BaseDirectPostApplication):
    """
    Uses django's signing mechanism to encrypt and decrypt payloads
    Requires Django 1.4 or later
    """
    salt_namespace = 'merchant_gateways.wsgi'
    
    def load_gateways(self):
        """
        Returns a dictionary of gateway objects
        """
        #TODO load from settings
        raise NotImplementedError
    
    def decrypt_data(self, encrypted_data):
        """
        Takes an encoded string and returns a dictionary
        """
        from django.core.signing import loads
        return loads(encrypted_data, salt=self.salt_namespace)
    
    def encrypt_data(self, params):
        """
        Takes a dictionary and returns a string
        """
        from django.core.signing import dumps
        return dumps(params, salt=self.salt_namespace)

class DirectPostMiddleware(object):
    def __init__(self, main_application, direct_post_application, url_endpoint):
        self.main_application = main_application
        self.direct_post_application = direct_post_application
        self.url_endpoint = url_endpoint
    
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == self.url_endpoint:
            return self.direct_post_application(environ, start_response)
        return self.main_application(environ, start_response)

