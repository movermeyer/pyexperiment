"""Provide flat, point separated interface to nested mapping
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Python 3 compatibility
from six import iteritems, iterkeys

from collections import MutableMapping


class DotSeparatedNestedMapping(  # pylint: disable=too-many-ancestors
        MutableMapping):
    """ABC for flat mutable mappings where all keys are strings, levels
    and the storage is implemented as a hierarchy of nested Mutable
    mappings.
    """
    @classmethod
    def _new_section(cls):
        """Creates a new section Mapping
        """
        raise NotImplementedError("Subclass should implement this")

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        raise NotImplementedError("Subclass should implement this")

    def __init__(self):
        """Initializer
        """
        self.base = None

    def __descend_sections(self, key, create=False):
        """Traverse the nested mappings down to the last layer
        """
        if self.base is None:
            raise KeyError("Cannot access key in empty mapping")
        try:
            split_name = key.split(".")
        except AttributeError() as err:
            raise KeyError("Key must be a string ('%s')", err)
        level = 0
        section = self.base
        # Iterate through the sections
        while level < len(split_name) - 1:
            try:
                section = section[split_name[level]]
                level += 1
            except KeyError as err:
                if not create:
                    raise KeyError(
                        "Section '%s' does not exist"
                        " ('%s')" % (split_name[level], err))
                else:
                    section[split_name[level]] = self._new_section()
                    section = section[split_name[level]]
                    level += 1

        subkey = split_name[level]
        return section, subkey

    def __getitem__(self, key):
        """Get an item
        """
        section, subkey = self.__descend_sections(key)
        # At the last section, get the value
        try:
            value = section[subkey]
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)
        return value

    def __setitem__(self, key, value):
        """Set an item
        """
        if self.base is None:
            raise KeyError("Mapping has not been initialized")
        section, subkey = self.__descend_sections(key, create=True)
        # At the last section, set the value
        try:
            section[subkey] = value
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)

    def __delitem__(self, key):
        """Delete an item
        """
        section, subkey = self.__descend_sections(key)
        # At the last section, set the value
        try:
            del section[subkey]
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)

    def __iter__(self):
        """Need to define __iter__ to make it a MutableMapping
        """
        iterator_list = [(iteritems(self.base or {}), '')]
        while iterator_list:
            iterator, prefix = iterator_list.pop()
            try:
                key, value = next(iterator)
                if len(prefix) > 0:
                    key = prefix + '.' + key
            except StopIteration:
                continue
            iterator_list.append((iterator, prefix))

            if self._is_section(value):
                iterator_list.append((iteritems(value), key))
            else:
                yield key

    def __len__(self):
        """Returns the number of entries in the mapping"""
        return len(list(iter(self)))

    def __repr__(self):
        """Get a represntation of the mapping"""
        return repr(list(iteritems(self)))

    def get(self, key, default=None):
        """Get the key or return the default value if provided
        """
        try:
            return self[key]
        except KeyError:
            if default is not None:
                return default
            else:
                raise

    def get_or_set(self, key, value):
        """Either gets the value associated with key or set it
        This can be useful as an easy way of
        """
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value