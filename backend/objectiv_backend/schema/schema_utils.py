

class SchemaEntity(dict):
    """
    Base class, extends dict, so we can use objects as dictionaries, but this also
    enables json support ootb (Without custom serialisation methods.


    Here we add the '_type' or 'event' properties, so we can json serialize, without losing
    info on what kind of object it was
    """
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        if hasattr(self, '_type'):
            self['_type'] = self._type
        else:
            # this should never happen! But better safe than sorry
            raise Exception(f'Unknown entity / missing attributes in {type(self)}')

    def __getattr__(self, item):
        """
        wrapper to allow attribute access to dictionary values by key
        :param item:
        :return:
        """
        try:
            return self[item]
        except KeyError:
            raise AttributeError
