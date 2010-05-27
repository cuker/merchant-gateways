import urllib2

def post(url, data, headers={}):
    # print 'nononono' TODO  fault if this calls in test mode
    request = urllib2.Request(url=url, data=data, headers=headers)
    response = urllib2.urlopen(request)
    return response.read()
