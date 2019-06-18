"""
Extended type:
    ExtList, rewrite multiple operation

    ExtDict, rewrite getitem so that '/a/b/c/d' -> ['a']['b']['c']['d']
"""
from collections import Iterable, Counter, OrderedDict



NO_DEFAULT = '__THIS_MEANS_NO_DEFAULT__'
class ExtList(list):
    """
    Extended list
    """
    def __mul__(self, a):
        assert isinstance(a, Iterable),\
            'multiplier should be Iterable, instead of {1}'.format(a, type(a))
        assert len(self) == len(a),\
            'multiple length should be same'
        return self.__class__([x for i, x in enumerate(self) for time in range(a[i])])

    def __sub__(self, a):
        if not a in self:
            return self
        result = ExtList(self.copy())
        result.pop(result.index(a))
        return result

    def contract_items(self, outtype=None):
        _contract_items = []
        for i, item in enumerate(self):
            if i==0 or item != self[i-1]:
                _contract_items.append(item)
        if outtype == 'string':
            _contract_items = ' '.join(str(_) for _ in _contract_items)
        return _contract_items

    def contract_numbers(self, outtype=None):
        _contract_numbers = []
        num = 0
        for i, item in enumerate(self):
            if i==0 or item == self[i-1]:
                num += 1
            else:
                _contract_numbers.append(num)
                num = 1
        if num != 0:
            _contract_numbers.append(num)
        if outtype == 'string':
            _contract_numbers = ' '.join(str(_) for _ in _contract_numbers)
        return _contract_numbers

    def __get_counts(self):
        counts = OrderedDict()
        for i in self:
            counts[i] = counts.get(i, 0) + 1
        return counts

    def deep_contract_items(self, outtype=None):
        _contract_items = self.__get_counts().keys()
        if outtype == 'string':
            _contract_items = ' '.join(str(_) for _ in _contract_items)
        return _contract_items

    def deep_contract_numbers(self, outtype=None):
        _contract_numbers = self.__get_counts().values()
        if outtype == 'string':
            _contract_numbers = ' '.join(str(_) for _ in _contract_numbers)
        return _contract_numbers

    def deep_contract_index(self):
        # import pdb; pdb.set_trace()
        counts = OrderedDict()
        for i, item in enumerate(self):
            if counts.get(item, None) is None:
                counts[item] = [i]
            else:
                counts[item].append(i)
        index = []
        for i in counts.values():
            index += i
        return index


class ExtDict(dict):
    """
    Extended Dict
    the array get from gaseio.read is a ExtDict
    """

    def __getitem__(self, name):
        if name in self.keys():
            return dict.__getitem__(self, name)
        name = name.split('/')
        sdict = self
        while name:
            key = name.pop(0)
            if not key:
                continue
            if not key in sdict.keys():
                raise KeyError('{0} not exist'.format(key))
            sdict = sdict[key]
        return sdict

    def __getattr__(self, name):
        if name.startswith('__'):
            return dict.__getattr__(name)
        if name.startswith('get_'):
            _name = name[len('get_'):]
            return lambda : self['calc_arrays'].get(_name, None) \
                            if self.get(_name, None) is None and dict.get(self, 'calc_arrays', None) \
                            else self.get(_name, None)
        return dict.__getitem__(self, name)

    def has_key(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    def get_all_keys(self, basename='', depth=10000):
        result = []
        if depth == 0:
            return result
        for key, val in self.items():
            keyname = basename+'/'+key
            if isinstance(val, dict):
                result += ExtDict.get_all_keys(val, keyname, depth-1)
            else:
                result.append(keyname)
        return result

    # def get(self, key, default=NO_DEFAULT):
    #     if key == 'defines' : 
    #         import pdb; pdb.set_trace()
    #     if self[key] is not None:
    #         return self[key]
    #     elif default != NO_DEFAULT:
    #         return default
    #     raise KeyError(key, 'not found')
        

