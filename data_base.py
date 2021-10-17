from typing import Optional, Tuple, Union
from node import Node, Entry
from enum import Enum
from struct import Struct
#from main import GRAUMINIMO, FILE_PATH

nodes = [Node.new_empty()]

class OpStatus(Enum):
    OK = 0
    ERR_KEY_EXISTS = -1
    ERR_OUT_OF_SPACE = -2
    ERR_KEY_NOT_FOUND = -3

# LAYOUT: | N | RAIZ | NÓ[0] | NÓ[1] | ... | NÓ[N-1]
class DataBase:
    header_format = Struct('> L l')  #Header(length: uint32, root: int32)

    # CERTO
    def __init__(self, file_path: str):
        self._path = file_path
        try:
            with open(file_path, 'xb') as file:
                self._length = 0
                self._root = -1
                file.write(self.header_format.pack(self._length, self._root))
        except FileExistsError:
            with open(file_path, "rb") as file:
                header = file.read(self._header_size())
                (length, root) = self.header_format.unpack(header)
                self._length = length
                self._root = root

    # TODO: Inicializa o índice e coloca o ponteiro na raiz
    def __iter__(self):
        print('TODO: DataBase.__iter__()')
        self.it_index = -1
        self.it_file = open(self._path, 'rb')
        self.it_file.seek(self._header_size(), 0)
        return self

    # TODO: Itera sobre elementos da árvore
    def __next__(self):
        print('TODO: DataBase.__next__()')
        self.it_index += 1
        if self.it_index >= self._length:
            self.it_file.close()
            raise StopIteration
        data = self.it_file.read(Entry.size())
        entry = Entry.from_bytes(data)
        return entry

    # TODO: IMPRIMIR A ÁRVORE
    def __str__(self):
        print('TODO: DataBase.__str__()')
        result = []
        for entry in self:
            result.append(str(entry))
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

    # TODO: Quebra nó 'to_break' e insere o registro do meio em 'parent.
    # Se não houver pai, cria nova raiz e insere.
    def _break_node(self, to_break: int, parent: Optional[int]) -> None:
        print('TODO: DataBase.break_node()')

    # TODO: Retorna registro de chave 'key' ou índice do nó onde deve ser inserido
    def _internal_search(self, key: int) -> Union[Entry, int]:
        print('TODO: DataBase.internal_search()')

    # TODO; Constrói novo registro, tenta inserir na posição correta 
    # e retorna o resultado.
    def add_entry(self, key: int, name: str, age: int) -> OpStatus:
        print('TODO: DataBase.add_entry()')
        with open(self._path, 'r+b') as file:
            free_pointer = self._index_to_ptr(self._length)
            file.seek(free_pointer)
            entry_bytes = Entry(key, name, age).into_bytes()
            file.write(Node.insert_in_leaf(entry_bytes))
        return OpStatus.OK

    # TODO: Retorna Registro com chave 'key', se estiver na árvore
    def entry_by_key(self, key: int) -> Optional[Entry]:
        print('TODO: DataBase.search_by_key()')
        (entry, key, aux) = Node.search_by_key(key)
        if key is not None:
            # busca
            return
        else:
            return

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
    def print_tree(self, node: int, depth: int):
        print('TODO: DataBase.print_tree()')
        depth = 0
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
    # Conferir se ta certo
    def print_occupancy(self):
        print('TODO: DataBase.print_occupancy()')
        occupancy = Node.occupancy()
        if occupancy > 0:
            print("{:.1f}".format(occupancy))
