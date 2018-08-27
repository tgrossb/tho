#!/usr/bin/env python3
#########################################################################################################
#  *LDA x    -  Load the contents of memory address x into register A                     -  0001 xxxx  #
#  STA x    -  Store the contents of register A into mememory address x                   -  0010 xxxx  #
#  SET x y  -  Sets the contents of memory adress x to the literal value y                -             #
#  *ADD x   -  Adds the contents of memory address x to the contents of register A        -  0011 xxxx  #
#  *SUB x   -  Subtracts the contents of memory adress x from the contents of register A  -  0100 xxxx  #
#  JMP x    -  Sets the program counter to x                                              -  0101 xxxx  #
#  JIC x    -  Jumps to x if the carry flag is set                                        -  0110 xxxx  #
#  JNC x    -  Jumps to x if the carry flag is not set                                    -  0111 xxxx  #
#  JIZ x    -  Jumps to x if the contents of register A is zero                           -  1000 xxxx  #
#  JNZ x    -  Jumps to x if the contents of register A is not zero                       -  1001 xxxx  #
#  OUT      -  Outputs the contents of register A to the display                          -  1010 0000  #
#  HLT      -  Halt, stop the program counter from incrementing                           -  1011 0000  #
#  NOP      -  No operation                                                               -  0000 0000  #
#                                                                                                       #
#  *This operation calculates the carry, not carry, zero, and not zero flag values                      #
#########################################################################################################

import sys
import os
import re
import argparse as ArgParser

commands = {
	# command: ([param 1 length, param 2 length, ...], binary representation)
	"LDA": ([4], "0001"),
	"STA": ([4], "0010"),
	"SET": ([4, 4], "1100"),
	"ADD": ([4], "0011"),
	"SUB": ([4], "0100"),
	"JMP": ([4], "0101"),
	"JIC": ([4], "0110"),
	"JNC": ([4], "0111"),
	"JIZ": ([4], "1000"),
	"JNZ": ([4], "1001"),
	"OUT": ([], "1010"),
	"HLT": ([], "1011"),
	"NOP": ([], "0000"),
}

def parseArgs():
	argParser = ArgParser.ArgumentParser(prog='tc', description="A simple compiler for the Tho assembly language")
	argParser.add_argument('-b', '--bin', default='.', nargs='?', help='the directory to export interpreted ')
	argParser.add_argument('files', nargs='+', help='a list of files to interpret')
	return argParser.parse_args()


def removeComments(string):
	# Remove all single line comments from the string
	string = re.sub(re.compile("//.*?\n" ) , "",string)

	return string


def compile(file):
	allLines = file.readlines()

	# Tokenize lines after removing comments
	elementStack = []
	for line in allLines:
		strippedLine = removeComments(line).strip()
		if len(strippedLine) == 0:
			elementStack.append([])
		else:
			lineStack = []
			for element in strippedLine.split():
				lineStack.append(element)
			elementStack.append(lineStack)

	# Handle the element stack as a flat stack


def main(args):
	for fileName in args.files:
		if not os.path.exists(fileName):
			print("Error: File '" + fileName + "' does not exist")
			os.exit(1)
		with open(fileName, 'r') as file:
			compile(file)

try:
	args = parseArgs()
	main(args)
except KeyboardInterrupt:
	print("Finishing up")
	sys.exit(0)
