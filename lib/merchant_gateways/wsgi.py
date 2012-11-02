from cgi import parse_qs
from urlib import urlencode

def get_first_or_none(post_data, key):
    val = post_data.get(key, [])
    if len(val):
        return val[0]
    return None

class BaseDirectPostApplication(object):
    encrypted_field = 'payload'
    protected_fields = ['currency', 'amount', 'gateway', 'action']
    
    def __init__(self, redirect_to):
        self.redirect_to = redirect_to
        self.gateways = self.load_gateways()
    
    def load_gateways(self):
        raise NotImplementedError
    
    def decrypt_data(self, encrypted_data):
        raise NotImplementedError
    
    def encrypt_data(self, params):
        raise NotImplementedError
    
    def process_direct_post(self, post_data):
        #encrypted data gives us our necessary sensitive variables: currency, amount, gateway, etc
        encrypted_data = get_first_or_none(post_data, self.encrypted_field)
        decrypted_data = self.decrypt_data(encrypted_data)
        gateway = self.gateways[decrypted_data['gateway']]
        assert gateway.supports_action(decrypted_data['action'])
        #TODO gateway.process_direct_post
        response = gateway.process_direct_post(post_data, decrypted_data)
        #TODO things left to encode in the response:
        #EXCLUDE: response.result -> this contains the entire payload coming back
        #other: card_type, card_expiration, card_masked (4*****1111)
        #amount
        #TODO pass through params
        response_params = {
            'success': response.success,
            'fraud_review': response.fraud_review,
            'message': response.message,
            'result': response.result,
            'card_store_id': response.card_store_id,
            'authorization': response.authorization,
            'avs': response.avs_code,
            'cvv': response.cvv_code,
        }
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

class DirectPostMiddleware(object):
    def __init__(self, main_application, direct_post_application, url_endpoint):
        self.main_application = main_application
        self.direct_post_application = direct_post_application
        self.url_endpoint = url_endpoint
    
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == self.url_endpoint:
            return self.direct_post_application(environ, start_response)
        return self.main_application(environ, start_response)

