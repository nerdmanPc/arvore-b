from struct import Struct
from typing import Optional, Tuple
from enum import Enum
from node import Node
from data_base import DataBase
import sys

FILE_PATH = "tree.bin"
#GRAUMINIMO = 2 #Dá problema de import circular. Movido para 'node.py'

class OpStatus(Enum): 
	OK = 0 
	ERR_KEY_EXISTS = -1
	ERR_KEY_NOT_FOUND = -2

def insert_entry(key:int, name:str, age:int):
	data_base = DataBase(FILE_PATH)
	insert_result = data_base.add_entry(key, name, age)
	if insert_result == OpStatus.OK:
		print('insercao com sucesso: {}'.format(key))
	elif insert_result == OpStatus.ERR_KEY_EXISTS:
		print('chave ja existente: {}'.format(key))
	else:
		print('DEBUG: erro logico na insercao da chave {}'.format(key))

def query_entry(key:int):
	data_base = DataBase(FILE_PATH)
	entry = data_base.entry_by_key(key)
	if entry is not None:
		print(entry)
	else:
		print('chave nao encontrada: {}'.format(key))

#def remove_entry(key:int):
#	data_base = DataBase(FILE_PATH)
#	remove_result = data_base.delete_by_key(key)
#	if remove_result == OpStatus.OK:
#		print('chave removida com sucesso: {}'.format(key))
#	elif remove_result == OpStatus.ERR_KEY_NOT_FOUND:	
#		print('chave nao encontrada: {}'.format(key))
#	else:
#		print('DEBUG: erro logico na remocao da chave {}'.format(key))

def print_tree(): print("TODO: print_tree()")

def print_sequence(): print("TODO: print_sequence()")

def print_occupancy(): print("TODO: print_occupancy()")

def exit_shell():
	sys.exit()

#Loop principal que processa os comandos.
#entry = input()
#while entry != 'e':
#    if(entry == 'i'):
#        num_reg = input()
#        name_reg = input()
#        age_reg = input()
#        insert_entry(int(num_reg), name_reg, int(age_reg))
#    elif(entry == 'c'):
#        num_reg = input()
#        query_entry(int(num_reg))
#    #elif(entry == 'r'):
#    #    num_reg = input()
#    #    remove_entry(int(num_reg))
#    elif(entry == 'p'):
#        print_tree()
#    elif(entry == 'o'):
#        print_sequence()
#    elif(entry == 't'):
#        print_occupancy()
#    entry = input()
#exit_shell()
#Fim do loop principal.