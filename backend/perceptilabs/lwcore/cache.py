import logging

from perceptilabs.caching.base import BaseCache
from perceptilabs.logconf import APPLICATION_LOGGER


#def print_order(l, d):
#    print('-- print order --')
#    head = l.head.value if l.head else '<none>'
#    tail = l.tail.value if l.tail else '<none>'    
#    print(f'head: {head}, tail: {tail}') 
#    for e in d.values():
#        prev = e.prev.value if e.prev else '<none>'
#        next = e.next.value if e.next else '<none>'        
#        print(f'value: {e.value}, prev: {prev}, next: {next}')
#    print('-- -- --')



logger = logging.getLogger(APPLICATION_LOGGER)


class ListEntry:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next_ = None
        

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        entry = ListEntry(key, value)        
        entry.next_ = self.head
        
        if self.head is not None:
            self.head.prev = entry
        if self.tail is None:
            self.tail = entry
            
        self.head = entry        
        return entry
        
    def drop_tail(self):
        dropped = self.tail
        if self.tail.prev is not None:
            self.tail = dropped.prev
            self.tail.next_ = None
        return dropped
            
    def move_up(self, entry):
        prev = entry.prev
        next_ = entry.next_

        if prev is not None:
            prev.next_ = next_
        if next_ is not None:
            next_.prev = prev

        if entry is self.head:
            self.head = next_
        if entry is self.tail:
            self.tail = prev
            
        new_entry = self.push(entry.key, entry.value)
        return new_entry
        
            
class LightweightCache(BaseCache):
    """ Uses LRU for pruning """
    
    def __init__(self, max_size=None):
        self._map = {}
        self._list = DoublyLinkedList()
        self._max_size = max_size

    def put(self, key, value):
        """ Inserts a key/value pair into the cache

        Args:
            key: a unique key. Typically the hash of a layer spec and its dependencies.
            value: the value associated with the key.
        """
        self._insert_and_maybe_purge(key, value)

    def get(self, key):
        """ Tries to retrieve the value of key from the cache

        Args:
            key: a unique key. Typically the hash of a layer spec and its dependencies.

        Returns:
            A value if key is present. Otherwise, returns None
        """
        if key is not None and key in self._map:
            entry = self._map[key]
            value = entry.value

            new_entry = self._list.move_up(entry)
            self._map[key] = new_entry
            return value
        else:
            return None

    def __contains__(self, key):
        return key is not None and key in self._map
        
    def _insert_and_maybe_purge(self, key, value):
        if key in self._map:
            entry = self._map[key]
            new_entry = self._list.move_up(entry)
            self._map[key] = new_entry            
        else:
            entry = self._list.push(key, value)
            self._map[key] = entry
            
        if self._max_size is not None and len(self._map) > self._max_size:
            dropped = self._list.drop_tail()
            if dropped is not None:
                del self._map[dropped.key]

    @property
    def size(self):
        return len(self)

    def __len__(self):
        return len(self._map)


