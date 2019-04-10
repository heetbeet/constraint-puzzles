from ortools.constraint_solver import pywrapcp
from itertools import product

def display_solution(cells):
    for line in cells:
        for cell in line:
            print('⬛' if cell.Value()==1 else '⬜', end='')
        print(flush=True)


def get_clues(txt):
       
    lines = [i.split('#')[0].strip() for i in txt.split('\n')]
    clues = []
    for line in lines:
        if line == '': continue
        print(line)
        clues.append([])
        for i in line:
            clues[-1].append(None if i=='.' else int(i))
    return clues
        
def fillapix(clues):
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
        
if __name__ == "__main__":
    import sys
    if len(sys.argv)>=2:
        filename = sys.argv[1]
    else: 
        filename = 'gizmodo-10-hardest-puzzles/fillapix-hardest.txt'
    
    for i in fillapix(get_clues(open(filename).read())):
        display_solution(i)