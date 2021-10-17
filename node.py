from struct import Struct
from typing import Optional, Tuple, Union, List
from enum import Enum
from math import floor
#from main import GRAUMINIMO

GRAUMINIMO = 2

class Entry:
    format = Struct('> L 20s B')

    def __init__(self, key:int, name:str, age:int) -> None:
        self._key = key
        self._name = name
        self._age = age

    @classmethod
    def size(cls) -> int:
        return cls.format.size

    def key(self) -> int:
        return self._key

    def is_key(self, key: int) -> bool:
        return self._key == key

    def key_greater_than(self, key: int) -> bool:
        return self._key > key

    def __str__(self):
        return '{} {} {}'.format(self._key, self._name, self._age)

    @classmethod 
    def from_bytes(cls, data: bytes): #-> Entry
        (key, name, age) = cls.format.unpack(data)
        name = str(name, 'utf-8')
        return Entry(key, name, age)

    def into_bytes(self) -> bytes:
        return self.format.pack(self._key, bytes(self._name, 'utf-8'), self._age)

class Node:

    max_degree = 2*GRAUMINIMO
    header_format = Struct('> ? I') #is_leaf: bool, entry_count: uint32
    child_id_format = Struct('> I')
    entry_format = Entry.format
    header_size = header_format.size
    child_id_size = child_id_format.size
    entry_size = entry_format.size

    def __init__(self, is_leaf: bool, entries: List[Entry], children_ids: List[int]) -> None:
        self._is_leaf = is_leaf
        self._entries = entries
        self._children_ids = children_ids

    @classmethod
    def new_empty(cls):
        return cls(True, [], [])

    @classmethod
    def new_root(cls, entry: Entry, left, right):
        return cls(False, [entry], [left, right])

    # Deve ser chamada logo após 'insert_in_parent()', 
    # no nó retornado por esta. 
    # sendo 'key' a chave recém inserida. Retorna o novo nó.
    #def split_by_key(self, key: int): #-> Node 
    #    split_index = self._index_to_split(key)
    #    right_entries = self._entries[split_index:]
    #    right_children = self._children_ids[split_index:]
    #    self._entries = self._entries[:split_index]
    #    self._children_ids = self._children_ids[:split_index+1]
    #    return Node(self._is_leaf, right_entries, right_children)

    @classmethod
    def from_bytes(cls, data: bytes): #-> Node:

        (is_leaf, entry_count) = cls.header_format.unpack(data[:cls.header_size])
        entries = []
        for index in range(entry_count):
            ptr = cls._entry_offset(index)
            entry_data = data[ ptr : ptr + cls.entry_size ]
            entry = Entry.from_bytes(entry_data)
            entries.append(entry)

        if is_leaf:
            return Node(is_leaf, entries, [])

        children = []
        for index in range(entry_count + 1):
            ptr = cls._child_offset(index)
            child_data = data[ ptr : ptr + cls.child_id_size ]
            child = cls.child_id_format.unpack(child_data)
            children.append(child)

        return Node(is_leaf, entries, children)

    def into_bytes(self) -> bytes:
        data = bytearray(self.size())
        data[:self.header_size] = self.header_format.pack(self._is_leaf, len(self._entries))

        for index, entry in enumerate(self._entries):
            ptr = self._entry_offset(index)
            entry_data = entry.into_bytes()
            data[ ptr : ptr + self.entry_size ] = entry_data

        if self._is_leaf:
            return bytes(data)

        for index, child in enumerate(self._children_ids):
            ptr = self._child_offset(index)
            child_data = self.child_id_format.pack(child)
            data[ ptr : ptr + self.child_id_size ] = child_data
        return bytes(data)

    # Deve ser chamada ao visitar o nó e ele estar cheio.
    # Retorna a tupla (chave_removida, novo_no)
    def split_when_full(self): #-> Tuple[Entry, Node]:
        split_index = floor((len(self._entries) + 1) / 2)
        right_entries = self._entries[split_index:]
        right_children = self._children_ids[split_index:]
        # Os ponteiros à esquerda e direita de 'middle_entry' podem ser obtidos por quem chama
        middle_entry = self._entries[split_index-1]

        self._entries = self._entries[:split_index-1]
        self._children_ids = self._children_ids[:split_index]
        new_node = Node(self._is_leaf, right_entries, right_children)
        return (middle_entry, new_node)
    
    #Insere registro 'to_insert', aloca espaço para o novo ID de filho 
    # e retorna o ID do filho passado por parâmetro. Chamada após a quebra de um nó filho. 
    #  |Registro|Ponteiro|Registro| -> |Registro|Ponteiro|NovoRegistro|NovoPonteiro|Registro|
    #  |index-1 |     index       | -> |index-1 |        index        |      index+1        |
    def insert_in_parent(self, to_insert: Entry, right_child: int) -> bool: 
        if self._is_leaf or self.is_full():
            return False
        for index, current in enumerate(self._entries):
            if current.key_greater_than(to_insert.key()):
                self._entries.insert(index, to_insert) # insere 'to_insert' antes de 'current'
                self._children_ids.insert(index + 1, right_child) 
                return True
        self._entries.append(to_insert)  
        self._children_ids.append(right_child) 
        return True 
    
    #Insere registr 'to_insert' e retorna se houve sucesso
    def insert_in_leaf(self, to_insert: Entry) -> bool:
        if (not self._is_leaf) or self.is_full():
            return False
        for index, current in enumerate(self._entries):
            if current.key_greater_than(to_insert.key()):
                self._entries.insert(index, to_insert) #insere 'to_insert' antes de 'current'
                return True
        self._entries.append(to_insert) # Se nenhum registro tem a chave maior, insere no final
        return True

    # Insere 'child_id' no lugar do primeiro ponteiro inválida (-1).
    # Deve ser chamada depois de insert_in_parent() com o ID  do novo nó.
    #def insert_child(self, child_id: int) -> None:
    #    for child in self._children_ids:
    #        if child == -1:
    #            child = child_id
    #            return
    #    print(f'Fail to insert child ({child_id})')
            
    # Retorna Entry se a chave está no nó, int se está num nó filho e None se
    # chave não está no nó e este nó é folha. Busca apenas dentro do próprio nó.
    # int é o ID do filho onde a chave deve estar (subarvore)
    def search_by_key(self, key: int) -> Union[Entry, int, None]: 
        #print('TODO: Node.search_by_key()')
        #print(f'key = {key} self._is_leaf = {self._is_leaf}')
        for i, entry in enumerate(self._entries):     # Itera sobre os valores de entradas
            if entry.key() == key:  # 'key' está na posição atual
                return entry
            elif entry.key() > key and not self._is_leaf:   # 'key' está no nó à esquerde
                return self._children_ids[i]
        if not self._is_leaf: # 'key' está no último filho à direita
            return self._children_ids[len(self._entries)]
        else:                 # 'key'não está nesta subárvore
            return None


    def is_full(self) -> bool:
        return len(self._entries) >= self.max_degree-1

    def is_leaf(self) -> bool:
        return self._is_leaf
        
    @classmethod
    def size(cls) -> int:
        return cls.header_size + \
            cls.child_id_size * cls.max_degree + \
            cls.entry_size * (cls.max_degree - 1)

    def occupancy(self) -> float:
        return len(self._entries) / (self.max_degree-1)

    # Retorna ínice do primeiro registro com chave maior que 'key'
    def _index_to_split(self, key: int) -> int:
        for i, entry in enumerate(entries):
            if entry.key() > key:
                return i
        return len(entries)

    @classmethod
    def _entry_offset(cls, index: int) -> Optional[Entry]: #PRIVADO
        start = cls.header_size + cls.child_id_size #Pula o cabeçalho e o primeiro filho
        step = cls.entry_size + cls.child_id_size #Avança para o próximo registro pulando o filho entre eles
        return start + index*step

    @classmethod
    def _child_offset(cls, index: int) -> Optional[int]: #PRIVADO
        start = cls.header_size #Pula o cabeçalho
        step = cls.child_id_size + cls.entry_size #Avança para o próximo filho pulando o registro entre eles
        return start + step * index 

    def __iter__(self):
        return iter(self._entries)

    #def __str__(self) -> str:      #VERDADEIRA
    #    items_str = []
    #    for index, entry in enumerate(self._entries):
    #        if index < len(self._children_ids):
    #            child = self._children_ids[index] 
    #            items_str.append(str(child))
    #        items_str.append(str(entry))
    #    if not self._is_leaf:
    #        child = self._children_ids[-1] 
    #        items_str.append(str(child))
    #    return ' | '.join(items_str)

    def __str__(self) -> str:     # TESTE
        items_str = []
        for index, entry in enumerate(self._entries):
            if index < len(self._children_ids):
                child = self._children_ids[index] 
                items_str.append('c'+str(child))
            items_str.append('k'+str(entry.key()))
        if not self._is_leaf:
            child = self._children_ids[-1] 
            items_str.append('c'+str(child))
        return '[ ' + ' | '.join(items_str) + ' ]'

