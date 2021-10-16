from typing_extensions import ParamSpecArgs
from node import *
from main import GRAUMINIMO, FILE_PATH

class OpStatus(Enum): 
	OK = 0 
	ERR_KEY_EXISTS = -1
	ERR_OUT_OF_SPACE = -2
	ERR_KEY_NOT_FOUND = -3

#LAYOUT: | N | NO[0] | NÓ[1] | ... | NÓ[N-1]                   
class DataBase:
	header_format = Struct('>L')

	# CERTO
	def __init__(self, file_path:str):
		self.path = file_path
		try:
			with open(file_path, 'xb') as file:
				self.length = 0
				file.write( self.header_format.pack(self.length) )
				#empty_entry = Entry.from_status(EntryStatus.EMPTY).into_bytes()
				#file.write(empty_entry * self.length)
		except FileExistsError:
			with open(file_path, "rb") as file:
				header = file.read(self.header_size())
				_tuple = self.header_format.unpack(header)
				self.length = _tuple[0]
	
	# TODO: Inicializa o índice e coloca o ponteiro na raiz
	def __iter__(self):
		print('TODO: DataBase.__iter__()')
		self.it_index = -1
		self.it_file = open(self.path, 'rb')
		self.it_file.seek(self.header_size(), 0)
		return self

	# TODO: Itera sobre elementos da árvore
	def __next__(self):
		print('TODO: DataBase.__next__()')
		self.it_index += 1
		if self.it_index >= self.length:
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
			result.append( str(entry) )
		return '\n'.join(result)

	# CERTO
	@classmethod
	def header_size(cls) -> int:
		return cls.header_format.size

	# CERTO - Note que antes, retornava um ponteiro pra registro, agora retorna um ponteiro pra nó
	@classmethod
	def index_to_ptr(cls, index:int) -> int:
		node_size = Node.size()
		header_size = cls.header_size()
		return header_size + index * node_size

	# CERTO
	def set_length(self, length:int) -> None:
		with open(self.path, 'r+b') as file:
			file.seek(0, 0)
			self.length = length
			file.write(self.header_format.pack(length))

	# TODO: Assim como outras funções, esta tem que mudar a semântica 
	# para oprerar sobre NÓS em vez de REGISTROS
	def node_by_index(self, index:int) -> Entry:
		print('TODO: DataBase.node_by_index()')
		if index >= self.length: print(f'ÍNDICE INVÁLIDO: {index}')
		with open(self.path, 'rb') as file:
			file.seek(self.header_size() + index * Entry.size(), 0)
			data = file.read(Entry.size())
			entry = Entry.from_bytes(data)
			return entry

	# TODO; PERCORRER A ARVORE PRA ACHAR O NÓ DO REGISTRO
	def add_entry(self, key:int, name:str, age:int) -> OpStatus:
		print('TODO: DataBase.add_entry()')
		with open(self.path, 'r+b') as file:
			free_pointer = self.index_to_ptr(self.length)
			file.seek(free_pointer)
			entry_bytes = Entry(key, name, age).into_bytes()
			file.write(Node.insert_in_leaf(entry_bytes))
		return OpStatus.OK

	# TODO: ACHA O REGISTRO DA CHAVE QUE PASSAR
	def search_by_key(self, key:int) -> Optional[Entry]:
		print('TODO: DataBase.search_by_key()')
		(entry, key, aux) = Node.search_by_key(key)
		if key is not None:
			#busca
			return
		else:
			return

	# TODO: IMPRIME A ARVORE
	# Os apontadores e chaves devem ser impressos seguindo a estrutura do nó. Cada apontador deve ser impresso da seguinte maneira: a sequência de caracteres ’apontador:’, seguida de um espaço, seguido do número sequencial do nó para o qual o apontador aponta. Se for um nó folha, o valor dos apontadores deve ser null. Cada chave será impressa da seguinte maneira: a sequência de caracteres ’chave:’, seguida de um espaço, seguido do valor da chave. As impressões de apontadores e chaves devem estar separadas por um espaço. Se em um nó estiverem armazenados k registros, apenas as chaves destes registros e os apontares adjacentes a eles devem ser impressos.
	def print_tree(self, node:int, depth:int):
		print('TODO: DataBase.print_tree()')
		depth = 0
		print('No: ', no, ': ')
		for child in node:
			print(apontar/chave, ': ', valor)
		print('\n')
		depth += 1
		pass

	# TODO: IMPRIME A ÁRVORE ORDENADA
	def print_keys_ordered(self):
		print('TODO: DataBase.print_keys_ordered()')
	
	# TODO: IMPRIME A TAXA DE OCUPAÇÃO
	def print_occupancy(self):
		print('TODO: DataBase.print_occupancy()')
