from board import Direction, Rotation
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        return self.random.choice([
            Direction.Left,
            Direction.Right,
            Direction.Down,
            Rotation.Anticlockwise,
            Rotation.Clockwise,
        ])


# from Mark
class version1_Mark(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        bestscore = 0
        bestmove = None
        for xtarget in range(10):
            score, move = self.try_move(board, xtarget)
            if score > bestscore:
                bestscore = score
                bestmove = move
        return bestmove
            

    def try_move(self, board, xtarget):
        clone = board.clone()
        firstmove = None
        while True:
            if clone.falling.left < xtarget:
                trymove = Direction.Right
            elif clone.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            if firstmove is None:
                firstmove = trymove
            res = clone.move(trymove)
            if res:
                score = self.score_board(clone)
                return score, firstmove
                
    
    def score_board(self, clone):

        min_y = min([y for x,y in clone.cells])
        print(min_y)
        return min_y
        
        """
        miny = 23
        for x,y in clone.cells:
            print(x,y)
            if y < miny:
                miny = y
        return miny
        """

# Base on Pierre Dellacherie Algorithom
class Adam_1(Player):

    def __init__(self, seed=None):
        self.random = Random(seed)
        self.best_rotation = 0

    def choose_action(self, board):
        bestscore = -999999
        move = None
        bestmove = None
        rotation = None
        clone_board = None
        #print(board.cells)
        #debug
        
        #print(self.getBoardBuriedHoles(board))
        # 4 rotation x 10 blocks
        # test possible movements (to see if block lands)
        #print(board.falling)

        

        for i in range(4):
            res = False
            count = 0
            clone_board = board.clone()
            if clone_board.falling == False:
                break
            if i == 1:
                rotation = Rotation.Clockwise
                res = clone_board.rotate(rotation)
                count += 1

            elif i == 2:
                tmp_board = clone_board.clone()
                rotation = Rotation.Clockwise
                res = tmp_board.rotate(rotation)
                count += 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    count += 1
                    clone_board = tmp_board

                #try rotation from other direction
                else:
                    tmp_board = clone_board.clone()
                    rotation = Rotation.Anticlockwise
                    res = tmp_board.rotate(rotation)
                    count -= 1
                    if not res:
                        res = tmp_board.rotate(rotation)
                        clone_board = tmp_board
                        count -= 1
                        
            elif i == 3:
                rotation = Rotation.Anticlockwise
                res = clone_board.rotate(rotation)               
                count -= 1

            else:
                count = 0
            
            if not res:
                for xtarget in range(10):
                    #print(clone_board.cells)
                    score, move = self.try_move(clone_board, xtarget)
                    #move = self.try_move(clone_board, xtarget)
                    #print(score)
                    
                    if score > bestscore:
                        self.best_rotation = count
                        #print(count)
                        bestscore = score
                        bestmove = move
            else:
                score = self.score_board(clone_board)

            if score > bestscore:
                self.best_rotation = count
                #print(count)
                bestscore = score
                bestmove = move

        if self.best_rotation != 0:
            if self.best_rotation > 0:
                bestmove = Rotation.Clockwise
            else:
                bestmove = Rotation.Anticlockwise
            #self.rotation_left -= 1

        return bestmove


    def try_move(self, board, xtarget):
        clone_board = board.clone()
        firstmove = None
        while True:
            if clone_board.falling.left < xtarget:
                trymove = Direction.Right
            elif clone_board.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            if firstmove is None:
                firstmove = trymove
            res = clone_board.move(trymove)
            
            if res:
                score = self.score_board(clone_board)
                return score, firstmove
                #return firstmove

    def boardRowTransitions(self, cells, min_y):
        transition = 0
        for i in range(10):
            #start from 1 element befor top y coordinate, reduce loop num
            for j in range(min_y-1, 23):
                if ((i, j) not in cells) and ((i,j+1) in cells):
                    transition += 1  
                if ((i, j) in cells) and ((i,j+1) not in cells):
                    transition += 1  
        
        return transition
                
    def boardcolTransitions(self, cells):
        transition = 0
        for i in range(9):
            for j in range(24):
                if ((i, j) not in cells) and ((i+1,j) in cells):
                    transition += 1  
                elif ((i, j) in cells) and ((i+1,j) not in cells):
                    transition += 1  

        return transition
    
    def get_erodedPieceCellsMetric(self, board, cells):
        row_eliminated = 0
        usefulblock = 0
        falling_cells = board.falling.cells
        for j in range(24):
            count = 0
            for i in range(10):
                if (i, j) in cells:
                    count += 1
            if count == 10:
                row_eliminated += 1
                #print(row_eliminated)
                for k in range(10):
                    if (k, j) in falling_cells:
                        usefulblock += 1
        #print(usefulblock)
        return row_eliminated * usefulblock

    def getBoardBuriedHoles(self, cells, min_y):
        holes = 0
        for i in range(10):
            colhole = None
            for j in range(min_y, 24):
                if (colhole == None) and ((i,j) in cells):
                    colhole = 0
                if (colhole != None) and ((i,j) not in cells):
                    colhole += 1
            if colhole != None:
                holes += colhole
                
        return holes        


    def getBoardWells(self, cells, min_y):
        #save as list (sequence addition)
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        holes = 0
        sum = 0
        for i in range(10):
            #loop from min_y to 24, reduce some loop
            for j in range(min_y, 24):
                if (i ,j) not in cells:
                    if ((i+1, j)  in cells) and (i-1, j) in cells:
                        holes += 1
                    elif ( i-1 < 0 and (i+1, j) in cells):
                        holes += 1
                    elif ( i+1 > 9 and (i-1,j) in cells):
                        holes += 1
                else:
                    sum += sum_n[holes]
                    holes = 0
        return sum

    def score_board(self, clone):

        #get maximun landing y coordinate
        cells = clone.cells
        #if cells != False:
        #check if list is empty
        if cells:
            min_y = min([y for x,y in cells])
        else:
            min_y = 23
        #checked
        transition_row = self.boardRowTransitions(cells, min_y)
        transition_col = self.boardcolTransitions(cells)
        #not yet (checked)
        erodedPieceCellsMetric = self.get_erodedPieceCellsMetric(clone, cells)
        #checked
        hole_num = self.getBoardBuriedHoles(cells, min_y)
        #checked
        boardwells = self.getBoardWells(cells, min_y)
        #print(hole_num)
        #print(clone.cells)
        #weithting
        
        
        score = -45 * (23-min_y) - 32 * transition_row - 93 * transition_col + \
            34 * erodedPieceCellsMetric - 79 * hole_num - 34 * boardwells
        
        #score = (-4.500158825082766) * (23-min_y) + (-3.2178882868487753) * transition_row + (-9.348695305445199) * transition_col\
        # + (-7.899265427351652) * hole_num + (3.4181268101392694) * erodedPieceCellsMetric + (-3.3855972247263626) * boardwells
        
        #print(score)
        return score


# version 2 - add more moving possibilities(rotation first, moving first)
class Adam_2(Player):

    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        #print(board.cells)
        #debug
        
        #print(self.getBoardBuriedHoles(board))
        # 4 rotation x 10 blocks
        # test possible movements (to see if block lands)
        #print(board.falling)

        
        best_rotation_rot_mov, score_rot_mov, bestmove_rot_mov = self.rotation_first(board)
        #movement first 
        best_rotation_mov_rot, score_mov_rot, bestmove_mov_rot, move_count = self.movement_first(board)
        
        """
        if score_rot_mov > score_mov_rot:
            if best_rotation_rot_mov != 0:
                if best_rotation_rot_mov > 0:
                    bestmove = Rotation.Clockwise
                else:
                    bestmove = Rotation.Anticlockwise
            else:
                bestmove = bestmove_rot_mov
            return bestmove
        #print(best_rotation_mov_rot)
        #print(move_count)
        else:
            hor_move = []
            if move_count > 0:
                for i in range (move_count):
                    hor_move.append(Direction.Right)
            elif move_count < 0:
                for i in range (-move_count):
                    hor_move.append(Direction.Left)
            else:

                if best_rotation_mov_rot != 0:
                    if best_rotation_mov_rot > 0:
                        bestmove = Rotation.Clockwise
                    else:
                        bestmove = Rotation.Anticlockwise
                else:
                    bestmove = Direction.Drop
            if hor_move:
                return hor_move           
            return bestmove
        """    
        hor_move = []
        if move_count > 0:
            for i in range (move_count):
                hor_move.append(Direction.Right)
        elif move_count < 0:
            for i in range (-move_count):
                hor_move.append(Direction.Left)
        else:

            if best_rotation_mov_rot != 0:
                if best_rotation_mov_rot > 0:
                    bestmove = Rotation.Clockwise
                else:
                    bestmove = Rotation.Anticlockwise
            else:
                bestmove = Direction.Drop
        if hor_move:
            return hor_move           
        return bestmove


    def rotation_first(self, board):
        bestscore = -999999
        move = None
        bestmove = None
        rotation = None
        clone_board = None
        best_rotation = 0

        res = False

        for i in range(4):
            count = 0
            clone_board = board.clone()
            if i == 1:
                rotation = Rotation.Clockwise
                res = clone_board.rotate(rotation)
                count += 1

            elif i == 2:
                tmp_board = clone_board.clone()
                rotation = Rotation.Clockwise
                res = tmp_board.rotate(rotation)
                count += 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    count += 1
                    clone_board = tmp_board

                #try rotation from other direction
                else:
                    tmp_board = clone_board.clone()
                    rotation = Rotation.Anticlockwise
                    res = tmp_board.rotate(rotation)
                    count -= 1
                    if not res:
                        res = tmp_board.rotate(rotation)
                        clone_board = tmp_board
                        count -= 1
                        
            elif i == 3:
                rotation = Rotation.Anticlockwise
                res = clone_board.rotate(rotation)               
                count -= 1

            else:
                count = 0
            
            if not res:
                for xtarget in range(10):
                    #print(clone_board.cells)
                    score, move = self.try_move(clone_board, xtarget)
                    #move = self.try_move(clone_board, xtarget)
                    #print(score)
                    
                    if score > bestscore:
                        best_rotation = count
                        #print(count)
                        bestscore = score
                        bestmove = move
            else:
                score = self.score_board(clone_board)

            if score > bestscore:
                best_rotation = count
                #print(count)
                bestscore = score
                bestmove = move

        return best_rotation, bestscore, bestmove

    def movement_first(self, board):
        best_rotation = 0
        bestscore = -999999
        bestmove = None
        clone_board = None
        count = 0
        bestmov_count = 0

        for xtarget in range(10):
            #a counter for horizontal movements
           
            clone_board = board.clone()
            firstmove = None
            res = False
            move_count = 0

            while True:
                
                block_left = clone_board.falling.left
                if block_left < xtarget:
                    trymove = Direction.Right
                    res = clone_board.move(trymove)
                    move_count += 1
                elif block_left > xtarget:
                    trymove = Direction.Left
                    res = clone_board.move(trymove)
                    move_count -= 1
                elif block_left == xtarget:
                    trymove = Direction.Drop
                    #move_count = 0
                if firstmove is None:
                    firstmove = trymove
                # from here, start try rotation
                if res or (block_left == xtarget):
                    break

            if not res:
                for i in range(4):
                    clone_board_for_rot = clone_board.clone()
                    count, score, clone_board_for_rot = self.try_rotation(clone_board_for_rot, i)
                    if score == None:
                        #clone_board_for_rot = clone_board_for_rot.clone()
                        res = clone_board_for_rot.move(trymove)
                        score = self.score_board(clone_board_for_rot)

                    if score > bestscore:
                        best_rotation = count
                        #print(count)
                        bestmove = firstmove
                        bestscore = score
                        bestmov_count = move_count
            else:
                score = score = self.score_board(clone_board)

            if score > bestscore:
                best_rotation = count
                #print(count)
                bestscore = score
                bestmove = firstmove   
                bestmov_count = move_count   

        return best_rotation, bestscore, bestmove, bestmov_count


    def try_rotation(self, board, i):
        count = 0
        res = False
        clone_board = board.clone()
        #a flag to see if rotation caused block landed
        score = None
        #firstrotation = None
        if i == 1:
            rotation = Rotation.Clockwise
            res = clone_board.rotate(rotation)
            count += 1

        elif i == 2:
            tmp_board = clone_board.clone()
            rotation = Rotation.Clockwise
            res = tmp_board.rotate(rotation)
            count += 1
            if not res:
                res = tmp_board.rotate(rotation)
                count += 1
                clone_board = tmp_board

            #try rotation from other direction
            else:
                tmp_board = clone_board.clone()
                rotation = Rotation.Anticlockwise
                res = tmp_board.rotate(rotation)
                count -= 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    clone_board = tmp_board
                    count -= 1
                    
        elif i == 3:
            rotation = Rotation.Anticlockwise
            res = clone_board.rotate(rotation)               
            count -= 1

        else:
            count = 0

        if res:
            score = self.score_board(clone_board)


        return count, score, clone_board


    def try_move(self, board, xtarget):
        clone_board = board.clone()
        firstmove = None
        while True:
            if clone_board.falling.left < xtarget:
                trymove = Direction.Right
            elif clone_board.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            if firstmove is None:
                firstmove = trymove
            res = clone_board.move(trymove)
            
            if res:
                score = self.score_board(clone_board)
                return score, firstmove
                #return firstmove

    def boardRowTransitions(self, cells, min_y):
        transition = 0
        for i in range(10):
            #start from 1 element befor top y coordinate, reduce loop num
            for j in range(min_y-1, 23):
                if ((i, j) not in cells) and ((i,j+1) in cells):
                    transition += 1  
                if ((i, j) in cells) and ((i,j+1) not in cells):
                    transition += 1  
        
        return transition
                
    def boardcolTransitions(self, cells):
        transition = 0
        for i in range(9):
            for j in range(24):
                if ((i, j) not in cells) and ((i+1,j) in cells):
                    transition += 1  
                elif ((i, j) in cells) and ((i+1,j) not in cells):
                    transition += 1  

        return transition
    
    def get_erodedPieceCellsMetric(self, board, cells):
        row_eliminated = 0
        usefulblock = 0
        falling_cells = board.falling.cells
        for j in range(24):
            count = 0
            for i in range(10):
                if (i, j) in cells:
                    count += 1
            if count == 10:
                row_eliminated += 1
                #print(row_eliminated)
                for k in range(10):
                    if (k, j) in falling_cells:
                        usefulblock += 1
        #print(usefulblock)
        return row_eliminated * usefulblock

    def getBoardBuriedHoles(self, cells, min_y):
        holes = 0
        for i in range(10):
            colhole = None
            for j in range(min_y, 24):
                if (colhole == None) and ((i,j) in cells):
                    colhole = 0
                if (colhole != None) and ((i,j) not in cells):
                    colhole += 1
            if colhole != None:
                holes += colhole
                
        return holes        


    def getBoardWells(self, cells, min_y):
        #save as list (sequence addition)
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        holes = 0
        sum = 0
        for i in range(10):
            #loop from min_y to 24, reduce some loop
            for j in range(min_y, 24):
                if (i ,j) not in cells:
                    if ((i+1, j)  in cells) and (i-1, j) in cells:
                        holes += 1
                    elif ( i-1 < 0 and (i+1, j) in cells):
                        holes += 1
                    elif ( i+1 > 9 and (i-1,j) in cells):
                        holes += 1
                else:
                    sum += sum_n[holes]
                    holes = 0
        return sum

    def score_board(self, clone):

        #get maximun landing y coordinate
        cells = clone.cells
        #if cells != False:
        #check if list is empty
        if cells:
            min_y = min([y for x,y in cells])
        else:
            min_y = 23
        #checked
        transition_row = self.boardRowTransitions(cells, min_y)
        transition_col = self.boardcolTransitions(cells)
        #not yet (checked)
        erodedPieceCellsMetric = self.get_erodedPieceCellsMetric(clone, cells)
        #checked
        hole_num = self.getBoardBuriedHoles(cells, min_y)
        #checked
        boardwells = self.getBoardWells(cells, min_y)
        #print(hole_num)
        #print(clone.cells)
        #weithting
        
        
        score = -45 * (23-min_y) - 32 * transition_row - 93 * transition_col + \
            34 * erodedPieceCellsMetric - 79 * hole_num - 34 * boardwells
        
        #score = (-4.500158825082766) * (23-min_y) + (-3.2178882868487753) * transition_row + (-9.348695305445199) * transition_col\
        # + (-7.899265427351652) * hole_num + (3.4181268101392694) * erodedPieceCellsMetric + (-3.3855972247263626) * boardwells
        
        #print(score)
        return score
        
        

# Rotation -> Movement + PD, 
class Adam_3(Player):

    def __init__(self, seed=None):
        self.random = Random(seed)
        self.best_rotation = 0

    def choose_action(self, board):

        action = self.rotation_first(board)
        #print(action)
        return action



    def rotation_first(self, board):
        bestscore = -999999
        #move = None
        #bestmove = None
        rotation = None
        clone_board = None
        #best_rotation = 0
        bestaction = []
        #list


        res = False

        for i in range(4):
            action = []
            move_action = []
            #count = 0
            clone_board = board.clone()
            if i == 1:
                rotation = Rotation.Clockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1

            elif i == 2:
                tmp_board = clone_board.clone()
                rotation = Rotation.Clockwise
                res = tmp_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Clockwise)
                    #count += 1
                    

                #try rotation from other direction
                else:
                    tmp_board = clone_board.clone()
                    action = []
                    rotation = Rotation.Anticlockwise
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Anticlockwise)
                    #count -= 1
                    if not res:
                        res = tmp_board.rotate(rotation)
                        action.append(Rotation.Anticlockwise)
                        #count -= 1
                    #clone_board = tmp_board
                    
                clone_board = tmp_board
                    
            elif i == 3:
                rotation = Rotation.Anticlockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Anticlockwise)               
                #count -= 1

            """
            else:
                #count = 0
                pass
            """
            
            if not res:
                for xtarget in range(10):
                    #print(clone_board.cells)
                    score, move_action = self.try_move(clone_board, xtarget)
                    #move = self.try_move(clone_board, xtarget)
                    #print(score)
                    
                    if score > bestscore:
                        #best_rotation = count
                        #print(count)
                        bestaction = action + move_action
                        bestscore = score
                        #bestmove = move
            else:
                score = self.score_board(clone_board)

            if score > bestscore:
                #best_rotation = count
                #print(count)
                bestscore = score
                #bestmove = move
                bestaction = action + move_action

        return bestaction

    def try_move(self, board, xtarget):
        clone_board = board.clone()
        move_action = []
        while True:
            if clone_board.falling.left < xtarget:
                trymove = Direction.Right
            elif clone_board.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            #if firstmove is None:
            #    firstmove = trymove
            res = clone_board.move(trymove)
            move_action.append(trymove)
            if res:
                score = self.score_board(clone_board)
                return score, move_action
                #return firstmove

    def boardRowTransitions(self, cells, min_y):
        transition = 0
        for i in range(10):
            #start from 1 element befor top y coordinate, reduce loop num
            for j in range(min_y-1, 23):
                if ((i, j) not in cells) and ((i,j+1) in cells):
                    transition += 1  
                if ((i, j) in cells) and ((i,j+1) not in cells):
                    transition += 1  
        
        return transition
                
    def boardcolTransitions(self, cells):
        transition = 0
        for i in range(9):
            for j in range(24):
                if ((i, j) not in cells) and ((i+1,j) in cells):
                    transition += 1  
                elif ((i, j) in cells) and ((i+1,j) not in cells):
                    transition += 1  

        return transition
    
    def get_erodedPieceCellsMetric(self, board, cells):
        row_eliminated = 0
        usefulblock = 0
        falling_cells = board.falling.cells
        for j in range(24):
            count = 0
            for i in range(10):
                if (i, j) in cells:
                    count += 1
            if count == 10:
                row_eliminated += 1
                #print(row_eliminated)
                for k in range(10):
                    if (k, j) in falling_cells:
                        usefulblock += 1
        #print(usefulblock)
        return row_eliminated * usefulblock

    def getBoardBuriedHoles(self, cells, min_y):
        holes = 0
        for i in range(10):
            colhole = None
            for j in range(min_y, 24):
                if (colhole == None) and ((i,j) in cells):
                    colhole = 0
                if (colhole != None) and ((i,j) not in cells):
                    colhole += 1
            if colhole != None:
                holes += colhole
                
        return holes        


    def getBoardWells(self, cells, min_y):
        #save as list (sequence addition)
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        holes = 0
        sum = 0
        for i in range(10):
            #loop from min_y to 24, reduce some loop
            for j in range(min_y, 24):
                if (i ,j) not in cells:
                    if ((i+1, j)  in cells) and (i-1, j) in cells:
                        holes += 1
                    elif ( i-1 < 0 and (i+1, j) in cells):
                        holes += 1
                    elif ( i+1 > 9 and (i-1,j) in cells):
                        holes += 1
                else:
                    sum += sum_n[holes]
                    holes = 0
        return sum

    def score_board(self, clone):

        #get maximun landing y coordinate
        cells = clone.cells
        #if cells != False:
        #check if list is empty
        if cells:
            min_y = min([y for x,y in cells])
        else:
            min_y = 23
        #checked
        transition_row = self.boardRowTransitions(cells, min_y)
        transition_col = self.boardcolTransitions(cells)
        #not yet (checked)
        erodedPieceCellsMetric = self.get_erodedPieceCellsMetric(clone, cells)
        #checked
        hole_num = self.getBoardBuriedHoles(cells, min_y)
        #checked
        boardwells = self.getBoardWells(cells, min_y)
        #print(hole_num)
        #print(clone.cells)
        #weithting
        
        
        score = -45 * (23-min_y) - 32 * transition_row - 93 * transition_col + \
            34 * erodedPieceCellsMetric - 79 * hole_num - 34 * boardwells
        
        #score = (-4.500158825082766) * (23-min_y) + (-3.2178882868487753) * transition_row + (-9.348695305445199) * transition_col\
        # + (-7.899265427351652) * hole_num + (3.4181268101392694) * erodedPieceCellsMetric + (-3.3855972247263626) * boardwells
        
        #print(score)
        return score