#TESTE

entries = [
    Entry(1, 'Aunt May', 5),
    Entry(6, 'Rainha Elizabeth', 255),
    Entry(3, 'Keanu Reeves', 196),
    Entry(4, 'Pedro Costa', 25),
    Entry(2, 'Abraham Weintraub', 12),
    Entry(0, 'Roberto Carlos', 128), 
    Entry(5, 'Kid Bengala', 64), #
    Entry(10, 'Ben 10', 12),
    Entry(666, 'Satanás Azelelé', 222)
]

nodes = [Node.new_empty()]
root = 0

def append_node(node: Node) -> int:
    global root, nodes
    new_index = len(nodes)
    nodes.append(node)
    return new_index 

def print_nodes():
    global root, nodes
    print(f'Root: {root}')
    for i, node in enumerate(nodes): 
        print(f'Node[{i}]: {node}')

def search_node(key: int) -> Union[Node, Entry]:
    global root, nodes
    next_index = root
    search_result = nodes[next_index].search_by_key(key)
    while not(search_result is None):
        if isinstance(search_result, int):
            next_index = search_result
            search_result = nodes[next_index].search_by_key(key)
        elif isinstance(search_result, Entry):
            return search_result
    return next_index

def break_node(to_break: int, parent: Optional[int]):
    global root, nodes
    (entry, new_node) = nodes[to_break].split_when_full()
    left, right = to_break, append_node(new_node)
    if parent is None: 
        new_root = Node.new_root(entry, left, right)
        root = append_node(new_root)
    else:
        nodes[parent].insert_in_parent(entry, right)

