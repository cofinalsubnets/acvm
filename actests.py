#!/usr/bin/env python
import unittest
import vm
import assembler
import loader
import ops
import io

class LoaderTests(unittest.TestCase):
  def test_split_inst(self):
    inst = (41<<26) + (9<<21) + (13<<16) + 2
    opc, a, b, c = loader.split_inst(inst)
    self.assertEqual(opc, 41)
    self.assertEqual(a,    9)
    self.assertEqual(b,   13)
    self.assertEqual(c,    2)

  def test_load_compiled(self):
    op, args = ops.by_name['gvecl'], (1,2,3)
    bstr = io.BytesIO(assembler.asm_basic_inst(op, args))
    ((f,args),) = loader.load(ops.by_code, bstr)
    self.assertIs(f, op)
    self.assertSequenceEqual(args, args)

class AssemblerTests(unittest.TestCase):
  def test_sum_inst(self):
    expected = (10<<26) + (1<<21) + (2<<16) + 3
    self.assertEqual(assembler.sum_inst(10, 1, 2, 3), expected)

  def test_asm_inst(self):
    op, args = ops.by_name['gvecl'], (1,2,3)
    expected_val   = 0b00101000001000100000000000000011
    expected_bytes = expected_val.to_bytes(4, 'big') 
    self.assertEqual(assembler.asm_basic_inst(op, args), expected_bytes)

class AsmTest(unittest.TestCase):
  def assemble(self, src):
    infile, outfile = io.StringIO(src), io.BytesIO()
    assembler.assemble(ops.by_name, infile, outfile)
    return list(loader.load(ops.by_code, io.BytesIO(outfile.getvalue())))

  def assertAssemblesTo(self, wasm, expected):
    self.assertSequenceEqual(self.assemble(wasm), expected)

  def assertEvalsTo(self, wasm, val):
    v = vm.VM()
    v.load(self.assemble(wasm))
    v.run()
    self.assertEqual(v.val, val)

class ProgTests(AsmTest):

  def test_assq_prog(self):
    wasm = """
      loadl 0 3 15 ; load the next 15 instructions into register 0

      ;; start subroutine
      ;; this is acvm assembly language for `assq'
      loadm 0 0 0 ; [key]
      loadm 1 0 1 ; [key | alist]
      loadl 2 2 0 ; [key | alist | nil]
      eq    2 1 2 ; [key | alist | (eq? alist nil)]
      cond  2     ; if (eq? alist nil)
      rtrn  1     ; return alist (== nil)
      loadl 3 0 0 ; [key | alist | (bool) | 0]
      gvecl 2 1 0 ; [key | alist | (car alist) | 0]
      gvecl 3 2 0 ; [key | alist | (car alist) | (caar alist)]
      eq    3 0 3 ; [key | alist | (car alist) | (eq? key (caar alist))]
      cond  3     ; if (eq? key (caar alist))
      rtrn  2     ; return (car alist)
      gvecl 1 1 1 ; [key | (cdr alist) | ...]
      cons  2 0 1
      rcur  2
      ;; end subroutine

      clos  0 0    ; make code callable by attaching a closure

      loadl 2 1 c  ; build argument vector
      loadl 3 0 3  ; start by consing together the 2nd argument
      loadl 4 2 0
      cons  1 2 3
      cons  1 1 4

      loadl 2 1 b
      loadl 3 0 2
      cons  4 2 3
      cons  1 4 1

      loadl 2 1 a
      loadl 3 0 1
      cons  4 2 3
      cons  1 4 1

      loadr 3 1
      loadl 2 1 b
      cons  1 2 3  ; now the argument vector is in register 1

      appl  0 1    ; apply assq
    """

    self.assertEvalsTo(wasm, ['b', 2])


class InstTests(AsmTest):
  def test_loadl_int(self):
    i1 = 51452145
    i2 = -145146

    wasm = """
      loadl 0 0 %d
      loadl 1 0 %d
    """ % (i1, i2)

    self.assertAssemblesTo(wasm,
      [ (ops.by_name['loadl'], (0, i1)),
        (ops.by_name['loadl'], (1, i2)),
      ])

  def test_loadl_none(self):
    wasm = """
      loadl 0 2 %s
      loadl 1 2 %s
    """ % (1425142, 'aewrwaer')

    self.assertAssemblesTo(wasm,
      [ (ops.by_name['loadl'], (0, None)),
        (ops.by_name['loadl'], (1, None)),
      ])

  def test_loadl_str(self):
    s1 = str(251245)
    s2 = 'aewrqwetrwfawr'

    wasm = """
      loadl 0 1 %s
      loadl 1 1 %s
    """ % (s1,s2)

    self.assertAssemblesTo(wasm,
      [ (ops.by_name['loadl'], (0, s1)),
        (ops.by_name['loadl'], (1, s2)),
      ])

  def test_loadl_insts(self):
    wasm = """
      loadl 0 3 1
      add   2 3 4
    """
    self.assertAssemblesTo(wasm, [
      (ops.by_name['loadl'], (0, ((ops.by_name['add'], [2, 3, 4]),)))
      ])

if __name__ == '__main__':
  unittest.main()

