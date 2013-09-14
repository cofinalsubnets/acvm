#!/usr/bin/env python
import re
import io

def assemble(ops, infile, outfile):
  return sum(map(outfile.write, asm_chunks(ops, infile)))

def asm_chunks(ops, infile): # gives 1 chunk per instruction
  return map(lambda i: asm_inst(ops, i, infile), enum_insts(infile))

def enum_insts(infile):
  l = infile.readline()
  while l:
    l = re.sub(';.*','',l).strip()
    if l: yield l
    l = infile.readline()

def asm_inst(ops, i, infile):
  opname, *args = i.split()
  op = ops[opname]
  if op.mode is 4:
    return asm_lit_inst(ops, op, args, infile)
  else:
    return asm_basic_inst(op, map(int, args))

def asm_lit_inst(ops, op, args, infile):
  _, typef, lit = args
  lit = lit_type_handlers[int(typef)](ops, lit, infile)
  args[2] = len(lit)
  return asm_basic_inst(op, map(int, args)) + lit

def asm_basic_inst(op, args):
  return sum_inst(op.code, *args).to_bytes(4, 'big')

def sum_inst(opcode, a=0, b=0, c=0):
  return (opcode<<26) + (a<<21) + (b<<16) + c


# literal encoding functions

def asm_int_lit(ops, lit, infile):
  lit = int(lit)
  return lit.to_bytes(lit.bit_length() // 8 + 1, 'big', signed=True)

def asm_str_lit(ops, lit, infile):
  return bytes(lit, 'ascii')

def asm_nil_lit(ops, lit, infile):
  return bytes()

def asm_asm_lit(ops, lit, infile):
  chunks = asm_chunks(ops, infile)
  return b''.join([next(chunks) for _ in range(int(lit))])

# end literal encoding functions


lit_type_handlers = {
  0 : asm_int_lit,
  1 : asm_str_lit,
  2 : asm_nil_lit,
  3 : asm_asm_lit,
}

if __name__ == '__main__':
  import sys
  import argparse
  import ops

  parser = argparse.ArgumentParser()
  parser.add_argument('infile', nargs='?',
                      type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument('outfile', nargs='?',
                      type=argparse.FileType('bw'), default=sys.stdout)

  args = parser.parse_args()

  print("%s bytes written" % assemble(ops.by_name, args.infile, args.outfile))

