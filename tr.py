#!/usr/bin/env python3

import sys
import os
import argparse as ArgParser

LDA = 1
STA = 2
STO = 3
ADD = 4
SUB = 5
JMP = 6
JIC = 7
JNC = 8
JIZ = 9
JNZ = 10
OUT = 11
HLT = 12
NOP = 13

NORMAL = '\033[0m'
GREEN = '\033[42m'
YELLOW = '\033[43m'
BLUE = '\033[44m'
BOLD = '\033[1m'
BLINK = '\033[5m'

CHECK = u'\u2713'
BOLD_CHECK = u'\u2714'
X = u'\u2717'
BOLD_X = u'\u2718'

LAST = '\033[F'

cmdStrs = ["-", "LDA", "STA", "STO", "ADD", "SUB", "JMP", "JIC", "JNC", "JIZ", "JNZ", "OUT", "HLT", "NOP"]

hexFirstParam = [LDA, STA, STO, ADD, SUB]

aRegister = 0
memory = [0]*16
zeroFlag = True
carryFlag = False

def parseArgs():
	argParser = ArgParser.ArgumentParser(prog='sim', description="A simple simulator for the Tho assembly language")
	argParser.add_argument('file', help='the file to be simulated')
	argParser.add_argument('-s', '--step', action='store_true', help='controls if the user must step the simulation for debugging purposes (automatically sets -v)')
	argParser.add_argument('-v', '--verbose', action='store_true', help='controls if memory, register, and flags should be printed at each clock tick')
	return argParser.parse_args()


def splitByte(byte):
	set1 = byte >> 4
	set2 = byte - (set1 << 4)
	return (set1, set2)


def calculateFlags(highlights):
	global zeroFlag, carryFlag, aRegister

#	newCarryFlag = aRegister > 15
#	if newCarryFlag:
#		aRegister = 0
	newCarryFlag = True

	newZeroFlag = aRegister == 0


	if not newZeroFlag == zeroFlag:
		highlights[-3] = YELLOW
	if not newCarryFlag == carryFlag:
		highlights[-2] = YELLOW

	zeroFlag = newZeroFlag
	carryFlag = newCarryFlag

