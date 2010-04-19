import urllib2

def post(url, data, headers={}):
    # print 'nononono' TODO  squawk if this calls in test mood
    request = urllib2.Request(url=url, data=data, headers=headers)
    response = urllib2.urlopen(request)
    return response.read()
