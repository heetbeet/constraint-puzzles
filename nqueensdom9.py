from ortools.constraint_solver import pywrapcp

def display_solution(queens):
    queen_columns = [int(queen.Value()) for queen in queens]
    for i in queen_columns:
        print(''.join(['⬛' if i==j else '⬜' for j in range(len(queens))]))

def n_queens(N=8):
    solver = pywrapcp.Solver(str(N)+'-queens')
    queens = [solver.IntVar(0,N-1,'x%d'%i) for i in range(N)]

    solver.Add(solver.AllDifferent(queens))
    solver.Add(solver.AllDifferent([queens[i]+i for i in range(N)]))
    solver.Add(solver.AllDifferent([queens[i]-i for i in range(N)]))

    db= solver.Phase(
        queens,
        solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
        solver.ASSIGN_CENTER_VALUE
    )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield queens
        
        

if __name__ == "__main__":
    for solution in n_queens(8):
        display_solution(solution)
        print()