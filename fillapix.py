from ortools.constraint_solver import pywrapcp
from itertools import product

def display_solution(cells):
    for line in cells:
        for cell in line:
            print('⬛' if cell.Value()==1 else '⬜', end='')
        print()


def get_clues(txt):
    def whitelist(line):
        if set(i for i in line).difference(
            set(i for i in '.0123456789')):
            return False
        return True
        
    lines = [i for i in txt.split('\n') if whitelist(i)]
    clues = []
    for line in lines:
        clues.append([])
        for i in line:
            clues[-1].append(None if i=='.' else int(i))
    return clues
        
def fillapix(clues)
    solver = pywrapcp.Solver('fill-a-pix')
    cells = []

    rows, cols = len(clues), len(clues[0])
    for i in range(rows):
        cells.append([])
        for j in range(cols):
            cells[-1].append(solver.IntVar(0,1,'x(%d,%d)'%(i,j)))

    def valid(i,j):
        if i<0 or j<0 or i>=rows or j>=cols:
            return False
        return True

    for i in range(rows):
        for j in range(cols):
            block = [(i+ii,j+jj)
                    for ii in range(-1,2) for jj in range(-1,2)
                    if valid(i+ii,j+jj)]

            if clues[i][j] is not None:
                #solver.Sum not working
                #solver.Add(solver.Sum(cells[i][j] for i,j in block) == clue[i][j])
                pycode = ("solver.Add(" + " + ".join("cells[%d][%d]"%(i,j) for i,j in block) + " == %d) "%clues[i][j])
                exec(pycode)


    cells_flat = []
    for i in range(rows):
        for j in range(cols):
            cells_flat.append(cells[i][j])

    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield(cells)