import xlrd
import numpy as np
from ortools.constraint_solver import pywrapcp
from pprint import pprint
import re
from misc import timeme:

def display_solution(cells):
    rows, cols = 0,0
    for (i,j), val in cells.items():
        if i+1 >= rows: rows = i+1
        if i+1 >= cols: cols = j+1
        
    for i in range(rows):
        for j in range(cols):
            if (i,j) in cells:
                print(cells[i,j].Value(), end=' ')
            else:
                print(" ", end=' ')
        print()
        
def load_calcudoku(filename):

    from itertools import product
    str_in = open(filename).read().replace('x','*')
    lines = [i.split('#')[0].strip() for i in str_in.split('\n')]
    lines = [i for i in lines if i]

    lwdth = len(lines[0])
    for i in lines:
        if len(i)!=lwdth:
            raise ValueError('Lines in calcudoku puzzle is not the same length:\n'+'\n'.join(lines))

    N = int(len(lines)/2)
    cwdth = int(lwdth/N)
    twdth = cwdth-1

    cellidx = {}
    for i,j in product(range(N),range(N)):
        cellidx[i,j] = (i*2+1,j*(cwdth)+1)

    for i,j in product(range(N),range(N)):
        ii,jj = cellidx[i,j]

    cageid  = {'cage'+str((i,j)):[(i,j)] for i,j in product(range(N),range(N))}

    def is_valid(i,j):
        if i<0 or j<0 or i>=N or j>=N:
            return False
        return True

    def merge(idx0, idx1):
        id0 = [id for id, cells in cageid.items() if idx0 in cells][0]
        id1 = [id for id, cells in cageid.items() if idx1 in cells][0]

        if id0!=id1:
            cageid[id0] = cageid[id0]+cageid[id1]
            cageid.pop(id1)

    for i,j in product(range(N),range(N)):

        ii,jj = cellidx[i,j]
        if is_valid(i-1, j):
            if len(lines[ii-1][jj:jj+twdth].replace(' ','')) != twdth:
                merge((i,j), (i-1,j))

        if is_valid(i+1, j):
            if len(lines[ii+1][jj:jj+twdth].replace(' ','')) != twdth:
                merge((i,j), (i+1,j))

        if is_valid(i, j-1):
            if lines[ii][jj-1] not in '|║':
                merge((i,j), (i,j-1))

        if is_valid(i, j+1):
            if lines[ii][jj+twdth] not in '|║':
                merge((i,j), (i,j+1))

    cages = []
    for id, cells in cageid.items():
        cells.sort()
        str_num = ""
        for (i,j) in cells:
            ii, jj = cellidx[i,j]
            str_num = str_num + lines[ii][jj:jj+cwdth]
        op = '+'    
        for i in '+-*/^':
            if i in str_num:
                op = i
                str_num = str_num.replace(op,' ')
        try:
            num = int(re.findall(r'\d+', str_num)[0])
        except IndexError:
            raise ValueError(id+' contains no value.')

        cages.append([(num,op), cells])

    return cages, N


def calcudoku(cages, N):
    with timeme('Setup time:'):
        solver = pywrapcp.Solver(__file__)
        cells = {}

        for i in range(N):
            for j in range(N):
                cells[i,j] = solver.IntVar(1,N,'x(%d,%d)'%(i,j))

        def is_int(txt):
            try: 
                int(txt)
                return True
            except:
                return False

        for i, ((num,op), block) in enumerate(cages):

            if op=='/' or op=='-':
                pycode = ("solver.Add((" + op.join("cells[%d,%d]"%(i,j) for i,j in block      )+" == %d)"%num + ' or '
                                     '(' + op.join("cells[%d,%d]"%(i,j) for i,j in block[::-1])+" == %d))"%num 
                         )
            else:
                pycode = ("solver.Add(" + op.join("cells[%d,%d]"%(i,j) for i,j in block)+
                                      " == %d)"%num)
            exec(pycode)

        #rows and cols
        for i in range(N):
            solver.Add(solver.AllDifferent([cells[i,j] for j in range(N)]))
            solver.Add(solver.AllDifferent([cells[j,i] for j in range(N)]))


        cells_flat = [cells[i] for i in cells]
        db= solver.Phase(
                cells_flat,
                solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
                solver.ASSIGN_CENTER_VALUE
            )
        solver.NewSearch(db)

    with timeme('Solver time:'):
        while solver.NextSolution():
            yield cells

if __name__ == "__main__":
    import sys
    if len(sys.argv)>=2:
        filename = sys.argv[1]
    else: 
        filename = 'gizmodo-10-hardest-puzzles/calcudoku-hardest.txt'
        
    for solution in calcudoku(*load_calcudoku(filename)):
        display_solution(solution)