# Rotation -> Movement + PD + next block 
class Adam_4(Player):

    def __init__(self, seed=None):
        self.random = Random(seed)
        self.best_rotation = 0

    def choose_action(self, board):

        action = self.rotation_first(board)
        #print(action)
        return action


    def rotation_first(self, board):
        bestscore = -999999
        #move = None
        #bestmove = None
        rotation = None
        clone_board = None
        #best_rotation = 0
        bestaction = []
        #list

        res = False

        for i in range(4):
            action = []
            move_action = []
            #count = 0
            clone_board = board.clone()
            if i == 1:
                rotation = Rotation.Clockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1

            elif i == 2:
                tmp_board = clone_board.clone()
                rotation = Rotation.Clockwise
                res = tmp_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Clockwise)
                    #count += 1
                    

                #try rotation from other direction
                else:
                    tmp_board = clone_board.clone()
                    action = []
                    rotation = Rotation.Anticlockwise
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Anticlockwise)
                    #count -= 1
                    if not res:
                        res = tmp_board.rotate(rotation)
                        action.append(Rotation.Anticlockwise)
                        #count -= 1
                    #clone_board = tmp_board
                    
                clone_board = tmp_board
                    
            elif i == 3:
                rotation = Rotation.Anticlockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Anticlockwise)               
                #count -= 1

            """
            else:
                #count = 0
                pass
            """
            
            if not res:
                for xtarget in range(10):
                    #print(clone_board.cells)
                    score, move_action = self.try_move(clone_board, xtarget)
                    #move = self.try_move(clone_board, xtarget)
                    #print(score)
                    
                    if score > bestscore:
                        #best_rotation = count
                        #print(count)
                        bestaction = action + move_action
                        bestscore = score
                        #bestmove = move
            else:
                score = self.score_board(clone_board)

            if score > bestscore:
                #best_rotation = count
                #print(count)
                bestscore = score
                #bestmove = move
                bestaction = action + move_action

        return bestaction

    def try_move(self, board, xtarget):
        clone_board = board.clone()
        move_action = []
        while True:
            if clone_board.falling.left < xtarget:
                trymove = Direction.Right
            elif clone_board.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            #if firstmove is None:
            #    firstmove = trymove
            res = clone_board.move(trymove)
            move_action.append(trymove)
            if res:
                #score, action = self.rotation_first_next_block(clone_board)
                #bug workaround from piazza
                clone_board.next = clone_board.falling

                score, action = self.rotation_first_next_block(clone_board)
                move_action += action
                #return score, move_action
                return score, move_action


    def rotation_first_next_block(self, board):
        bestscore = -999999
        #move = None
        #bestmove = None
        rotation = None
        clone_board = None
        #best_rotation = 0
        bestaction = []
        #list

        #not sure if we need to manually switch to next block


        res = False

        for i in range(4):
            action = []
            move_action = []
            #count = 0
            clone_board = board.clone()
            if i == 1:
                rotation = Rotation.Clockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1

            elif i == 2:
                tmp_board = clone_board.clone()
                rotation = Rotation.Clockwise
                res = tmp_board.rotate(rotation)
                action.append(Rotation.Clockwise)
                #count += 1
                if not res:
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Clockwise)
                    #count += 1
                    

                #try rotation from other direction
                else:
                    tmp_board = clone_board.clone()
                    action = []
                    rotation = Rotation.Anticlockwise
                    res = tmp_board.rotate(rotation)
                    action.append(Rotation.Anticlockwise)
                    #count -= 1
                    if not res:
                        res = tmp_board.rotate(rotation)
                        action.append(Rotation.Anticlockwise)
                        #count -= 1
                    #clone_board = tmp_board
                    
                clone_board = tmp_board
                    
            elif i == 3:
                rotation = Rotation.Anticlockwise
                res = clone_board.rotate(rotation)
                action.append(Rotation.Anticlockwise)               
                #count -= 1

            """
            else:
                #count = 0
                pass
            """
            
            if not res:
                for xtarget in range(10):
                    #print(clone_board.cells)
                    score, move_action = self.try_move_nextblock(clone_board, xtarget)
                    #move = self.try_move(clone_board, xtarget)
                    #print(score)
                    
                    if score > bestscore:
                        #best_rotation = count
                        #print(count)
                        bestaction = action + move_action
                        bestscore = score
                        #bestmove = move
            else:
                score = self.score_board(clone_board)

            if score > bestscore:
                #best_rotation = count
                #print(count)
                bestscore = score
                #bestmove = move
                bestaction = action + move_action

        return bestscore, bestaction



    def try_move_nextblock(self, board, xtarget):
        clone_board = board.clone()
        move_action = []
        while True:
            if clone_board.falling.left < xtarget:
                trymove = Direction.Right
            elif clone_board.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop
            #if firstmove is None:
            #    firstmove = trymove
            res = clone_board.move(trymove)
            move_action.append(trymove)
            if res:
                score = self.score_board(clone_board)
                return score, move_action
                #return firstmove



    def boardRowTransitions(self, cells, min_y):
        transition = 0
        for i in range(10):
            #start from 1 element befor top y coordinate, reduce loop num
            for j in range(min_y-1, 23):
                if ((i, j) not in cells) and ((i,j+1) in cells):
                    transition += 1  
                if ((i, j) in cells) and ((i,j+1) not in cells):
                    transition += 1  
        
        return transition
                
    def boardcolTransitions(self, cells):
        transition = 0
        for i in range(9):
            for j in range(24):
                if ((i, j) not in cells) and ((i+1,j) in cells):
                    transition += 1  
                elif ((i, j) in cells) and ((i+1,j) not in cells):
                    transition += 1  

        return transition
    
    def get_erodedPieceCellsMetric(self, board, cells):
        row_eliminated = 0
        usefulblock = 0
        falling_cells = board.falling.cells
        for j in range(24):
            count = 0
            for i in range(10):
                if (i, j) in cells:
                    count += 1
            if count == 10:
                row_eliminated += 1
                #print(row_eliminated)
                for k in range(10):
                    if (k, j) in falling_cells:
                        usefulblock += 1
        #print(usefulblock)
        return row_eliminated * usefulblock

    def getBoardBuriedHoles(self, cells, min_y):
        holes = 0
        for i in range(10):
            colhole = None
            for j in range(min_y, 24):
                if (colhole == None) and ((i,j) in cells):
                    colhole = 0
                if (colhole != None) and ((i,j) not in cells):
                    colhole += 1
            if colhole != None:
                holes += colhole
                
        return holes        


    def getBoardWells(self, cells, min_y):
        #save as list (sequence addition)
        #sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        sum_n = 0
        holes = 0
        sum = 0
        for i in range(10):
            #loop from min_y to 24, reduce some loop
            for j in range(min_y, 24):
                if (i ,j) not in cells:
                    if ((i+1, j)  in cells) and (i-1, j) in cells:
                        holes += 1
                    elif ( i-1 < 0 and (i+1, j) in cells):
                        holes += 1
                    elif ( i+1 > 9 and (i-1,j) in cells):
                        holes += 1
                else:
                    #sum += sum_n[holes]
                    sum_n += holes * (holes+1)/2
                    holes = 0
        return sum

    def score_board(self, clone):

        #get maximun landing y coordinate
        cells = clone.cells
        #if cells != False:
        #check if list is empty
        if cells:
            min_y = min([y for x,y in cells])
        else:
            min_y = 23
        #checked
        transition_row = self.boardRowTransitions(cells, min_y)
        transition_col = self.boardcolTransitions(cells)
        #not yet (checked)
        erodedPieceCellsMetric = self.get_erodedPieceCellsMetric(clone, cells)
        #checked
        hole_num = self.getBoardBuriedHoles(cells, min_y)
        #checked
        boardwells = self.getBoardWells(cells, min_y)
        #print(hole_num)
        #print(clone.cells)
        #weithting
        
        
        score = -45 * (23-min_y) - 32 * transition_row - 93 * transition_col + \
            34 * erodedPieceCellsMetric - 79 * hole_num - 34 * boardwells
        
        #score = (-4.500158825082766) * (23-min_y) + (-3.2178882868487753) * transition_row + (-9.348695305445199) * transition_col\
        # + (-7.899265427351652) * hole_num + (3.4181268101392694) * erodedPieceCellsMetric + (-3.3855972247263626) * boardwells
        
        #print(score)
        return score

#SelectedPlayer = RandomPlayer
#SelectedPlayer = version1_Mark
#SelectedPlayer = Adam_1
#SelectedPlayer = Adam_2
#SelectedPlayer = Adam_3
SelectedPlayer = Adam_4



























