import logging
import logging
import hashlib
import numpy as np
import networkx as nx
from collections import namedtuple

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
        self.next = None
        

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        entry = ListEntry(key, value)        
        entry.next = self.head
        
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
            self.tail.next = None
        return dropped
            
    def move_up(self, entry):
        prev = entry.prev
        next = entry.next

        if prev is not None:
            prev.next = next
        if next is not None:
            next.prev = prev

        if entry is self.head:
            self.head = next
        if entry is self.tail:
            self.tail = prev
            
        new_entry = self.push(entry.key, entry.value)
        return new_entry
        
            
class LightweightCache:
    """ Uses LRU for pruning """
    
    def __init__(self, max_size=None):
        self._map = {}
        self._list = DoublyLinkedList()
        self._max_size = max_size

    def put(self, layer_id, value, id_to_properties, edges_by_id):
        key = self._compute_hash(layer_id, id_to_properties, edges_by_id)
        self._insert_and_purge(key, value)

    def get(self, layer_id, id_to_properties, edges_by_id):
        key = self._compute_hash(layer_id, id_to_properties, edges_by_id)

        if key is not None and key in self._map:
            entry = self._map[key]
            value = entry.value

            new_entry = self._list.move_up(entry)
            self._map[key] = new_entry
            return value
        else:
            return None
        
    def _compute_hash(self, layer_id, id_to_properties, edges_by_id):
        graph = nx.DiGraph()
        graph.add_edges_from(edges_by_id)
        graph.add_node(layer_id)

        ancestor_ids = nx.ancestors(graph, layer_id)
        full_properties = id_to_properties[layer_id]

        if full_properties is None:
            return None            
        
        for ancestor_id in sorted(ancestor_ids):
            properties = id_to_properties[ancestor_id]            
            if properties is None:
                return None            
            
            full_properties += properties

        encoded = full_properties.encode('utf-8')
        md5 = hashlib.md5(encoded).hexdigest()
        return md5
        
    def _insert_and_purge(self, key, value):
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

        #print_order(self._list, self._map)                                

    @property
    def size(self):
        return len(self._map)


if __name__ == "__main__":
    cache = LightweightCache()


