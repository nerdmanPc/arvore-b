import os
from typing import Optional, Tuple, Union
from node import Node, Entry
from enum import Enum
from struct import Struct
from queue import Queue
#from main import GRAUMINIMO, FILE_PATH

#nodes = [Node.new_empty()]


class OpStatus(Enum):
    OK = 0
    ERR_KEY_EXISTS = -1
    ERR_OUT_OF_SPACE = -2
    ERR_KEY_NOT_FOUND = -3

# LAYOUT: | N | RAIZ | NO[0] | NO[1] | ... | NO[N-1]
class DataBase:
    header_format = Struct('> L L')  #Header(length: uint32, root: uint32)

    # CERTO
    def __init__(self, file_path: str):
        self._path = file_path
        try:
            with open(file_path, 'xb') as file:
                self._length = 0
                self._root = 0
                file.write(self.header_format.pack(self._length, self._root))
            new_root = self._append_node(Node.new_empty())
            self._set_root(new_root)
        except FileExistsError:
            with open(file_path, "rb") as file:
                header = file.read(self._header_size())
                (length, root) = self.header_format.unpack(header)
                self._length = length
                self._root = root

    # CERTO
    # Inicializa o indice e coloca o ponteiro na raiz
    def __iter__(self):
        self.it_queue = Queue()
        #print('root', self._root)
        self.it_queue.put(self._root)
        return self

    # CERTO
    # Retorna proximo no do percurso em largura e sua posicao original
    def __next__(self) -> Tuple[Node, int]:
        if self.it_queue.empty():
            raise StopIteration
        next_index = self.it_queue.get()
        #print(next_index)
        next_node = self._load_node(next_index)
        for child in next_node.children_ids():
            #print('child', child)
            self.it_queue.put(child)
        return (next_node, next_index)

    def __str__(self):
        result = []
        for i, node in enumerate(self):
            result.append(str(node))
        return '\n'.join(result)

    # CERTO
    @classmethod
    def _header_size(cls) -> int:
        return cls.header_format.size

    def empty(self) -> bool:
        return self._length == 0

    # CERTO
    @classmethod
    def _index_to_ptr(cls, index: int) -> int:
        node_size = Node.size()
        header_size = cls._header_size()
        return header_size + index * node_size

    # CERTO
    def _set_length(self, length: int) -> None:
        with open(self._path, 'r+b') as file:
            file.seek(0, 0)
            self._length = length
            file.write(self.header_format.pack(length, self._root))

    # CERTO
    def _set_root(self, root: int) -> None:
        with open(self._path, 'r+b') as file:
            file.seek(0, 0)
            self._root = root
            file.write(self.header_format.pack(self._length, root))

    # CERTO Retorna no de indice 'index' deserializado
    def _load_node(self, index: int) -> Node:
        if index >= self._length: print(f'INDICE INVALIDO: {index}')
        load_position = self._index_to_ptr(index)
        with open(self._path, 'rb') as file:
            file.seek(load_position, 0)
            data = file.read(Node.size())
            node = Node.from_bytes(data)
            return node

    # CERTO Armazena no 'node' no arquivo, na posicao 'index'
    def _store_node(self, node: Node, index: int) -> None:
        if index > self._length: print(f'INDICE INVALIDO: {index}')
        store_position = self._index_to_ptr(index)
        with open(self._path, 'r+b') as file:
            file.seek(store_position, 0)
            data = node.into_bytes()
            file.write(data)
            
    # CERTO Armazena no 'to_append' no final do arquivo
    # e retorna o novo indice.
    def _append_node(self, to_append: Node) -> int:
        new_index = self._length
        self._store_node(to_append, new_index)
        self._set_length(self._length + 1)
        return new_index

    # CERTO
    # Se nao houver pai, cria nova raiz e insere.
    def _break_node(self, to_break: int, parent_index: Optional[int]) -> None:
        left_node = self._load_node(to_break)
        (entry, new_node) = left_node.split_when_full()
        left, right = to_break, self._append_node(new_node)
        if parent_index is None:
            new_root = Node.new_root(entry, left, right)
            self._set_root(self._append_node(new_root))
        else:
            parent_node = self._load_node(parent_index)
            parent_node.insert_in_parent(entry, right)
            self._store_node(parent_node, parent_index)
        self._store_node(left_node, left)

    # CERTO
    def _break_if_full(self, index: int, parent_index: int) -> bool:
        node_to_break = self._load_node(index)
        if node_to_break.is_full():
            self._break_node(index, parent_index)
            return True
        return False

    # CERTO
    def _internal_search(self, key: int) -> Union[Entry, int]:
        next_index = self._root
        if self._break_if_full(next_index, None):
            return self._internal_search(key)
        search_result = self._load_node(next_index).search_by_key(key)
        while not (search_result is None):
            if isinstance(search_result, int):
                parent_index = next_index
                next_index = search_result
                if self._break_if_full(next_index, parent_index):
                    return self._internal_search(key)
                search_result = self._load_node(next_index).search_by_key(key)
            elif isinstance(search_result, Entry):
                return search_result
        return next_index

    # CERTO
    # Constroi novo registro, tenta inserir na posicao correta
    # e retorna o resultado.
    def add_entry(self, key: int, name: str, age: int) -> OpStatus:
        search_result = self._internal_search(key)
        if isinstance(search_result, Entry):
            return OpStatus.ERR_KEY_EXISTS
        else:
            entry_to_insert = Entry(key, name, age)
            node_to_insert = self._load_node(search_result)
            node_to_insert.insert_in_leaf(entry_to_insert)
            self._store_node(node_to_insert, search_result)
            return OpStatus.OK

    # CERTO
    # Retorna Registro com chave 'key', se estiver na arvore
    def entry_by_key(self, key: int) -> Optional[Entry]:
        search_result = self._internal_search(key)
        if isinstance(search_result, Entry):
            # busca
            return search_result
        else:
            return None

    def _make_node_map(self) -> dict:
        node_map = dict()
        for print_id, (node, addr) in enumerate(self):
            node_map[addr] = print_id + 1
        return node_map

    # TODO: IMPRIME A ARVORE
    def print_tree(self):
        # Deve ser passado pra cada no, como parametro de mapped_str()
        node_map = self._make_node_map()
        for print_id, (node, address) in enumerate(self):
            node_str = node.mapped_str(node_map)
            print(f'no: {print_id + 1}: {node_str}')

    def _print_keys_ordered(self, index: int):
        node = self._load_node(index)
        if node.is_leaf():
            for entry in node:
                print(entry.key())
        else:
            children = node.children_ids()
            for i, entry in enumerate(node):
                self._print_keys_ordered(children[i])
                print(entry.key())
            self._print_keys_ordered(children[-1])

    def print_keys_ordered(self):
        if self.empty():
            print('arvore vazia')
            return
        self._print_keys_ordered(self._root)


    # CERTO
    # IMPRIME A TAXA DE OCUPACAO
    def occupancy(self) -> float:
        _sum, count = 0.0, 0
        for (node, addr) in self:
            _sum += node.occupancy()
            count += 1
        return _sum / count

'''
try:
    os.remove("database.bin")
except:
    pass

database = DataBase("database.bin")

database.add_entry(10, 'joao', 10)
database.add_entry(15, 'maria', 15)
database.add_entry(20, 'pedro', 20)
database.add_entry(30, 'laila', 30)

joao = database.entry_by_key(10)
maria = database.entry_by_key(15)
pedro = database.entry_by_key(20)
laila = database.entry_by_key(30)

print(joao)
print(maria)
print(pedro)
print(laila)

#database.print_tree()
#database.print_keys_ordered()
exit()
'''