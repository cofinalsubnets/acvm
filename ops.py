from vm import StackFrame, Closure

class Op():
  by_name = {}
  by_code = {}
  
  def __init__(self, name, mode, defn):
    self.name = name
    self.mode = mode
    self.defn = defn
    self.code = len(self.by_name)
    self.__doc__ = self.defn.__doc__

    # register this operation
    self.by_name[self.name] = self
    self.by_code[self.code] = self

  def __call__(self, *args):
    self.defn(*args)

def savr(vm, r):
  'save the contents of a register on the stack'
  vm.frame.vstack.append(vm[r])

def rstr(vm, r):
  'pop a value off of the stack and into a register'
  vm[r] = vm.frame.vstack.pop()

def loadm(vm, r, n, i):
  'load a lexically bound value into a register'
  vm[r] = vm.frame.closure.lexaddr(n, i)

def loadr(vm, d, o):
  'load a value from a register into another register'
  vm[d] = vm[o]

def vecl(vm, r, n):
  'create a new vector with the given length'
  vm[r] = [None for _ in range(n)]

def vec(vm, r, n):
  'create a new vector with length stored in the register named by the second argument'
  vecl(vm, r, vm[n])

def svecl(vm, v, i, n):
  'set the contents of the named index of a vector from a named register'
  vm[v][i] = vm[n]

def svec(vm, v, i, n):
  'set the contents of the index held in a named register from another register'
  svecl(vm, v, vm[i], n)

def gvecl(vm, d, v, i):
  'get the contents of the named index of a vector and place it in a named register'
  vm[d] = vm[v][i]

def gvec(vm, d, v, i):
  'get the contents of the index held in a named register and place it in another register'
  gvecl(vm, d, v, vm[i])

def eq(vm, d, a, b):
  'd := a is b'
  vm[d] = vm[a] is vm[b]

def lt(vm, d, a, b):
  'd := a < b'
  vm[d] = vm[a] < vm[b]

def negt(vm, d, o):
  'd := -o'
  vm[d] = not vm[o]

def add(vm, d, a, b):
  'd := a + b'
  _arithop('__add__', d, a, b)

def mul(vm, d, a, b):
  'd := a * b'
  _arithop('__mul__', d, a, b)

def sub(vm, d, a, b)   :
  'd := a - b'
  _arithop('__sub__', d, a, b)

def div(vm, d, a, b)   :
  'd := a / b'
  _arithop('__truediv__', d, a, b)

def conj(vm, d, a, b):
  'd := a and b'
  _arithop('__and__', d, a, b)

def disj(vm, d, a, b):
  'd := a or b'
  _arithop('__or__', d, a, b)

def jmp(vm, r):
  'set PC from the contents of a register'
  vm.frame.pc = vm[r]

def host(vm, d, f, a):
  'call a python function'
  vm[d] = vm.val = vm[f](vm[a])

def loadl(vm, d, v):
  'load a literal value into a register'
  vm[d] = v

def cons(vm, r, a, d):
  'convenience operation for creating a two-element vector with contents taken from given registers'
  vm[r] = [vm[a], vm[d]]

def clos(vm, d, c):
  'enclose raw code in the current lexical scope, making it callable, and place in register named by d'
  vm[d] = (vm.frame.closure, vm[c])

def getv(vm, d):
  'load the last return value into a register'
  vm[d] = vm.val

def ccc(vm, fn):
  'call-with-current-continuation'
  appl(vm, fn, [vm.frame])

def cond(vm, r):
  'execute an instruction conditionally on the contents of the given register'
  if not vm[r]: vm.frame.pc += 1

def rcur(vm, bs):
  're-execute the current function with a new argument vector, without creating a new stack frame'
  vm.frame.closure, vm.frame.pc = Closure(vm[bs], vm.frame.closure.parent), -1

def rtrn(vm, v):
  'return from the current function call & pop the current frame off the stack'
  vm.val, vm.frame = vm[v], vm.frame.parent

def appl(vm, fn, bs):
  'function application'
  if isinstance(fn, StackFrame): # continuation
    vm.val, v.frame = bs[0], fn
  else:
    (cl, body), bs = vm[fn], vm[bs]
    closure = Closure(bs, cl)
    if vm.frame.pc == len(vm.frame.prog) - 1: # tail call
      vm.frame.pc = -1
      vm.frame.closure = closure
      vm.frame.prog = body
      vm.frame.vstack = []
    else:
      vm.frame = StackFrame(closure, [], body, -1, vm.frame)

def _arithop(vm, op, d, a, b):
  vm[d] = getattr(vm[a], op)(vm[b])

Op(  'clos'  ,     2,  clos)
Op(  'savr'  ,     1,  savr)
Op(  'rstr'  ,     1,  rstr)
Op(  'appl'  ,     2,  appl)
Op(  'loadm' ,     3,  loadm)
Op(  'loadr' ,     2,  loadr)
Op(  'vecl'  ,     2,  vecl)
Op(  'vec'   ,     2,  vec)
Op(  'svecl' ,     3,  svecl)
Op(  'svec'  ,     3,  svec)
Op(  'gvecl' ,     3,  gvecl)
Op(  'gvec'  ,     3,  gvec)
Op(  'eq'    ,     3,  eq)
Op(  'lt'    ,     3,  lt)
Op(  'not'   ,     2,  negt)
Op(  'rcur'  ,     1,  rcur)
Op(  'rtrn'  ,     1,  rtrn)
Op(  'cond'  ,     1,  cond)
Op(  'add'   ,     3,  add)
Op(  'mul'   ,     3,  mul)
Op(  'sub'   ,     3,  sub)
Op(  'div'   ,     3,  div)
Op(  'and'   ,     3,  conj)
Op(  'or'    ,     3,  disj)
Op(  'jmp'   ,     1,  jmp)
Op(  'loadl' ,     4,  loadl)
Op(  'cons'  ,     3,  cons)
Op(  'getv'  ,     1,  getv)
Op(  'ccc'   ,     1,  ccc)

by_name = Op.by_name
by_code = Op.by_code

