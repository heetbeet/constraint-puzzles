from ortools.constraint_solver import pywrapcp
from itertools import product

def display_solution(cells):
    for line in cells:
        for cell in line:
            print('⬛' if cell.Value()==1 else '⬜', end='')
        print()

def n_queens(N=8):
    solver = pywrapcp.Solver(str(N)+'-queens')
    cells = []
    for i in range(N):
        cells.append([])
        for j in range(N):
            cells[-1].append(solver.IntVar(0,1,'x(%d,%d)'%(i,j)))
            
    for i in range(N):
        exec("solver.Add(" + " + ".join("cells[i][%d]"%j for j in range(N)) + " == 1) ")
        exec("solver.Add(" + " + ".join("cells[%d][i]"%j for j in range(N)) + " == 1) ")

    #slopes upwards-right
    idx = {(i,j) for i,j in product(range(N),range(N))}
    for i in range(1,N*2-2):
        slope = []
        for j in range(N):
            if (i-j,j) in idx: slope.append((i-j,j))
        exec("solver.Add(" + " + ".join("cells[%d][%d]"%(i,j) for (i,j) in slope) + " <= 1) ")

    #slopes downwards-right
    for i in range(-N+2,N-1):
        slope = []
        for j in range(N):
            if (i+j,j) in idx: slope.append((i+j,j))
        exec("solver.Add(" + " + ".join("cells[%d][%d]"%(i,j) for (i,j) in slope) + " <= 1) ")


    cells_flat = []
    for i in range(N):
        for j in range(N):
            cells_flat.append(cells[i][j])
            
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield cells


if __name__ == "__main__":
    for solution in n_queens(8):
        display_solution(solution)
        print()