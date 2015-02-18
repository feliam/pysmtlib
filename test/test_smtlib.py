# Copyright (c) 2013, Felipe Andres Manzano
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from smtlib import *
# from smtlibv2 import CVC4Solver as Solver
import unittest
import fcntl
import resource
import gc
import sys
#logging.basicConfig(filename = "test.log",
#                format = "%(asctime)s: %(name)s:%(levelname)s: %(message)s",
#                level = logging.DEBUG)

class ExpressionTest(unittest.TestCase):
    def get_open_fds(self):
        fds = []
        for fd in range(3, resource.RLIMIT_NOFILE):
            try:
                flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            except IOError:
                continue
            fds.append(fd)
        return fds

    def setUp(self):
        self.fds = self.get_open_fds()

        self.engine = 'z3'

    def tearDown(self):
        gc.collect()
        gc.garbage = []
        self.assertEqual(self.fds, self.get_open_fds())

    def checkLeak(self, s):
        import gc, pickle
        s_str = pickle.dumps(s)
        del s
        s1 = pickle.loads(s_str)
        s2 = pickle.loads(s_str)
        del s1
        del s2
        gc.collect()
        self.assertEqual(gc.garbage, [])

    '''
    def testBasicAST(self):
        a = Symbol(1)
        b = Symbol(2)
        c = Symbol('+', a, b)
        self.assertTrue(a.isleaf)
        self.assertTrue(b.isleaf)
        self.assertFalse(c.isleaf)
        self.assertEqual(c.children, (a,b))
    '''

    def testSolver(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a+b>100)
        self.assertEqual(s.check(), 'sat')
        self.checkLeak(s)

    def testBool(self):
        s = Solver(self.engine)
        bf = Bool('false')
        bt = Bool('true')
        s.add( bf & bt )
        self.assertEqual(s.check(), 'unsat')
        self.checkLeak(s)

    def testBasicArray(self):
        s = Solver(self.engine)
        #make array of 32->8 bits
        array = s.mkArray(32)
        #make free 32bit bitvector 
        key = s.mkBitVec(32)

        #assert that the array is 'A' at key position
        s.add(array[key] == 'A')
        #lets restrict key to be greater than 1000
        s.add(key.ugt(1000))

        s.push()
        #1001 position of array can be 'A'
        s.add(array[1001] == 'A')
        self.assertEqual(s.check(), 'sat')
        s.pop()

        s.push()
        #1001 position of array can also be 'B'
        s.add(array[1001] == 'B')
        self.assertEqual(s.check(), 'sat')
        s.pop()

        s.push()
        #but if it is 'B' ...
        s.add(array[1001] == 'B')
        #then key can not be 1001
        s.add(key == 1001)
        self.assertEqual(s.check(), 'unsat')
        s.pop()

        s.push()
        #If 1001 position is 'B' ...
        s.add(array[1001] == 'B')
        #then key can be 1000 for ex..
        s.add(key == 1002)
        self.assertEqual(s.check(), 'sat')
        s.pop()
        #self.checkLeak(s)


    def testBasicArrayStore(self):
        s = Solver(self.engine)
        #make array of 32->8 bits
        array = s.mkArray(32)
        #make free 32bit bitvector 
        key = s.mkBitVec(32)

        #assert that the array is 'A' at key position
        array[key] = 'A'
        #lets restrict key to be greater than 1000
        s.add(key.ugt(1000))
        s.push()
        #1001 position of array can be 'A'
        s.add(array[1001] == 'A')
        self.assertEqual(s.check(), 'sat')
        s.pop()

        s.push()
        #1001 position of array can also be 'B'
        s.add(array[1001] == 'B')
        self.assertEqual(s.check(), 'sat')
        s.pop()

        s.push()
        #but if it is 'B' ...
        s.add(array[1001] == 'B')
        #then key can not be 1001
        s.add(key == 1001)
        self.assertEqual(s.check(), 'unsat')
        s.pop()

        s.push()
        #If 1001 position is 'B' ...
        s.add(array[1001] == 'B')
        #then key can be 1000 for ex..
        s.add(key != 1002)
        self.assertEqual(s.check(), 'sat')
        s.pop()
        self.checkLeak(s)


    def testBasicPickle(self):
        import pickle
        s = Solver(self.engine)
        #make array of 32->8 bits
        array = s.mkArray(32)
        #make free 32bit bitvector 
        key = s.mkBitVec(32)

        #assert that the array is 'A' at key position
        array[key] = 'A'
        #lets restrict key to be greater than 1000
        s.add(key.ugt(1000))
        s = pickle.loads(pickle.dumps(s))
        self.assertEqual(s.check(), 'sat')
        self.checkLeak(s)

    def testBitvector_add(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a+b)
        s.add(a == 1)
        s.add(b == 10)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 11)
        self.checkLeak(s)

    def testBitvector_add1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a+10)
        s.add(a == 1)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 11)
        self.checkLeak(s)

    def testBitvector_add2(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(11==a+10)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(a), 1)
        self.checkLeak(s)

    def testBitvector_mul(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a*b)
        s.add(a == 5)
        s.add(b == 7)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 35)
        self.checkLeak(s)

    def testBitvector_mul1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a*b)
        s.add(a == 5)
        s.add(b == -7)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), (-35) & 2**32-1)
        self.checkLeak(s)

    def testBitvector_mul2(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a*b)
        s.add(a == -5)
        s.add(b == -7)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 35)
        self.checkLeak(s)

    def testBitvector_mod(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a%b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 2)
        self.checkLeak(s)

    def testBitvector_lshift(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a<<b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 7 << 5)
        self.checkLeak(s)

    def testBitvector_rshift(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a>>b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 7 >> 5)
        self.checkLeak(s)

    def testBitvector_and(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a & b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 7 & 5)
        self.checkLeak(s)

    def testBitvector_xor(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a ^ b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 7 ^ 5)
        self.checkLeak(s)

    def testBitvector_or(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a | b)
        s.add(a == 7)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 7 | 5)
        self.checkLeak(s)

    def testBitvector_div(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a / b)
        s.add(a == 15)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 15 / 5)
        self.checkLeak(s)

    def testBitvector_div1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a / b)
        s.add(a == -15)
        s.add(b == 5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), (-15 / 5) & 2**32-1)
        self.checkLeak(s)

    def testBitvector_div2(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(c==a / b)
        s.add(a == 15)
        s.add(b == -5)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), (15 / -5) & 2**32-1)
        self.checkLeak(s)

    def testBitvector_invert(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(b==~a)
        s.add(a == 15)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(b), (~15) & 2**32-1)
        self.checkLeak(s)

    def testBitvector_lt(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a < b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) < s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_lt1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a == -2)
        s.add(b == -1)
        s.add(a < b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) < s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_lt2(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a == -2)
        s.add(a < b)
        a_value = s.getvalue(a) & (2**32-1)
        b_value = s.getvalue(b) & (2**32-1)
        # print a_value
        # print b_value
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) < s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_le(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a <= b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) <= s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_eq(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a == b)
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(a), s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_ne(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a != b)
        self.assertEqual(s.check(), 'sat')
        self.assertNotEqual(s.getvalue(a), s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_gt(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a > b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) > s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_gt1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a == -1)
        s.add(b == -2)
        s.add(a > b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) > s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_gt1(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a == -1)
        s.add(a > b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) > s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_ge(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a >= b)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) >= s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_ugt(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a.ugt(b))
        s.add(a == 15)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) > s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_uge(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a.uge(b))
        s.add(a == 15)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) >= s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_ult(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a.ult(b))
        s.add(a == 15)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) < s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_ule(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        s.add(a.ule(b))
        s.add(a == 15)
        self.assertEqual(s.check(), 'sat')
        self.assertTrue(s.getvalue(a) <= s.getvalue(b))
        self.checkLeak(s)

    def testBitvector_udiv(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(a == 15)
        s.add(b == 5)
        s.add(c == a.udiv(b))
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 3)
        self.checkLeak(s)

    def testBitvector_rudiv(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(a == 5)
        s.add(b == 15)
        s.add(c == a.rudiv(b))
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 3)
        self.checkLeak(s)

    def testBitvector_urem(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(a == 7)
        s.add(b == 5)
        s.add(c == a.urem(b))
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 2)
        self.checkLeak(s)

    def testBitvector_rurem(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        b = s.mkBitVec(32)
        c = s.mkBitVec(32)
        s.add(a == 5)
        s.add(b == 7)
        s.add(c == a.rurem(b))
        self.assertEqual(s.check(), 'sat')
        self.assertEqual(s.getvalue(c), 2)
        self.checkLeak(s)

    def testSolver_getallvalues(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        s.add(a >= 10)
        self.assertEqual(s.check(), 'sat')
        values = s.getallvalues(a)
        for value in values:
            # print value, type(value)
            self.assertGreaterEqual(value, 10)
        self.checkLeak(s)

    def testSolver_max(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        s.add(a >= 10)
        s.add(a <= 100)
        self.assertEqual(s.check(), 'sat')
        # print s.max(a)
        self.assertEqual(s.max(a), 100)
        self.checkLeak(s)

    def testSolver_min(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        s.add(a >= 10)
        s.add(a <= 100)
        self.assertEqual(s.check(), 'sat')
        # print s.min(a)
        self.assertEqual(s.min(a), 10)
        self.checkLeak(s)

    def testSolver_minmax(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32)
        s.add(a >= 10)
        s.add(a <= 100)
        self.assertEqual(s.check(), 'sat')
        min_val, max_val = s.minmax(a)
        self.assertEqual(min_val, 10)
        self.assertEqual(max_val, 100)
        self.checkLeak(s)

    def testSolver_mkBitVec(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32, 'BV')
        decls = s.declarations
        self.assertEqual(decls[0].declaration, '(declare-fun BV () (_ BitVec 32))')
        self.checkLeak(s)

    def testSolver_mkBool(self):
        s = Solver(self.engine)
        a = s.mkBool('B')
        decls = s.declarations
        self.assertEqual(decls[0].declaration, '(declare-fun B () Bool)')
        self.checkLeak(s)

    def testSolver_mkArray(self):
        s = Solver(self.engine)
        a = s.mkArray(32, 'A')
        decls = s.declarations
        self.assertEqual(decls[0].declaration, '(declare-fun A () (Array (_ BitVec 32) (_ BitVec 8)))')
        self.checkLeak(s)

    def testSolver_constraints(self):
        s = Solver(self.engine)
        a = s.mkBitVec(32, 'A')
        b = s.mkBitVec(32, 'B')
        s.add(a == b)
        constrs = s.constraints
        self.assertEqual(constrs[0], '(assert (= A B))')
        self.checkLeak(s)

if __name__ == '__main__':
    unittest.main()

