import xlrd
from ortools.constraint_solver import pywrapcp
from pprint import pprint

def display_solution(cells):
    rows, cols = 0,0
    for (i,j), val in cells.items():
        if i+1 >= rows: rows = i+1
        if j+1 >= cols: cols = j+1
        
    for i in range(rows):
        for j in range(cols):
            if (i,j) in cells:
                print(cells[i,j].Value(), end=" ")
            else:
                print(".", end=' ')
        print()

def load_kakuro(filename):
    str_in = open(filename).read()
    
    lines = [i.split('#')[0].strip() for i in str_in.split('\n')]
    cells = [[j.strip().replace('_','') for j in i.split('|')] 
                                        for i in lines if '|' in i]
    
    cols = len(cells[0])
    rows = len(cells)
    
    cages = []
    for i, line in enumerate(cells):
        for j, ijtxt in enumerate(line):
            if '\\' in ijtxt:
                dwn = ijtxt.split('\\')[0].strip()
                rgt = ijtxt.split('\\')[1].strip()

                if dwn != '':
                    cages.append([int(dwn),[]])
                    for ii in range(i+1,len(cells)):
                        if cells[ii][j].strip()=='':
                            cages[-1][-1].append((ii,j))
                        else: break

                if rgt != '':
                    cages.append([int(rgt),[]])
                    for jj in range(j+1,len(line)):
                        if cells[i][jj].strip()=='':
                            cages[-1][-1].append((i,jj))
                        else: break
    return cages

def kakuro(cages):
    solver = pywrapcp.Solver(__file__)
    cells = {}

    for i, (num, block) in enumerate(cages):
        for i,j in block:
            cells[i,j] = solver.IntVar(1,9,'x(%d,%d)'%(i,j))

    for i, (num, block) in enumerate(cages):
        
        #solver.Sum not working
        #solver.Add([solver.Sum(cells[i,j] for i,j in block]) == num)
        pycode = ("solver.Add(" + " + ".join("cells[%d,%d]"%(i,j) for i,j in block) + " == %d) "%num)
        exec(pycode)
        
        solver.Add(solver.AllDifferent([cells[i,j] for i,j in block]))


    cells_flat = [cells[i] for i in cells]
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield(cells)