nodes[root].insert_in_leaf(entries[0])
nodes[root].insert_in_leaf(entries[1])
nodes[root].insert_in_leaf(entries[2])
print_nodes()

#(entry, new_node) = nodes[root].split_when_full()
#new_index = append_node(new_node)
#new_root = Node.new_root(entry, root, new_index)
#root = append_node(new_root)
break_node(0, None)
print_nodes()

index_to_insert = search_node(entries[3].key()) # Resultado da busca da chave 4
nodes[index_to_insert].insert_in_leaf(entries[3])
print_nodes()

index_to_insert = search_node(entries[4].key()) # Resultado da busca da chave 2
nodes[index_to_insert].insert_in_leaf(entries[4])
print_nodes()

index_to_insert = search_node(entries[5].key()) # Resultado da busca da chave 0
nodes[index_to_insert].insert_in_leaf(entries[5])
print_nodes()

index_to_insert = search_node(entries[6].key()) # Resultado da busca da chave 5
nodes[index_to_insert].insert_in_leaf(entries[6])
print_nodes()

#index_to_break = 1 
#(entry, new_node) = nodes[index_to_break].split_when_full()
#new_index = append_node(new_node)
#nodes[root].insert_in_parent(entry, new_index)
break_node(1, 2)
print_nodes()

index_to_insert = search_node(entries[7].key())# Resultado da busca da chave 10
nodes[index_to_insert].insert_in_leaf(entries[7])
print_nodes()

exit()
