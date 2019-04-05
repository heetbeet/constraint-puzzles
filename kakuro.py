import xlrd
from ortools.constraint_solver import pywrapcp
from pprint import pprint

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

def load_kakuro(filename):
    book = xlrd.open_workbook(filename, formatting_info=True)
    sheets = book.sheet_names()
    sheet = book.sheet_by_index(0)

    rows, cols = sheet.nrows, sheet.ncols

    print(rows, cols)
    
    kaku_rc = []
    for i in range(rows):
        kaku_rc.append([])
        for j in range(cols):
            kaku_rc[-1].append(str(sheet.cell(i,j).value).strip())
    l = 0
    for line in kaku_rc:
        for i, val in enumerate(line):
            if val and str(val).strip()!="":
                if i+1>=l:
                    l=i+1
    kaku_rc = [line[:l] for line in kaku_rc if sum([i!='' for i in line])]
    pprint(kaku_rc)

    cages = []

    for i, line in enumerate(kaku_rc):
        for j, ijtxt in enumerate(line):
            if '\\' in ijtxt:
                dwn = ijtxt.split('\\')[0].strip()
                rgt = ijtxt.split('\\')[1].strip()

                if dwn != '':
                    cages.append([int(dwn),[]])
                    for ii in range(i+1,len(kaku_rc)):
                        if kaku_rc[ii][j].strip()=='':
                            cages[-1][-1].append((ii,j))
                        else: break

                if rgt != '':
                    cages.append([int(rgt),[]])
                    for jj in range(j+1,len(line)):
                        if kaku_rc[i][jj].strip()=='':
                            cages[-1][-1].append((i,jj))
                        else: break
    return cages

def kakuro(cages):
    solver = pywrapcp.Solver('fill-a-pix')
    cells = {}

    for i, (num, block) in enumerate(cages):
        for i,j in block:
            cells[i,j] = solver.IntVar(1,9,'x(%d,%d)'%(i,j))

    for i, (num, block) in enumerate(cages):
        
        #solver.Sum not working
        #solver.Add([solver.Sum(cells[i,j] for i,j in block]) == num)
        pycode = ("solver.Add(" + " + ".join("cells[%d,%d]"%(i,j) for i,j in block) + " == %d) "%num)
        print(pycode, flush=1)
        exec(pycode)


    cells_flat = [cells[i] for i in cells]
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield(cells)