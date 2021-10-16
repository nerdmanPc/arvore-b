from typing_extensions import ParamSpecArgs
from node import *
from main import GRAUMINIMO, FILE_PATH

class DataBase:
	header_format = Struct('>L')

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
	
	#Inicializa o índice e coloca o ponteiro na raiz
	def __iter__(self):
		self.it_index = -1
		self.it_file = open(self.path, 'rb')
		self.it_file.seek(self.header_size(), 0)
		return self

	#Itera sobre elementos da árvore
	def __next__(self):
		self.it_index += 1
		if self.it_index >= self.length:
			self.it_file.close()
			raise StopIteration
		data = self.it_file.read(Entry.size())
		entry = Entry.from_bytes(data)
		return entry
	
	#IMPRIMIR A ÁRVORE
	def __str__(self):
		result = []
		for entry in self:
			result.append( str(entry) )
		return '\n'.join(result)

	@classmethod
	def header_size(cls) -> int:
		return cls.header_format.size

	@classmethod
	def index_to_ptr(cls, index:int) -> int:
		entry_size = Entry.size()
		header_size = cls.header_size()
		return header_size + index * entry_size

	def set_length(self, length:int) -> None:
		with open(self.path, 'r+b') as file:
			file.seek(0, 0)
			file.write(self.header_format.pack(length))
			self.length = length

	def entry_by_index(self, index:int) -> Entry:
		if index >= self.length: print(f'ÍNDICE INVÁLIDO: {index}')
		with open(self.path, 'rb') as file:
			file.seek(self.header_size() + index * Entry.size(), 0)
			data = file.read(Entry.size())
			entry = Entry.from_bytes(data)
			return entry

	#PERCORRER A ARVORE PRA ACHAR O NÓ DO REGISTRO
	def add_entry(self, key:int, name:str, age:int) -> OpStatus:
		with open(self.path, 'r+b') as file:
			free_pointer = self.index_to_ptr(self.length)
			file.seek(free_pointer)
			entry_bytes = Entry(key, name, age).into_bytes()
			file.write(Node.insert_in_leaf(entry_bytes))
		return OpStatus.OK

	#ACHA O REGISTRO DA CHAVE QUE PASSAR
	def search_by_key(self, key:int) -> Optional[Entry]:
		(entry, key, aux) = Node.search_by_key(key)
		if key is not None:
			#busca
			return
		else:
			return

	# IMPRIME A ARVORE
	# Os apontadores e chaves devem ser impressos seguindo a estrutura do nó. Cada apontador deve ser impresso da seguinte maneira: a sequência de caracteres ’apontador:’, seguida de um espaço, seguido do número sequencial do nó para o qual o apontador aponta. Se for um nó folha, o valor dos apontadores deve ser null. Cada chave será impressa da seguinte maneira: a sequência de caracteres ’chave:’, seguida de um espaço, seguido do valor da chave. As impressões de apontadores e chaves devem estar separadas por um espaço. Se em um nó estiverem armazenados k registros, apenas as chaves destes registros e os apontares adjacentes a eles devem ser impressos.
	def print_tree(self, node:int, depth:int):
		depth = 0
		print('No: ', no, ': ')
		for child in node:
			print(apontar/chave, ': ', valor)
		print('\n')
		depth += 1
		pass

	#IMPRIME A ÁRVORE ORDENADA
	def print_keys_ordered(self):
		pass
	
	#IMPRIME A TAXA DE OCUPAÇÃO
	def print_occupancy(self):
		pass
