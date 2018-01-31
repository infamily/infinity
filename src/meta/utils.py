from boltons.iterutils import remap
from functools import reduce
import operator

def dictget(d, mapList):
    '''
    Given:
    >>> d = {'a': [{'b': 'c'}, {'e': 'f'}, {'g': 'h'}]}

    Returns:
    >>> dictget(d, ['a', 2, 'b'])
    >>> 'c'
    '''
    return reduce(operator.getitem, mapList, d)

def metapath(path):
    '''
    Given:
    >>> p = [1, 'a', 2, 'b', 3]

    Returns:
    >>> metapath(p)
    >>> [0, 'a', 0, 'b', 0]
    '''
    metapath = []
    for item in path:
        if isinstance(item, int):
            metapath.append(0)
        else:
            metapath.append(item)
    return metapath


def convert(key, value, meta):
    '''
    Given:
    >>> key = 'something'
    >>> value = '1,234'
    >>> meta = {'': [('int', lambda _: _.replace(',')), ['https://www.wikidata.org/wiki/Q82799']]}

    Returns:
    >>> key = 'Q82799'
    >>> value = 1234
    '''

    schema, types = list(meta.keys()) + list(meta.values())


    if schema:

        for index, operation in enumerate(schema):
            if index == 0:
                continue
            elif index == 1:
                value = eval(operation)(value)

        try:
            value = eval(schema[0])(value)
        except:
            pass

    if types:

        for index, typeurl in enumerate(types):
            if index == 0:
                key = typeurl.rsplit('/',1)[-1]

    return key, value

def standardize(data, metadata, if_schema_value_type=tuple):
    '''
    Combine data with schema and types in metadata by zipping tree.

    Given:
    >>> data = [{'address': {'number': 14, 'street': 'Leonardo str.'},
  'children': [{'age': 1, 'name': 'Mike'}, {'age': 15, 'name': 'Tom'}],
  'name': 'Max'},
 {'address': {'number': 12, 'street': 'Mao str.'},
  'children': [{'age': 10, 'name': 'Sonnie'}],
  'name': 'Lin'},
 {'address': {'number': 1, 'street': 'Nexus str.'},
  'children': [{'age': 1, 'name': 'Deli'}, {'age': 7, 'name': 'Miki'}],
  'name': 'Dim'}]

    >>> metadata = [{'': [('obj',), ['https://www.wikidata.org/wiki/Q7565']],
  'address': {'': [('obj',), ['https://www.wikidata.org/wiki/Q319608']],
   'number': {'': [('int', 'lambda _: int(_)'), ['https://www.wikidata.org/wiki/Q1413235']]},
   'street': {'': [('str',), ['https://www.wikidata.org/wiki/Q24574749']]}},
  'children': [{'': [('obj',), ['https://www.wikidata.org/wiki/Q7569']],
    'age': {'': [('int', 'lambda _: float(_)'), ['https://www.wikidata.org/wiki/Q185836']]},
    'name': {'': [('str',), ['https://www.wikidata.org/wiki/Q82799']]}}],
  'name': {'': [('str',), ['https://www.wikidata.org/wiki/Q82799']]}}]

    Returns:
    >>> standardize(data, metadata)
    [{'Q319608': {'Q1413235': 14, 'Q24574749': 'Leonardo str.'},
  'Q7569': [{'Q185836': 1, 'Q82799': 'Mike'},
   {'Q185836': 15, 'Q82799': 'Tom'}],
  'Q82799': 'Max'},
 {'Q319608': {'Q1413235': 12, 'Q24574749': 'Mao str.'},
  'Q7569': [{'Q185836': 10, 'Q82799': 'Sonnie'}],
  'Q82799': 'Lin'},
 {'Q319608': {'Q1413235': 1, 'Q24574749': 'Nexus str.'},
  'Q7569': [{'Q185836': 1, 'Q82799': 'Deli'},
   {'Q185836': 7, 'Q82799': 'Miki'}],
  'Q82799': 'Dim'}]
    '''

    def visit(path, key, value):
        try:
            meta = dictget(metadata, metapath(path))[key if not isinstance(key, int) else 0]
        except:
            return key, value

        if not any([isinstance(value, t) for t in [dict, list, tuple]]):

            k, v = list(meta.values())[0]
            metamap = {tuple(k): v}

            return convert(key, value, metamap)
        else:
            if isinstance(key, str):
                try:
                    k, v = list(meta)[0]['']
                except:
                    try:
                        k, v = meta['']
                    except:
                        pass

                try:
                    metamap = {tuple(k): v}

                    key, _ = convert(key, value, metamap)
                except:
                    pass

                return key, value

            return key, value


    remapped = remap(data, visit=visit)
    return remapped


def normalize(data):
    return standardize(data[1:], metadata=data[0:1])

