from ortools.constraint_solver import pywrapcp
from itertools import product


def display_solution(cells_dict):
    rows, cols = 0,0
    for (i,j), val in cells_dict.items():
        if i+1 >= rows: rows = i+1
        if i+1 >= cols: cols = j+1
    
    
    for i in range(rows):
        for j in range(cols):
            if (i,j) not in cells_dict:
                print('🔲', end='')
            else:
                print('⬛' if cells_dict[i,j].Value()==1 else '⬜', end='')
        print(flush=True)

def get_clues(txt):
       
    lines = [i.split('#')[0].strip() for i in txt.split('\n')]
    clues = []
    for line in lines:
        if line == '': continue
        clues.append([])
        for i in line:
            clues[-1].append(None if i=='.' else int(i))
    return clues
        
def fillapix(clues):
    solver = pywrapcp.Solver('fill-a-pix')
    cells = {}

    rows, cols = len(clues), len(clues[0])
    for i in range(rows):
        for j in range(cols):
            cells[i,j] = solver.IntVar(0,1,'x(%d,%d)'%(i,j))

    def valid(i,j):
        if i<0 or j<0 or i>=rows or j>=cols:
            return False
        return True

    ij_scope = set()
    for i in range(rows):
        for j in range(cols):
            block = [(i+ii,j+jj)
                    for ii in range(-1,2) for jj in range(-1,2)
                    if valid(i+ii,j+jj)]
            
            ij_scope.update(block)
            if clues[i][j] is not None:
                #solver.Sum not working
                #solver.Add(solver.Sum(cells[i][j] for i,j in block) == clue[i][j])
                pycode = ("solver.Add(" + " + ".join("cells[%d,%d]"%(i,j) for i,j in block) + " == %d) "%clues[i][j])
                exec(pycode)

    for i in range(rows):
        for j in range(cols):
            if (i,j) not in ij_scope:
                cells.pop((i,j))

    db= solver.Phase(
            [cell for _, cell in cells.items()],
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