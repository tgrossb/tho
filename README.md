# Welcome
This is a quick assembler I am writing for an instruction set I'm creating called Tho.

This assembly set will be run on my 8 bit computer, and the end goal for this project is to write something to assemble `.tho` files and 
write them to EEPROMS that can be swapped out on the breadboard.

Also included: a `.nanorc` file for the Tho instruction set.

Second bonus: Tho code to multiply two numbers and Tho code to generate some of the Fibonachi sequence.

## The assembler
The assembler is provided in the python script `ta.py`.  This script can be used to assemble a set of `.tho` files and place 
generated `.th` (binary) files in a bin directory.  This is a very simple assembler, but it works pretty well.

## The simulator
The simulator is provided in the python script `tr.py`.  This script can be used to run a `.th` file on your computer 
without needing to put it on an EEPROM and run it on my 8 bit computer.  Additionally, the simulator gives the option to 
have verbose output with `-v` or `--verbose` and manual clock stepping with `-s` or `--step`.  Verbose output provides a trace 
of the current command index, command and parameters, register, memory locations, flags, and output.  It also has some cool 
coloring, bolding, and blinking effects which I am very proud of.  The stepping functionality provides the same verbose output, but 
it requires the user to press enter to step the program counter manually for debugging.
