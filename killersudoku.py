import xlrd
from ortools.constraint_solver import pywrapcp
from pprint import pprint
import re

def display_solution(cells):
    rows, cols = 0,0
    for (i,j), val in cells.items():
        if i+1 >= rows: rows = i+1
        if i+1 >= cols: cols = j+1

    for i in range(rows):
        for j in range(cols):
            print(cells[i,j].Value(),end=' ')
            if (j+1)%3==0 and (j+1)!=9:
                print('|', end=' ')
        if (i+1)%3==0 and (i+1)!=9:
            print('\n------+-------+------')
            
        else:
            print()
    
def load_killersudoku(filename):
    from itertools import product
    str_in = open(filename).read()
    lines = [i.split('#')[0].strip() for i in str_in.split('\n')]
    lines = [i for i in lines if i]

    lwdth = len(lines[0])
    for i in lines:
        if len(i)!=lwdth:
            raise ValueError('Lines in killersudoku puzzle is not the same length:\n'+'\n'.join(lines))
    
    #print('\n'.join(lines))
    cellidx = {}
    for i in range(9):
        for j in range(9):
            cellidx[i,j] = (i*2+1,j*4+1)

    for i in range(9):
        for j in range(9):
            ii,jj = cellidx[i,j]

    cageid  = {'cage'+str((i,j)):[(i,j)] for i in range(9) for j in range(9)}

    def is_valid(i,j):
        if i<0 or j<0 or i>=9 or j>=9:
            return False
        return True

    def merge(idx0, idx1):
        id0 = [id for id, cells in cageid.items() if idx0 in cells][0]
        id1 = [id for id, cells in cageid.items() if idx1 in cells][0]

        if id0!=id1:
            cageid[id0] = cageid[id0]+cageid[id1]
            cageid.pop(id1)


    for i,j in product(range(9),range(9)):

        ii,jj = cellidx[i,j]
        if is_valid(i-1, j):
            if len(lines[ii-1][jj:jj+3].replace(' ','')) != 3:
                merge((i,j), (i-1,j))

        if is_valid(i+1, j):
            if len(lines[ii+1][jj:jj+3].replace(' ','')) != 3:
                merge((i,j), (i+1,j))

        if is_valid(i, j-1):
            if lines[ii][jj-1] not in '|║':
                merge((i,j), (i,j-1))

        if is_valid(i, j+1):
            if lines[ii][jj+3] not in '|║':
                merge((i,j), (i,j+1))

    cages = []
    for i, cells in cageid.items():
        cells.sort()
        str_num = ""
        for (i,j) in cells:
            ii, jj = cellidx[i,j]
            str_num = str_num + lines[ii][jj:jj+4]

        num = int(re.findall(r'\d+', str_num)[0])
        cages.append([num, cells])

    return cages


def killersudoku(cages):
    solver = pywrapcp.Solver(__file__)
    cells = {}

    for i in range(9):
        for j in range(9):
            cells[i,j] = solver.IntVar(1,9,'x(%d,%d)'%(i,j))

    for i, (num, block) in enumerate(cages):
        
        #solver.Sum not working
        pycode = ("solver.Add(" + " + ".join("cells[%d,%d]"%(i,j) for i,j in block)+
                              " == %d)"%num)
        exec(pycode)

    #rows and cols
    for i in range(9):
        solver.Add(solver.AllDifferent([cells[i,j] for j in range(9)]))
        solver.Add(solver.AllDifferent([cells[j,i] for j in range(9)]))

    #blocks
    for i in range(0,9,3):
        for j in range(0,9,3):
            solver.Add(solver.AllDifferent([cells[i+ii,j+jj] 
                                 for ii in range(3) for jj in range(3)]))

    cells_flat = [cells[i] for i in cells]
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield(cells)
        
if __name__ == "__main__":
    import sys
    if len(sys.argv)>=2:
        filename = sys.argv[1]
    else: 
        filename = 'gizmodo-10-hardest-puzzles/killersudoku-hardest.txt'
        
    for solution in killersudoku(load_killersudoku(filename)):
        display_solution(solution)