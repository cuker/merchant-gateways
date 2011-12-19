"""
Provides a poor man's xml <=> python translactions
Meant to be dead simple, but the ordered multi value dict is not!
"""
import random
import string
from types import GeneratorType
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

def gencode(length=16, chars=(string.uppercase+string.lowercase+string.digits)):
    return ''.join([random.choice(chars) for i in range(length)])

class MultiValueDictKeyError(KeyError):
    pass

class OrderedMultiValueDict(dict): #Shameless copy from django, Thank you django devs!
    """
    A subclass of dictionary customized to handle multiple values for the
    same key.

    >>> d = MultiValueDict({'name': ['Adrian', 'Simon'], 'position': ['Developer']})
    >>> d['name']
    'Simon'
    >>> d.getlist('name')
    ['Adrian', 'Simon']
    >>> d.get('lastname', 'nonexistent')
    'nonexistent'
    >>> d.setlist('lastname', ['Holovaty', 'Willison'])

    This class exists to solve the irritating problem raised by cgi.parse_qs,
    which returns a list for every key, even though most Web forms submit
    single name-value pairs.
    """
    def __init__(self, data=()):
        if isinstance(data, GeneratorType):
            # Unfortunately we need to be able to read a generator twice.  Once
            # to get the data into self with our super().__init__ call and a
            # second time to setup keyOrder correctly
            data = list(data)
        if isinstance(data, (list, tuple)):
            processed_data = data
            data = list()
            for key, value in processed_data:
                if not isinstance(value, list):
                    value = [value]
                data.append((key, value))
        super(OrderedMultiValueDict, self).__init__(data)
        if hasattr(data, 'keyOrder'):
            self.keyOrder = list(data.keyOrder)
        elif isinstance(data, dict):
            self.keyOrder = data.keys()
        else:
            self.keyOrder = []
            for key, value in data:
                if key not in self.keyOrder:
                    self.keyOrder.append(key)

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__,
                             ', '.join("'%s': %s" % (key, value) for key, value in self.iteritems()))

    def __getitem__(self, key):
        """
        Returns the last data value for this key, or [] if it's an empty list;
        raises KeyError if not found.
        """
        try:
            list_ = super(OrderedMultiValueDict, self).__getitem__(key)
        except KeyError:
            raise MultiValueDictKeyError("Key %r not found in %r" % (key, self))
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        super(OrderedMultiValueDict, self).__setitem__(key, [value])

    def __delitem__(self, key):
        super(OrderedMultiValueDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        return iter(self.keyOrder)

    def __copy__(self):
        return self.__class__(super(OrderedMultiValueDict, self).items())

    def __deepcopy__(self, memo=None):
        import django.utils.copycompat as copy
        if memo is None:
            memo = {}
        result = self.__class__()
        memo[id(self)] = result
        for key, value in dict.items(self):
            dict.__setitem__(result, copy.deepcopy(key, memo),
                             copy.deepcopy(value, memo))
        return result

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict['_data'] = dict([(k, self.getlist(k)) for k in self])
        return obj_dict

    def __setstate__(self, obj_dict):
        data = obj_dict.pop('_data', {})
        for k, v in data.items():
            self.setlist(k, v)
        self.__dict__.update(obj_dict)
    
    def keys(self):
        return self.keyOrder[:]

    def iterkeys(self):
        return iter(self.keyOrder)

    def get(self, key, default=None):
        """
        Returns the last data value for the passed key. If key doesn't exist
        or value is an empty list, then default is returned.
        """
        try:
            val = self[key]
        except KeyError:
            return default
        if val == []:
            return default
        return val

    def getlist(self, key):
        """
        Returns the list of values for the passed key. If key doesn't exist,
        then an empty list is returned.
        """
        try:
            return super(OrderedMultiValueDict, self).__getitem__(key)
        except KeyError:
            return []

    def setlist(self, key, list_):
        if key not in self:
            self.keyOrder.append(key)
        super(OrderedMultiValueDict, self).__setitem__(key, list_)

    def setdefault(self, key, default=None):
        if key not in self:
            self.keyOrder.append(key)
            self[key] = default
        return self[key]

    def setlistdefault(self, key, default_list=()):
        if key not in self:
            self.setlist(key, default_list)
        return self.getlist(key)

    def appendlist(self, key, value):
        """Appends an item to the internal list associated with key."""
        self.setlistdefault(key, [])
        super(OrderedMultiValueDict, self).__setitem__(key, self.getlist(key) + [value])

    def items(self):
        """
        Returns a list of (key, value) pairs, where value is the last item in
        the list associated with the key.
        """
        return [(key, self[key]) for key in self.iterkeys()]

    def iteritems(self):
        """
        Yields (key, value) pairs, where value is the last item in the list
        associated with the key.
        """
        for key in self.iterkeys():
            yield (key, self[key])

    def lists(self):
        """Returns a list of (key, list) pairs."""
        return [(key, self.getlist(key)) for key in self.iterkeys()]

    def iterlists(self):
        """Yields (key, list) pairs."""
        for key in self.iterkeys():
            yield (key, self.getlist(key))

    def values(self):
        """Returns a list of the last value on every key list."""
        return [self[key] for key in self.iterkeys()]

    def itervalues(self):
        """Yield the last value on every key list."""
        for key in self.iterkeys():
            yield self[key]

    def copy(self):
        """Returns a copy of this object."""
        return self.__deepcopy__()

    def update(self, *args, **kwargs):
        """
        update() extends rather than replaces existing key lists.
        Also accepts keyword args.
        """
        if len(args) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(args))
        if args:
            other_dict = args[0]
            if isinstance(other_dict, OrderedMultiValueDict):
                for key, value_list in other_dict.lists():
                    self.setlistdefault(key, []).extend(value_list)
            else:
                try:
                    for key, value in other_dict.items():
                        self.setlistdefault(key, []).append(value)
                except TypeError:
                    raise ValueError("MultiValueDict.update() takes either a MultiValueDict or dictionary")
        for key, value in kwargs.iteritems():
            self.setlistdefault(key, []).append(value)

    def clear(self):
        super(OrderedMultiValueDict, self).clear()
        self.keyOrder = []
    
    def pop(self, k, *args):
        result = super(OrderedMultiValueDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def value_for_index(self, index):
        """Returns the value of the item at the given zero-based index."""
        return self[self.keyOrder[index]]

    def insert(self, index, key, value):
        """Inserts the key, value pair before the item with the given index."""
        if key in self.keyOrder:
            n = self.keyOrder.index(key)
            del self.keyOrder[n]
            if n < index:
                index -= 1
        self.keyOrder.insert(index, key)
        super(OrderedMultiValueDict, self).__setitem__(key, value)

class XMLDict(OrderedMultiValueDict):
    def __init__(self, key_to_list_mapping=(), attrib={}):
        super(XMLDict, self).__init__(key_to_list_mapping)
        self.attrib = attrib
        self.text = None
    
    def __nonzero__(self):
        return bool(len(self) or len(self.attrib))
    
    def __repr__(self):
        if self.attrib:
            return "<%s (%s)>" % (super(XMLDict, self).__repr__(), 
                                  self.attrib)
        return "<%s>" % super(XMLDict, self).__repr__()
    
    def to_xml(self, parent):
        dicttoxml(self, parent)

class _ShowEmpty(unicode):
    def __nonzero__(self):
        return True

SHOW_EMPTY = _ShowEmpty(u'')

def _handle_attrib(element, obj):
    if hasattr(obj, 'attrib'):
        element.attrib.update(obj.attrib)

def pytoxml(key, obj, parent):
    if hasattr(obj, 'iterlists'):
        container = ET.SubElement(parent, key)
        _handle_attrib(container, obj)
        for key, lists in obj.iterlists():
            pytoxml(key, lists, container)
    elif hasattr(obj, 'iteritems'):
        container = ET.SubElement(parent, key)
        _handle_attrib(container, obj)
        for key, value in obj.iteritems():
            pytoxml(key, value, container)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            pytoxml(key, value, parent)
    else:
        container = ET.SubElement(parent, key)
        _handle_attrib(container, obj)
        if obj is not None:
            if isinstance(obj, basestring):
                container.text = obj
            elif isinstance(obj, bool):
                container.text = obj and 'true' or 'false'
            else:
                container.text = unicode(obj)

def dicttoxml(dictionary, parent):
    if hasattr(dictionary, 'iterlists'):
        iterator = dictionary.iterlists()
    else:
        iterator = dictionary.iteritems()
    for key, value in iterator:
        pytoxml(key, value, parent)

def listtoxml(iterable, parent):
    for value in iterable:
        dicttoxml(value, parent)

def xmltodict(element, strip_namespaces=False):
    ret = XMLDict(attrib=element.attrib)
    if element.text:
        ret.text = element.text
    for item in element.getchildren():
        tag = item.tag
        if strip_namespaces:
            tag = tag.split('}')[-1]
        if item.text:
            ret.appendlist(tag, item.text)
        if len(element.getchildren()):
            subitem = xmltodict(item, strip_namespaces)
            if subitem:
                ret.appendlist(tag, subitem)
    return ret

#lxml quickies

from lxml.builder import ElementMaker

def xStr(doc):
    from lxml import etree
    return etree.tostring(doc, pretty_print=True)
