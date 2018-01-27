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
    >>> meta = {('int', lambda _: _.replace(',')): ['https://www.wikidata.org/wiki/Q82799']}

    Returns:
    >>> key = 'Q82799'
    >>> value = 1234
    '''

    schema, types = list(meta.keys()) + list(meta.values())

    if schema:
        # value
        for index, operation in enumerate(schema):
            if index == 0:
                # value = eval(operation)(value)
                continue
            elif index == 1:
                value = eval(operation)(value)

        value = eval(schema[0])(value)

    if types:
        # key
        for index, typeurl in enumerate(types):
            if index == 0:
                key = typeurl.rsplit('/',1)[-1]

    return key, value


def prepare_keys(schema):

    def visit(path, key, value):
        if key == '' and isinstance(value, list):
            return key, tuple(value)
        return key, value

    remapped = remap(schema, visit=visit)
    return remapped


def zip_metadata(schemas, types, if_schema_value_type=tuple):
    '''
    Create metadata from schemas and types by zipping tree.

    Given:
    >>> schemas = [{'': 'S',
  'address': {'': 'S', 'number': {'': 'S'}, 'street': {'': 'S'}},
  'children': [{'': 'S', 'age': {'': 'S'}, 'name': {'': 'S'}}],
  'name': {'': 'S'}}]
    >>> types = [{'': 'Q',
  'address': {'': 'Q', 'number': {'': 'Q'}, 'street': {'': 'Q'}},
  'children': [{'': 'Q', 'age': {'': 'Q'}, 'name': {'': 'Q'}}],
  'name': {'': 'Q'}}]

    Returns:
    >>> make_metadata(schemas, types, if_schema_value_type=str)
    [{'S': 'Q',
  'address': {'S': 'Q', 'number': {'S': 'Q'}, 'street': {'S': 'Q'}},
  'children': [{'S': 'Q', 'age': {'S': 'Q'}, 'name': {'S': 'Q'}}],
  'name': {'S': 'Q'}}]

    Given:
    >>> schemas = [{
    '': ('obj',),
    'name': {
        '': ('str',)
    },
    'address': {
        '': ('obj',),
        'number': {
            '': ('int', lambda _: int(_))
        },
        'street': {
            '': ('str',)
        }
    },
    'children': [{
        '': ('obj',),
        'name': {
            '': ('str',)
        },
        'age': {
            '': ('int', lambda _: float(_))
        }
    }]
}]
    >>> types = [{
    '': ['https://www.wikidata.org/wiki/Q7565'],
    'name': {
        '': ['https://www.wikidata.org/wiki/Q82799']
    },
    'address': {
        '': ['https://www.wikidata.org/wiki/Q319608'],
        'number': {
            '': ['https://www.wikidata.org/wiki/Q1413235']
        },
        'street': {
            '': ['https://www.wikidata.org/wiki/Q24574749']
        }
    },
    'children': [{
        '': ['https://www.wikidata.org/wiki/Q7569'],
        'name': {
            '': ['https://www.wikidata.org/wiki/Q82799']
        },
        'age': {
            '': ['https://www.wikidata.org/wiki/Q185836']
        }
    }]
}]

    >>> zip_metadata(types, schemas)
    [{('obj',): ['https://www.wikidata.org/wiki/Q7565'],
  'address': {('obj',): ['https://www.wikidata.org/wiki/Q319608'],
   'number': {('int',
     <function __main__.<lambda>>): ['https://www.wikidata.org/wiki/Q1413235']},
   'street': {('str',): ['https://www.wikidata.org/wiki/Q24574749']}},
  'children': [{('obj',): ['https://www.wikidata.org/wiki/Q7569'],
    'age': {('int',
      <function __main__.<lambda>>): ['https://www.wikidata.org/wiki/Q185836']},
    'name': {('str',): ['https://www.wikidata.org/wiki/Q82799']}}],
  'name': {('str',): ['https://www.wikidata.org/wiki/Q82799']}}]
    '''
    def visit(path, key, value): 
        if isinstance(value, if_schema_value_type):
            return list(dictget(schemas, path).values())[0], list(dictget(types, path).values())[0]
        return key, value

    remapped = remap(schemas, visit=visit)

    return remapped


def add_metadata(data, metadata):
    '''
    Visit every place of nested list, dict, tuples, and apply metadata to data.

    Given:
    >>> data = [
    {'name': 'Max', 'address': {'street': 'Leonardo str.', 'number': 14}, 'children': [{'name': 'Mike', 'age': 1}, {'name': 'Tom', 'age': 15}]},
    {'name': 'Lin', 'address': {'street': 'Mao str.', 'number': 12}, 'children': [{'name': 'Sonnie', 'age': 10}]},
    {'name': 'Dim', 'address': {'street': 'Nexus str.', 'number': 1}, 'children': [{'name': 'Deli', 'age': 1}, {'name': 'Miki', 'age': 7}]}
]
    >>> metadata = [{
    ('obj',): ['https://www.wikidata.org/wiki/Q7565'],
    'name': {
        ('str',): ['https://www.wikidata.org/wiki/Q82799']
    },
    'address': {
        ('obj',): ['https://www.wikidata.org/wiki/Q319608'],
        'number': {
            ('int', 'lambda _: int(_)'): ['https://www.wikidata.org/wiki/Q1413235']
        },
        'street': {
            ('str',): ['https://www.wikidata.org/wiki/Q24574749']
        }
    },
    'children': [{
        ('obj',): ['https://www.wikidata.org/wiki/Q7569'],
        'name': {
            ('str',): ['https://www.wikidata.org/wiki/Q82799']
        },
        'age': {
            ('int', 'lambda _: float(_)'): 
               ['https://www.wikidata.org/wiki/Q185836']
        }
    }]
}]

    Returns:
    >>> [{'Q82799': 'Max',
  'address': {'Q1413235': 14, 'Q24574749': 'Leonardo str.'},
  'children': [{'Q185836': 1, 'Q82799': 'Mike'},
   {'Q185836': 15, 'Q82799': 'Tom'}]},
 {'Q82799': 'Lin',
  'address': {'Q1413235': 12, 'Q24574749': 'Mao str.'},
  'children': [{'Q185836': 10, 'Q82799': 'Sonnie'}]},
 {'Q82799': 'Dim',
  'address': {'Q1413235': 1, 'Q24574749': 'Nexus str.'},
  'children': [{'Q185836': 1, 'Q82799': 'Deli'},
   {'Q185836': 7, 'Q82799': 'Miki'}]}]
    '''

    def visit(path, key, value):

        try:
            meta = dictget(metadata, metapath(path))[key if not isinstance(key, int) else 0]
        except:
            return key, value

        if not any([isinstance(value, t) for t in [dict, list, tuple]]):
            return convert(key, value, meta)
        else:
            return key, value


    remapped = remap(data, visit=visit)

    return remapped

def localize_data(data, lang='xx'):
    pass