previousLine = ""
def simulate(inFile, step, verbose):
	global aRegister, memory, zeroFlag, carryFlag, previousLine

	byteLine = inFile.readlines()[0]

	longestCmdIndex = len(str(len(byteLine)//2))
	longestCmdIndex = longestCmdIndex if longestCmdIndex > 2 else 2

	if verbose or step:
		formatter = "{b}|{n} {0: <{lci}} {b}|{n}  INS  p1   p2   p3   {b}|{n} REG {b}|{n} 0x0 | 0x1 | 0x2 | 0x3 | 0x4 | 0x5 | 0x6 | 0x7 | 0x8 | 0x9 | 0xA | 0xB | 0xC | 0xD | 0xE | 0xF {b}|{n} ZFl | CFl {b}|{n} OUT {b}|{n}"
		print(formatter.format("CI", b = BOLD, n = NORMAL, lci = longestCmdIndex))
		print("-" * (longestCmdIndex + 147))

	commandIndex = 0
	while commandIndex < len(byteLine)/2:
		highlight = [NORMAL] * 21

		cmd, p1 = splitByte(byteLine[commandIndex*2])
		p2, p3 = splitByte(byteLine[commandIndex*2+1])

		nextIndex = commandIndex + 1

		# LDA xxxx 0000 0000  =>  Put the value of memory address xxxx into the a register
		if cmd == LDA:
			aRegister = memory[p1]
			highlight[1] = GREEN
			highlight[p1+2] = BLUE
			calculateFlags(highlight)

		# STA xxxx 0000 0000  =>  Put the value of the a register into memory address xxxx
		elif cmd == STA:
			memory[p1] = aRegister
			highlight[p1+2] = GREEN
			highlight[1] = BLUE

		# STO xxxx yyyy 0000  =>  Set the value at memory address xxxx to the literal yyyy
		elif cmd == STO:
			memory[p1] = p2
			highlight[p1+2] = GREEN

		# ADD xxxx 0000 0000  =>  Add the value at memory address xxxx to the a register and calculate flags
		elif cmd == ADD:
			aRegister += memory[p1]
			highlight[1] = GREEN
			highlight[p1+2] = BLUE
			calculateFlags(highlight)

		# SUB xxxx 0000 0000  =>  Subtract the value at memory address xxxx from the a register and calculate flags
		elif cmd == SUB:
			aRegister -= memory[p1]
			highlight[1] = GREEN
			highlight[p1+2] = BLUE
			calculateFlags(highlight)

		# JMP xxxx 0000 0000  =>  Move the program counter to xxxx
		elif cmd == JMP:
			commandIndex = p1
			highlight[0] = YELLOW

		# JIC xxxx 0000 0000  =>  Move the program counter to xxxx if the carry flag is set
		elif cmd == JIC:
			highlight[-2] = BLUE
			if carryFlag:
				nextIndex = p1
				highlight[0] = YELLOW

		# JNC xxxx 0000 0000  =>  Move the program counter to xxxx if the carry flag is not set
		elif cmd == JNC:
			highlight[-2] = BLUE
			if not carryFlag:
				nextIndex = p1
				highlight[0] = YELLOW

		# JIZ xxxx 0000 0000  =>  Move the program counter to xxxx if the zero flag is set
		elif cmd == JIZ:
			highlight[-3] = BLUE
			if zeroFlag:
				nextIndex = p1
				highlight[0] = YELLOW

		# JNZ xxxx 0000 0000  =>  Move the program counter to xxxx if the zero flag is not set
		elif cmd == JNZ:
			highlight[-3] = BLUE
			if not zeroFlag:
				nextIndex = p1
				highlight[0] = YELLOW

		# OUT 0000 0000 0000  =>  Print the value of the a register (we'll get this later)
		elif cmd == OUT:
			highlight[1] = BLUE
			highlight[-1] = GREEN

		# HLT 0000 0000 0000  =>  Exit the program
		elif cmd == HLT:
			print(LAST + "HALT REACHED")
			sys.exit(0)

		# NOP 0000 0000 0000  =>  Do nothing
		elif cmd == NOP:
			pass

		else:
			print("Unrecognized operation '" + cmd + "'")

		if verbose or step:
			if len(previousLine) > 0:
				print(LAST *2 + previousLine.replace(BLINK, ''))

			line = ""
			p1Str = "0x{0:X}".format(p1) if cmd in hexFirstParam else "{0}".format(p1)

			# Command index
			line += BOLD + "|" + NORMAL
			line += color(" {0: <{lci}} ".format(commandIndex, lci = longestCmdIndex), highlight[0])
			line += BOLD + "|" + NORMAL + "  "

			# Command and params
			line += "{0}  {1: <3}  {2: <3}  {3: <3}  {4}|{5}".format(cmdStrs[cmd], p1Str, p2, p3, BOLD, NORMAL)

			# Register
			line += color(str(aRegister).center(5), highlight[1])
			line += BOLD + "|" + NORMAL

			# Memory addresses
			for memIndex in range(len(memory)):
				line += color(str(memory[memIndex]).center(5), highlight[memIndex+2])
				line += "|" if memIndex < len(memory)-1 else BOLD + "|" + NORMAL

			# Zero flag
			line += color((CHECK if zeroFlag else X).center(5), highlight[-3]) + "|"

			# Carry flag
			line += color((CHECK if carryFlag else X).center(5), highlight[-2])
			line += BOLD + "|" + NORMAL

			if cmd == OUT:
				line += color(str(aRegister).center(5), highlight[-1])
				line += BOLD + "|" + NORMAL
			else:
				line += BOLD + "     |" + NORMAL

			print(line)
			previousLine = line

		elif cmd == OUT:
			print("A REGISTER OUTPUT: " + str(aRegister))

		commandIndex = nextIndex

		if step:
			input("")
		elif verbose:
			print()


def color(text, color, boldColors = [GREEN, BLUE, YELLOW], blinkColors = [GREEN, YELLOW], end = ''):
	colorMods = ""

	if color in boldColors:
		colorMods += BOLD
		text = text.replace(CHECK, BOLD_CHECK).replace(X, BOLD_X)
	if color in blinkColors:
		colorMods += BLINK

	return color + colorMods + text + NORMAL



def main(args):
	if not os.path.exists(args.file):
		print("Error: File '" + args.file + "' does not exist")
		sys.exit(1)

	with open(args.file, 'rb') as inFile:
		simulate(inFile, args.step, args.verbose)

if __name__ == "__main__":
	try:
		args = parseArgs()
		main(args)
	except KeyboardInterrupt:
		if args.verbose or args.step:
			print(LAST + previousLine.replace(BLINK, '') + "\nExiting prematurely")
		else:
			print("\nExiting prematurely")
		sys.exit(0)
