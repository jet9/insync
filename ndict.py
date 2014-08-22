class NDict(dict):
    """
    Custom dict class for access items thru methods:

    >>> d = { 'a': 1, 'b': { 'c': 'foo', 'd': True, 'e': [1,2,3,{ 'f': 'good'}] }}
    >>> d = NDict(d)
    >>> d.a
    1
    >>> d.b.c
    'foo'
    >>> d.b.e[2]
    3
    >>> d.b.e[3]
    {'f': 'good'}
    >>> d.b.e[3].f
    'good'

    """

    def __init__(self, data=None):
        """
        Constructor:

         > data DICT: dict for conversion to NDict
        """
        if data is not None:
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        p=[]
                        for x in v:
                            if isinstance(x, dict):
                                p.append(NDict(x))
                            else:
                                p.append(x)
                        self[k] = p

                    elif isinstance(v, dict):
                        self[k] = NDict(v)

                    else:
                        self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def dict(self):
        """
        Return NDict instance as dict:

        >>> d.dict()
        {'a': 1, 'b': {'c': 'foo', 'e': [1, 2, 3, {'f': 'good'}], 'd': True}}
        >>> d = d.dict()
        >>> d.a
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        AttributeError: 'dict' object has no attribute 'a'
        >>> d['a']
        1
        """
        def ndict2dict(data):
            if isinstance(data, list):
                return [ndict2dict(x) for x in data]
            elif isinstance(data, NDict) or isinstance(data, dict):
                r = {}
                for k, v in data.items():
                    r[k] = ndict2dict(v)
                return r
            else:
                return data

        return ndict2dict(self)

if __name__ == "__main__":
    d = { 'a': 1, None: "test",3: 555, 'b': { 'c': 'foo', 'd': True, 'e': [1,2,3,{ 'f': 'good'}] }}
    d = NDict(d)
    print d.a
    print d[None]
    print d.b.c
    print d.b.e[2]
    print d.b.e[3]
    print d.b.e[3].f