# pysmtlib
A python layer to interface with several SMTlIBv2 enabled SMT solvers

# Features
Serializable. Able to save, replicate and send the solver state over the network
Python native integer operations. Operation on native python types are translates to smtlib transparently
Multiple solvers supported

#Example
```
        import pickle
        s = Solver()
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

```

# Tests
```
pysmtlib $ python -m unittest discover
........
----------------------------------------------------------------------
Ran 8 tests in 0.619s

OK
```
