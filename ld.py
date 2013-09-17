import io

len_inst = 32 # inst length in bits
lit_types = {
  # typeflag -> typing fn
  0 : lambda ops, bs: int.from_bytes(bs, 'big', signed=True), # int
  1 : lambda ops, bs: bs.decode('ascii'),                     # str
  2 : lambda ops, bs: None,                                   # nil
  3 : lambda ops, bs: tuple(load(ops, io.BytesIO(bs))),       # code
}

def load(ops, infile):
  return [load_inst(ops, i, infile) for i in enum_insts(infile)]

def enum_insts(infile):
  bs = infile.read(len_inst // 8)
  while bs:
    yield int.from_bytes(bs, 'big')
    bs = infile.read(len_inst // 8)

def load_inst(ops, i, infile):
  opcode, *args = split_inst(i)
  op = ops[opcode]
  return (op, load_args(ops, args, op.mode, infile))

def load_args(ops, args, mode, infile):
  return load_lit(ops, args, infile) if mode is 4 else args[:mode]

def load_lit(ops, args, infile):
  return (args[0], lit_types[args[1]](ops, infile.read(args[2])))

def bitmask(nbits, offset):
  return sum([2**x for x in range(nbits)]) << offset

def bitselect(nbits, offset, n):
  return (n & bitmask(nbits, offset)) >> offset

def getpart(p, i):
  bitlens = (6,  5,  5,  16)
  offsets = (26, 21, 16, 0 )
  return bitselect(bitlens[p], offsets[p], i)

def split_inst(i):
  return [getpart(p,i) for p in range(4)]

