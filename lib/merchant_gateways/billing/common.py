"""
Provides a poor man's xml <=> python translactions
Meant to be dead simple!
"""

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

class MultiValueDictKeyError(KeyError):
    pass

class MultiValueDict(dict): #Shameless copy from django, Thank you django devs!
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
    def __init__(self, key_to_list_mapping=()):
        super(MultiValueDict, self).__init__(key_to_list_mapping)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,
                             super(MultiValueDict, self).__repr__())

    def __getitem__(self, key):
        """
        Returns the last data value for this key, or [] if it's an empty list;
        raises KeyError if not found.
        """
        try:
            list_ = super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            raise MultiValueDictKeyError("Key %r not found in %r" % (key, self))
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        super(MultiValueDict, self).__setitem__(key, [value])

    def __copy__(self):
        return self.__class__(super(MultiValueDict, self).items())

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
            return super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            return []

    def setlist(self, key, list_):
        super(MultiValueDict, self).__setitem__(key, list_)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def setlistdefault(self, key, default_list=()):
        if key not in self:
            self.setlist(key, default_list)
        return self.getlist(key)

    def appendlist(self, key, value):
        """Appends an item to the internal list associated with key."""
        self.setlistdefault(key, [])
        super(MultiValueDict, self).__setitem__(key, self.getlist(key) + [value])

    def items(self):
        """
        Returns a list of (key, value) pairs, where value is the last item in
        the list associated with the key.
        """
        return [(key, self[key]) for key in self.keys()]

    def iteritems(self):
        """
        Yields (key, value) pairs, where value is the last item in the list
        associated with the key.
        """
        for key in self.keys():
            yield (key, self[key])

    def lists(self):
        """Returns a list of (key, list) pairs."""
        return super(MultiValueDict, self).items()

    def iterlists(self):
        """Yields (key, list) pairs."""
        return super(MultiValueDict, self).iteritems()

    def values(self):
        """Returns a list of the last value on every key list."""
        return [self[key] for key in self.keys()]

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
            if isinstance(other_dict, MultiValueDict):
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

class XMLDict(MultiValueDict):
    def __init__(self, key_to_list_mapping=(), attrib={}):
        super(XMLDict, self).__init__(key_to_list_mapping)
        self.attrib = attrib
    
    def __nonzero__(self):
        return bool(len(self) or len(self.attrib))
    
    def to_xml(self, parent):
        dicttoxml(self, parent)

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
            container.text = unicode(obj)

def dicttoxml(dictionary, parent):
    for key, value in dictionary.iteritems():
        pytoxml(key, value, parent)

def listtoxml(iterable, parent):
    for value in iterable:
        dicttoxml(value, parent)

def xmltodict(element):
    ret = XMLDict(attrib=element.attrib)
    for item in element.getchildren():
        if item.text:
            ret.appendlist(item.tag, item.text)
        if len(element.getchildren()):
            subitem = xmltodict(item)
            if subitem:
                ret.appendlist(item.tag, subitem)
    return ret

# Below is all the functionality we needed from lxml, but mapped to element tree
# lxml is no longer necessary

class ElementMaker(object):
    def __init__(self, key=None):
        self.key = key
        self.value = None
        self.children = XMLDict()
    
    def __call__(self, *elements, **attrib):
        if not self.key:
            return type(self)(elements[0])(*elements[1:], **attrib)
        elements = list(elements)
        if elements and not isinstance(elements[0], ElementMaker):
            self.value = unicode(elements.pop(0))
        for element in elements:
            if element.value is not None:
                self.children.appendlist(element.key, element.value)
            if element.children:
                self.children.appendlist(element.key, element.children)
        self.children.attrib = attrib
        return self
    
    def __getattr__(self, key):
        return type(self)(key)
    
    def to_xml(self):
        root = ET.Element(self.key)
        root.attrib = self.children.attrib
        dicttoxml(self.children, root)
        return root

def xStr(element_maker):
    return ET.tostring(element_maker.to_xml())
