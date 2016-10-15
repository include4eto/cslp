#!/usr/bin/env python3

import sys
from input_parser import *

def print_usage():
	print('Usage: TODO')

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print_usage()
		sys.exit(0)
	
	file_path = sys.argv[1]
	 
	# create the parser
	parser = InputParser(file_path)
	result = parser.parse()

	if not result:
		print('Parse errors occurred. Exiting...')
		for i in (parser.parse_errors + parser.parse_warnings):
			print(i)

		sys.exit(1)
	
	print('Configuration read from {0}.'.format(file_path))
	print('Exiting.')
	