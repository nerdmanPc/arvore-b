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

# LAYOUT: | N | RAIZ | NÓ[0] | NÓ[1] | ... | NÓ[N-1]
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
            new_root = self._append_node(Node.new_empty)
            self._set_root(new_root)
        except FileExistsError:
            with open(file_path, "rb") as file:
                header = file.read(self._header_size())
                (length, root) = self.header_format.unpack(header)
                self._length = length
                self._root = root

    # CERTO
    # Inicializa o índice e coloca o ponteiro na raiz
    def __iter__(self):
        self.it_queue = Queue()
        self.it_queue.put(self._root)
        return self

    # CERTO
    # Itera sobre elementos da árvore
    def __next__(self):
        if self.it_queue.empty():
            raise StopIteration
        next = self._load_node(self.it_queue.get())
        for child in next.children_ids():
            self.it_queue.put(child)
        return next

    # TODO: IMPRIMIR A ÁRVORE
    def __str__(self):
        result = []
        for i, node in enumerate(self):
            result.append(str(node))
        return '\n'.join(result)

    # CERTO
    @classmethod
    def _header_size(cls) -> int:
        return cls.header_format.size()

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

    # CERTO Retorna nó de índice 'index' deserializado
    def _load_node(self, index: int) -> Node:
        if index >= self._length: print(f'ÍNDICE INVÁLIDO: {index}')
        load_position = self._index_to_ptr(index)
        with open(self._path, 'rb') as file:
            file.seek(load_position, 0)
            data = file.read(Node.size())
            node = Node.from_bytes(data)
            return node

    # CERTO Armazena nó 'node' no arquivo, na posição 'index'
    def _store_node(self, node: Node, index: int) -> None:
        if index >= self._length: print(f'ÍNDICE INVÁLIDO: {index}')
        store_position = self._index_to_ptr(index)
        with open(self._path, 'rb') as file:
            file.seek(store_position, 0)
            data = node.into_bytes()
            file.write(data)
            
    # CERTO Armazena nó 'to_append' no final do arquivo
    # e retorna o novo índice.
    def _append_node(self, to_append: Node) -> int:
        new_index = self._length
        self._store_node(to_append, new_index)
        self._set_length(self._length + 1)
        return new_index

    # CERTO
    # Se não houver pai, cria nova raiz e insere.
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
    def _break_if_full(self, index: int, parent_index: int) -> None:
        node_to_break = self._load_node(index)
        if node_to_break.is_full():
            self._break_node(index, parent_index)

    # CERTO
    def _internal_search(self, key: int) -> Union[Entry, int]:
        next_index = self._root
        self._break_if_full(next_index, None)
        search_result = self._load_node(next_index).search_by_key(key)
        while not (search_result is None):
            if isinstance(search_result, int):
                parent_index = next_index
                next_index = search_result
                self._break_if_full(next_index, parent_index)
                search_result = self._load_node(next_index).search_by_key(key)
            elif isinstance(search_result, Entry):
                return search_result
        return next_index

    # CERTO
    # Constrói novo registro, tenta inserir na posição correta
    # e retorna o resultado.
    def add_entry(self, key: int, name: str, age: int) -> OpStatus:
        search_result = self._internal_search(key)
        if isinstance(search_result, Entry):
            return OpStatus.ERR_KEY_EXISTS
        else:
            entry_to_insert = Entry(key, name, age)
            node_to_insert = self._load_node(search_result)
            node_to_insert.insert_in_leaf(entry_to_insert)
            self._store_node(node_to_insert)
            return OpStatus.OK

    # CERTO
    # Retorna Registro com chave 'key', se estiver na árvore
    def entry_by_key(self, key: int) -> Optional[Entry]:
        search_result = self._internal_search(key)
        if isinstance(search_result, Entry):
            # busca
            return search_result
        else:
            return None

    # TODO: IMPRIME A ARVORE
    # Os apontadores e chaves devem ser impressos seguindo a estrutura do nó.
    # Cada apontador deve ser impresso da seguinte maneira:
    # a sequência de caracteres ’apontador:’, seguida de um espaço,
    # seguido do número sequencial do nó para o qual o apontador aponta.
    # Se for um nó folha, o valor dos apontadores deve ser null.
    # Cada chave será impressa da seguinte maneira:
    # a sequência de caracteres ’chave:’, seguida de um espaço,
    # seguido do valor da chave. As impressões de apontadores
    # e chaves devem estar separadas por um espaço.
    # Se em um nó estiverem armazenados k registros,
    # apenas as chaves destes registros e os apontares adjacentes a
    # eles devem ser impressos.
    def print_tree(self):
        print('TODO: DataBase.print_tree()')
        print('No: ', no, ': ')
        for child in node:
            print(apontar / chave, ': ', valor)
        print('\n')
        depth += 1
        pass

    # TODO: IMPRIME A ÁRVORE ORDENADA
    def print_keys_ordered(self):
        print('TODO: DataBase.print_keys_ordered()')

    # TODO: IMPRIME A TAXA DE OCUPAÇÃO
    # TA ERRADO
    def print_occupancy(self):
        print('TODO: DataBase.print_occupancy()')
        occupancy = Node.occupancy()
