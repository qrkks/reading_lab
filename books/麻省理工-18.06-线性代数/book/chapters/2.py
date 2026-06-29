import sympy as sp

A = sp.Matrix([[1, 2, 1], [3, 8, 1], [0, 4, 1]])
rref_mat, pivots = A.rref()
sp.pprint(rref_mat)
print("主元列下标：", pivots)
