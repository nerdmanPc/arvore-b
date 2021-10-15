from struct import Struct
from typing import Optional, Tuple, Union, List
from enum import Enum
from main import FILE_PATH
from main import GRAUMINIMO

import os

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

    max_degree = 2*GRAUMINIMO
    header_format = Struct('> ? I') #is_leaf: bool, entry_count: uint32
    child_id_format = Struct('> I')
    entry_format = Entry.format
    header_size = header_format.size
    child_id_size = child_id_format.size
    entry_size = entry_format.size

    def __init__(self, is_leaf: bool, entries: List[Entry], children_ids: List[int]) -> None:
        self.is_leaf = is_leaf
        self.entries = entries
        self.children_ids = children_ids

    @classmethod
    def new_empty(cls):
        return cls(True, [], [])

    def split_by_key(self, key: int): #-> Node 
        print('TODO: Node.slpit_by_key()')

    def split_when_full(self): #-> Tuple[Entry, Node]:
        print('TODO: node.split_when_full')
    
    @classmethod
    def from_bytes(cls, data: bytes): #-> Node:
        (is_leaf, entry_count) = cls.header_format.unpack(data[:cls.header_size])

        entries = []
        for index in range(entry_count):
            ptr = cls.entry_offset(index)
            entry_data = data[ ptr : ptr + cls.entry_size ]
            entry = Entry.from_bytes(entry_data)
            entries.append(entry)

        if is_leaf:
            return Node(is_leaf, entries, [])

        children = []
        for index in range(entry_count + 1):
            ptr = cls.child_offset(index)
            child_data = data[ ptr : ptr + cls.child_id_size ]
            child = cls.child_id_format.unpack(child_data)
            children.append(child)

        return Node(is_leaf, entries, children)

    def into_bytes(self) -> bytes:
        data = bytearray(self.size())
        data[:self.header_size] = self.header_format.pack(self.is_leaf, len(self.entries))

        for index, entry in enumerate(self.entries):
            ptr = self.entry_offset(index)
            entry_data = entry.into_bytes()
            data[ ptr : ptr + self.entry_size ] = entry_data

        if self.is_leaf:
            return bytes(data)

        for index, child in enumerate(self.children_ids):
            ptr = self.child_offset(index)
            child_data = self.child_id_format.pack(child)
            data[ ptr : ptr + self.child_id_size ] = child_data

        return bytes(data)

    #Insere registro 'to_insert', aloca espaço para um novo ID de filho e retorna o ID do filho a ser dividido 
    def insert_entry(self, to_insert: Entry) -> Optional[int]: # Registro|Ponteiro|Registro -> Registro|Ponteiro|NovoRegistro|NovoPonteiro|Registro
        #                                                       index=j-1| index=j            index=i-1|        index=i      |     index=i+1
        child_to_split = None
        if self.is_full():
            return child_to_split
        for index, current in enumerate(self.entries):
            if current.key_greater_than(to_insert.key()):
                self.entries.insert(index, to_insert) #insere 'to_insert' antes de 'current'
                child_to_split = 
                break
        
        return child_to_split

    def is_full(self) -> bool:
        return len(self.entries) >= self.max_degree-1
        
    @classmethod
    def size(cls) -> int:
        return cls.header_size + \
            cls.child_id_size * cls.max_degree + \
            cls.entry_size * (cls.max_degree - 1)
    #Retorna Entry se a chave está no nó, int se está num nó filho e None se 
    # chave não está no nó e este é folha. Busca apenas dentor do próprio nó.
    def search_by_key(key: int) -> Optional[Union[Entry, int]]: 
        print('TODO: Node.search_by_key()')

    @classmethod
    def entry_offset(cls, index: int) -> Optional[Entry]: #PRIVADO
        start = cls.header_size + cls.child_id_size #Pula o cabeçalho e o primeiro filho
        step = cls.entry_size + cls.child_id_size #Avança para o próximo registro pulando o filho entre eles
        return start + index*step

    @classmethod
    def child_offset(cls, index: int) -> Optional[int]: #PRIVADO
        start = cls.header_size #Pula o cabeçalho
        step = cls.child_id_size + cls.entry_size #Avança para o próximo filho pulando o registro entre eles
        return start + step * index 

    def __str__(self) -> str: 
        return 'TODO: Node.__str__()'

file_path = 'teste.bin'
node = None
try:
    with open(file_path, 'xb') as file:
        node = Node.new_empty()
        print(f'Empty node: [{node.into_bytes()}]')
        file.write(node.into_bytes())
except FileExistsError:
    with open(file_path, "rb") as file:
        node_data = file.read(Node.size())
        node = Node.from_bytes(node_data)

entry_a = Entry(0, 'Roberto Carlos', 255)
entry_b = Entry(1, 'Aunt May', 5)
entry_c = Entry(2, 'Abraham Weintraub', 12)

print(node)
node.insert_entry(entry_a)
print(node)
node.insert_entry(entry_b)
print(node)
node.insert_entry(entry_c)
print(node)
