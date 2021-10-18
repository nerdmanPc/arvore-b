import os
from struct import Struct
from typing import Optional, Tuple
from enum import Enum
from node import Node
from data_base import DataBase, OpStatus
import sys

FILE_PATH = "tree.bin"
#GRAUMINIMO = 2 #Dá problema de import circular. Movido para 'node.py'

#class OpStatus(Enum):
#	OK = 0
#	ERR_KEY_EXISTS = -1
#	ERR_KEY_NOT_FOUND = -2

def insert_entry(key:int, name:str, age:int):
	data_base = DataBase(FILE_PATH)
	insert_result = data_base.add_entry(key, name, age)
	#print(insert_result)
	if insert_result == OpStatus.OK:
		print('insercao com sucesso: {}'.format(key))
	elif insert_result == OpStatus.ERR_KEY_EXISTS:
		print('chave ja existente: {}'.format(key))
	else:
		print('DEBUG: erro logico na insercao da chave {}'.format(key))

def query_entry(key:int):
	data_base = DataBase(FILE_PATH)
	_entry = data_base.entry_by_key(key)
	if _entry is not None:
		print(_entry)
	else:
		print('chave nao encontrada: {}'.format(key))

def print_tree():
	data_base = DataBase(FILE_PATH)
	data_base.print_tree()

def print_sequence():
	data_base = DataBase(FILE_PATH)
	data_base.print_keys_ordered()

def print_occupancy():
	data_base = DataBase(FILE_PATH)
	if data_base.empty():
		print('árvore vazia')
		return
	occupancy = data_base.occupancy()
	print('{:.1f}'.format(occupancy))

def exit_shell():
	sys.exit()

os.remove(FILE_PATH)

#Loop principal que processa os comandos.
entry = input()
while entry != 'e':
    if(entry == 'i'):
        num_reg = input()
        name_reg = input()
        age_reg = input()
        insert_entry(int(num_reg), name_reg, int(age_reg))
    elif(entry == 'c'):
        num_reg = input()
        query_entry(int(num_reg))
    elif(entry == 'p'):
        print_tree()
    elif(entry == 'o'):
        print_sequence()
    elif(entry == 't'):
        print_occupancy()
    entry = input()
exit_shell()
#Fim do loop principal.