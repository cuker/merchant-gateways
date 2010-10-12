try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

def dicttoxml(dictionary, parent):
    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            dicttoxml(value, ET.SubElement(parent, key))
        elif isinstance(value, list):
            listtoxml(value, ET.SubElement(parent, key))
        else:
            child = ET.SubElement(parent, key)
            if value is not None:
                child.text = unicode(value)

def listtoxml(iterable, parent):
    for value in iterable:
        dicttoxml(value, parent)

def xmltodict(element):
    ret = dict()
    ret['_attributes'] = dict(element.items())
    for item in element.getchildren():
        if item.text:
            ret[item.tag] = item.text
        if len(element.getchildren()):
            subitem = xmltodict(item)
            if subitem:
                ret[item.tag] = subitem
    return ret

