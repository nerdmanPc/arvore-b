from struct import Struct
from typing import Optional, Tuple, Union
from enum import Enum

from old import Entry

class Entry:
    format = Struct('> L 20s B')

    def __init__(self, key:int, name:str, age:int) -> None:
        self.key = key
        self.name = name
        self.age = age

    @classmethod
    def size(cls) -> int:
        return cls.format.size

    def is_key(self, key: int) -> bool:
        return self.key == key

    @classmethod 
    def from_bytes(cls, data: bytes): #-> Entry
        (key, name, age) = cls.format.unpack(data)
        name = str(name, 'utf-8')
        return Entry(key, name, age)

    def into_bytes(self) -> bytes:
        return self.format.pack(self.key, bytes(self.name, 'utf-8'), self.age)

class Node:
    header_format = Struct('> ? I') #bool, uint32
    child_ptr_format = Struct('> I')
    entry_format = Entry.format
    @classmethod
    def from_bytes(cls, data: bytes): #-> Node:
        pass
    def into_bytes(self) -> bytes:
        pass
    def insert_entry(self, entry: Entry) -> None:
        pass
    def break_node(self): #-> Tuple[Node, Entry, Node]:
        pass
    def full(self) -> bool:
        pass
    #Retorna Entry se a chave está no nó, int se está num nó filho e None se chave não está no nó e este é folha. Busca apenas dentor do próprio nó.
    def search_by_key(key: int) -> Optional[Union[Entry, int]]: 
        pass
    def __str__(self): 
        pass
    def entry_by_index(index: int) -> Optional[Entry]: #PRIVADO
        pass
    def child_by_index(index: int) -> Optional[int]: #PRIVADO
        pass