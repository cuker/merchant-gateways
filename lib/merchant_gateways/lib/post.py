import urllib2
import urllib


def post(url, data, headers={}):
    # print 'nononono' TODO  fault if this calls in test mode

    if not getattr(data, 'split', False):  #  TODO  take the if out
        for key, value in data.iteritems():
            data[key] = value.encode('utf-8')
        data = urllib.urlencode(data)

    request = urllib2.Request(url=url, data=data, headers=headers)
    # print url, data
    response = urllib2.urlopen(request)
    rebound = response.read()
    # print rebound #  TODO  clean out these prints
    return rebound
