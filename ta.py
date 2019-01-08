#!/usr/bin/env python3
#########################################################################################################
#  *LDA x   -  Load the contents of memory address x into register A                      -  0001 xxxx  #
#  STA x    -  Store the contents of register A into mememory address x                   -  0010 xxxx  #
#  STO x y  -  Sets the contents of memory adress x to the literal value y                -             #
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

# Checks that a number can be represented in 4 bits
def fbc(num):
	return num >= 0 and num < 16

commands = {
	# keyword: ([param 1 checker, param 2 checker, ...], numerical representation)
	"LDA": ([fbc], 1),
	"STA": ([fbc], 2),
	"STO": ([fbc, fbc], 3),
	"ADD": ([fbc], 4),
	"SUB": ([fbc], 5),
	"JMP": ([fbc], 6),
	"JIC": ([fbc], 7),
	"JNC": ([fbc], 8),
	"JIZ": ([fbc], 9),
	"JNZ": ([fbc], 10),
	"OUT": ([], 11),
	"HLT": ([], 12),
	"NOP": ([], 13),
}

def parseArgs():
	argParser = ArgParser.ArgumentParser(prog='tc', description="A simple compiler for the Tho assembly language")
	argParser.add_argument('-b', '--bin', default='.', nargs='?', help='the directory to export interpreted ')
	argParser.add_argument('files', nargs='+', help='a list of files to interpret')
	return argParser.parse_args()


def throwError(line, lineNumber, cursorPos, errorMsg):
	print(line)
	print((" " * cursorPos) + "^")
	print("Error:", errorMsg, " (line " + str(lineNumber) + ", cursor " + str(cursorPos) + ")")
	sys.exit()


def removeComments(string):
	# Remove all single line comments from the string
	string = re.sub(re.compile("//.*?\n" ) , "",string)

	return string


def assemble(inFile, outFile):
	allLines = inFile.readlines()

	# Tokenize lines after removing comments, and flatten to a stack
	bp = re.compile("^b\d+$")
	hp = re.compile("^0x[\da-f]+$")
	dp = re.compile("^\d+$")

	currentCommand = []
	lineNumber = 0
	for line in allLines:
		strippedLine = removeComments(line).strip()

		cursorPos = 0
		for element in strippedLine.split():
			cursorPos = strippedLine.index(element, cursorPos)
			cursorEnd = cursorPos + len(element)

			# If the element matches a number pattern, parse it into a binary string
			# Numbers can be hex (0xf), binary (b1111), or decimal (15)
			if bp.match(element):
				element = int(element[1:], 2)
			elif hp.match(element):
				element = int(element[2:], 16)
			elif dp.match(element):
				element = int(element)

			# If the element is not a number, check if it is a keyword
			# If it is, just convert it to uppercase
			elif element.upper() in commands.keys():
				element = element.upper()

			# If it is neither of these, throw an error
			else:
				throwError(strippedLine, lineNumber, cursorPos, "Unrecognized keyword '%s'" % element)

			# If it is a command, start a new parameter list with the command and add it to the stack
			if isinstance(element, str):
				# When a new command has started, process the previous command and write it to the file
				if len(currentCommand) > 0:
					handleFullCommand(currentCommand, outFile)
					currentCommand.clear()
				currentCommand.append((element, lineNumber, cursorPos, cursorEnd, strippedLine))

			# If it is a number, add it to the parameter list of the latest command in the stack
			elif isinstance(element, int):
				currentCommand.append((element, lineNumber, cursorPos, cursorEnd, strippedLine))

			# This else really shouldn't ever trigger, because it should have been caught already
			else:
				throwError(strippedLine, lineNumber, cursorPos, "Assembler error")

		lineNumber += 1

	# Clean up by handling the last command in the current command as well
	handleFullCommand(currentCommand, outFile)


# Turn the command into a numerical representation
# Also check each command for parameter count and check each parameter by the check function
# Then append it to the outFile in binary
def handleFullCommand(command, outFile):
	# The first command in the command stack should be the keyword
	# Use it to get the command signature
	paramCheckers, cmdNumberRep = commands[command[0][0]]

	# Check for parameter count
	if len(command) < len(paramCheckers) + 1:
		throwError(command[-1][4], command[-1][1], command[-1][3], "Too few parameters for command '%s' (%i found, %i required)" % (command[0][0], len(command)-1, len(paramCheckers)))
	elif len(command) > len(paramCheckers) + 1:
		throwError(command[-1][4], command[-1][1], command[-1][2], "Too many parameters for command '%s' (%i found, %i required)" % (command[0][0], len(command)-1, len(paramCheckers)))

	# Check for parameter range and build a binary representation
	binary = cmdNumberRep << 12
	print("{0:04b}".format(cmdNumberRep), end = ' ')

	for paramIndex in range(0, len(paramCheckers)):
		param, paramLineNumber, paramCursor, paramEndCursor, paramLine = command[paramIndex+1]
		if not paramCheckers[paramIndex](param):
			throwError(paramLine, paramLineNumber, paramCursor, "Parameter out of range")

		# If the parameter is okay, add it to the binary representation
		binary += param << 4 * (2 - paramIndex)

		print("{0:04b}".format(param), end = ' ')
	print()


	# Turn the numerical command into a byte array and then write it to the outFile
	outFile.write(binary.to_bytes(2, byteorder='big'))


# Takes a binary number that is n bits long, appends it to the end of the queue, and write all available bytes to the output file
# Nvm, this doesn't work
binaryQueue = 0
def queueFileWrite(binary, n, outFile):
	global binaryQueue

	binaryQueue = (binaryQueue << n) + binary
	availableBytes = int(binaryQueue.bit_length()/8)
	if availableBytes == 0:
		return

	writeable = binaryQueue >> (availableBytes * 8)
	outFile.write(writeable.to_bytes(availableBytes, byteorder='big'))
	binaryQueue -= writeable

def writeExcess(outFile):
	global binaryQueue

	pass


def main(args):
	if not os.path.exists(args.bin):
		os.path.mkdir(args.bin)

	for fileName in args.files:
		if not os.path.exists(fileName):
			print("Error: File '" + fileName + "' does not exist")
			sys.exit(1)

		tcIndex = fileName.rfind(".tc")
		fileBase = fileName[0:tcIndex]
		outFile = os.path.join(args.bin, fileBase)

		with open(fileName, 'r') as inFile:
			with open(outFile, 'w+b') as outFile:
				assemble(inFile, outFile)

try:
	args = parseArgs()
	main(args)
except KeyboardInterrupt:
	print("Finishing up")
	sys.exit(0)
