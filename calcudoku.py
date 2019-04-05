import xlrd
import numpy as np
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
        
def load_calcudoku(filename):
    import xlrd
    
    #******************************************
    #A helper function to sort out and label clusters concerning the same sum
    def find_clusters(arr):
        outarr = np.zeros_like(arr)
        outidx = [];
        
        def find_neighbours(iin,jin):
            neighidx = [[iin-1,jin],[iin+1,jin],[iin,jin-1],[iin,jin+1]]
            neighidx = [[i,j] for i,j in neighidx if ( 0<=i and i<len(arr) and 0<=j and j<len(arr.T))]
            neighidx = [[i,j] for i,j in neighidx if (arr[iin,jin] == arr[i,j]) and outarr[i,j]==0]
            return neighidx
   
        def add_sector(iin, jin):
            current_labels = [[iin, jin]]
            lidx = 0;
            while(lidx < len(current_labels)):
                #remove if added twice
                if outarr[current_labels[lidx][0], current_labels[lidx][1]]:
                    current_labels.pop(lidx)
                    lidx-=1
                outarr[current_labels[lidx][0], current_labels[lidx][1]] = len(outidx)+1
                current_labels += find_neighbours(*current_labels[lidx])
                lidx+=1;
            outidx.append(current_labels)

        #Recursive helper
        for i in range(len(arr)):
            for j in range(len(arr.T)):
                if outarr[i,j] == 0:
                    add_sector(i, j)
                    
        return outidx, outarr
    
    #*******************************************
    #Load an .xls spreadsheet containing the sumsoduko information and return
    #a list of sumvalues corresponding to sudoku indices (0-based [row, col])
    def load_xls(filename):
        if not filename.lower().endswith('xls'):
            raise ValueError("load_sumsudoku uses file with the 90's Excel .xls "
            "extension not .txt, .csv, or .xlsx. You gave "+str(filename))
            
        colarray = np.zeros([9,9])
        valarray = [['']*9 for i in range(9)] 
        
        book = xlrd.open_workbook(filename, formatting_info=True)
        sheets = book.sheet_names()
        sheet = book.sheet_by_index(0)
        
        rows, cols = sheet.nrows, sheet.ncols
        for row in range(9):
            for col in range(9):
                thecell = sheet.cell(row, col)      
                xfx = sheet.cell_xf_index(row, col)
                xf = book.xf_list[xfx]
                
                try:   val = str(int(thecell.value))
                except:val = thecell.value.strip()
                
                colarray[row, col] = xf.background.pattern_colour_index
                valarray[row][col] = val
                    
        return colarray, valarray
    
    colarray, valarray = load_xls(filename)
    clusteridx, clusterarr = find_clusters(colarray)
    
    #Rearange clusteridx to [(sumvalue1, idxes1), (..,...)]
    for i, idxes in enumerate(clusteridx):
        sumval = '';
        for idx in idxes:
            if valarray[idx[0]][idx[1]] != '':
                sumval = valarray[idx[0]][idx[1]]
                break
        #if sumval == 0:
        #    raise ValueError('No sumvalue for cluster indexes in .xls sheet: '+str(idxes)+'.')
            
        clusteridx[i] = (sumval, idxes)
    
    return clusteridx



def calcudoku(cages):
    solver = pywrapcp.Solver('fill-a-pix')
    cells = {}

    pprint(cages)
    for i in range(9):
        for j in range(9):
            cells[i,j] = solver.IntVar(1,9,'x(%d,%d)'%(i,j))

    def is_int(txt):
        try: 
            int(txt)
            return True
        except:
            return False

    for i, (num, block) in enumerate(cages):
        num = num.replace('x','*')
        if is_int(num):
            num = num+'+'

        op = num[-1]
        num = int(num[:-1])

        if op=='/' or op=='-':
            pycode = ("solver.Add((" + op.join("cells[%d,%d]"%(i,j) for i,j in block      )+" == %d)"%num + ' or '
                                 '(' + op.join("cells[%d,%d]"%(i,j) for i,j in block[::-1])+" == %d))"%num 
                     )
        else:
            pycode = ("solver.Add(" + op.join("cells[%d,%d]"%(i,j) for i,j in block)+
                                  " == %d)"%num)
        print(pycode)
        exec(pycode)

    #rows and cols
    for i in range(9):
        solver.Add(solver.AllDifferent([cells[i,j] for j in range(9)]))
        solver.Add(solver.AllDifferent([cells[j,i] for j in range(9)]))

    #blocks not applicable for calcudoku
    #for i in range(0,9,3):
    #    for j in range(0,9,3):
    #        solver.Add(solver.AllDifferent([cells[i+ii,j+jj] 
    #                             for ii in range(3) for jj in range(3)]))

    cells_flat = [cells[i] for i in cells]
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield cells

import xlrd
import numpy as np
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
        
