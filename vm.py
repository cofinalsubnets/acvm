class StackFrame():
  def __init__(self, closure, valstack, prog, pc, parent=None):
    self.closure = closure
    self.vstack = valstack
    self.prog = prog
    self.pc = pc
    self.parent = parent

class Closure():
  def __init__(self, bindings=(), parent=None):
    self.bindings, self.parent = bindings, parent

  def lexaddr(self, n, i):
    for _ in range(n): self = self.parent
    return self.bindings[i]

class VM():
  num_registers = 8
  def __init__(self, nr=num_registers):
    self.val, self.frame, self.registers = None, None, [None for _ in range(nr)]

  def __getitem__(self, i):
    return self.registers[i]

  def __setitem__(self, i, v):
    self.registers[i] = v

  def run(self):
    while self.frame:
      self.frame.pc += 1
      if self.frame.pc < len(self.frame.prog):
        op, args = self.frame.prog[self.frame.pc]
        op(self, *args)
      else:
        self.val, self.frame = None, self.frame.parent

  def load(self, prog):
    self.frame = StackFrame(Closure(), [], prog, -1)