def load_calcudoku(filename):
    import xlrd
    
    #******************************************
    #A helper function to sort out and label clusters concerning the same sum
    def find_clusters(arr):
        outarr = np.zeros_like(arr)
        outidx = [];
        
        def find_neighbours(iin,jin):
            neighidx = [[iin-1,jin],[iin+1,jin],[iin,jin-1],[iin,jin+1]]
            neighidx = [[i,j] for i,j in neighidx if ( 0<=i and i<len(arr) and 0<=j and j<len(arr.T))]
            neighidx = [[i,j] for i,j in neighidx if (arr[iin,jin] == arr[i,j]) and outarr[i,j]==0]
            return neighidx
   
        def add_sector(iin, jin):
            current_labels = [[iin, jin]]
            lidx = 0;
            while(lidx < len(current_labels)):
                #remove if added twice
                if outarr[current_labels[lidx][0], current_labels[lidx][1]]:
                    current_labels.pop(lidx)
                    lidx-=1
                outarr[current_labels[lidx][0], current_labels[lidx][1]] = len(outidx)+1
                current_labels += find_neighbours(*current_labels[lidx])
                lidx+=1;
            outidx.append(current_labels)

        #Recursive helper
        for i in range(len(arr)):
            for j in range(len(arr.T)):
                if outarr[i,j] == 0:
                    add_sector(i, j)
                    
        return outidx, outarr
    
    #*******************************************
    #Load an .xls spreadsheet containing the sumsoduko information and return
    #a list of sumvalues corresponding to sudoku indices (0-based [row, col])
    def load_xls(filename):
        if not filename.lower().endswith('xls'):
            raise ValueError("load_sumsudoku uses file with the 90's Excel .xls "
            "extension not .txt, .csv, or .xlsx. You gave "+str(filename))
            
        colarray = np.zeros([9,9])
        valarray = [['']*9 for i in range(9)] 
        
        book = xlrd.open_workbook(filename, formatting_info=True)
        sheets = book.sheet_names()
        sheet = book.sheet_by_index(0)
        
        rows, cols = sheet.nrows, sheet.ncols
        for row in range(9):
            for col in range(9):
                thecell = sheet.cell(row, col)      
                xfx = sheet.cell_xf_index(row, col)
                xf = book.xf_list[xfx]
                
                try:   val = str(int(thecell.value))
                except:val = thecell.value.strip()
                
                colarray[row, col] = xf.background.pattern_colour_index
                valarray[row][col] = val
                    
        return colarray, valarray
    
    colarray, valarray = load_xls(filename)
    clusteridx, clusterarr = find_clusters(colarray)
    
    #Rearange clusteridx to [(sumvalue1, idxes1), (..,...)]
    for i, idxes in enumerate(clusteridx):
        sumval = '';
        for idx in idxes:
            if valarray[idx[0]][idx[1]] != '':
                sumval = valarray[idx[0]][idx[1]]
                break
        #if sumval == 0:
        #    raise ValueError('No sumvalue for cluster indexes in .xls sheet: '+str(idxes)+'.')
            
        clusteridx[i] = (sumval, idxes)
    
    return clusteridx



def calcudoku(cages):
    solver = pywrapcp.Solver('fill-a-pix')
    cells = {}

    for i in range(9):
        for j in range(9):
            cells[i,j] = solver.IntVar(1,9,'x(%d,%d)'%(i,j))

    def is_int(txt):
        try: 
            int(txt)
            return True
        except:
            return False

    for i, (num, block) in enumerate(cages):
        num = num.replace('x','*')
        if is_int(num):
            num = num+'+'

        op = num[-1]
        num = int(num[:-1])

        if op=='/' or op=='-':
            pycode = ("solver.Add((" + op.join("cells[%d,%d]"%(i,j) for i,j in block      )+" == %d)"%num + ' or '
                                 '(' + op.join("cells[%d,%d]"%(i,j) for i,j in block[::-1])+" == %d))"%num 
                     )
        else:
            pycode = ("solver.Add(" + op.join("cells[%d,%d]"%(i,j) for i,j in block)+
                                  " == %d)"%num)
        exec(pycode)

    #rows and cols
    for i in range(9):
        solver.Add(solver.AllDifferent([cells[i,j] for j in range(9)]))
        solver.Add(solver.AllDifferent([cells[j,i] for j in range(9)]))

    #blocks not applicable for calcudoku
    #for i in range(0,9,3):
    #    for j in range(0,9,3):
    #        solver.Add(solver.AllDifferent([cells[i+ii,j+jj] 
    #                             for ii in range(3) for jj in range(3)]))

    cells_flat = [cells[i] for i in cells]
    db= solver.Phase(
            cells_flat,
            solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
            solver.ASSIGN_CENTER_VALUE
        )
    solver.NewSearch(db)

    while solver.NextSolution():
        yield cells

if __name__ == "__main__":
    for solution in calcudoku(load_calcudoku('puzzles/calcudoku-hardest.xls')):
        display_solution(solution)