""" Team44 Xtreme Tic Tac Toe Tournament implementation using negamax alphabeta pruning """
import copy
import datetime
import random

class Team44():
    """Class Team44 returns move after looking at the available moves using the negamax search."""

    def __init__(self):
        self.max_depth = 6
        self.big_board_win_pos = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        self.small_board_win_pos = [[0, 1, 2]]
        self.score_table = {'2inrow': 10, '3inrow': 100, '1inrow': 1,
                            'block2inrow': 5, 'block1inrow': 5}
        self.inf = 100000000
        self.good_moves = []
        self.big_board_lineup_pos = []
        self.small_board_lineup_pos = []
        self.tdelta = datetime.timedelta(seconds=23)
        self.starttime = datetime.datetime.utcnow()


    @classmethod
    def get_block_cords(cls, old_move):
        """Get Block and cell coordinates given the move
             co ordinates of the form boardno, row, col"""

        block_x = old_move[1] / 3
        cell_x = old_move[1] % 3
        block_y = old_move[2] / 3
        cell_y = old_move[2] % 3
        # print("blockx:", block_x, "blocky:", block_y, "cellx:", cell_x, "celly:", cell_y, )
        return (old_move[0], block_x, cell_x, block_y, cell_y)


    def evaluate(self, lineup_pos, flag, bstatus):
        """ check the row, col, diagonal set in lineup_pos
             for xxx, xx-, x-, ooo, oo-, o--, etc patterns and assign weights to decide
             hueristic. Used in both Block and bigboard level hueristic derivation"""
        value = 0
        glaf = 'x' if flag == 'o' else 'o'
        # evaluate win positions
        for (a, b, c) in lineup_pos:
            # print(a, b, c)
            p = bstatus[a[0]][a[1]]
            q = bstatus[b[0]][a[1]]
            r = bstatus[c[0]][c[1]]
            # print(p,q,r)
            if bstatus[a[0]][a[1]] == flag and q == flag and r == flag:
                value += self.score_table["3inrow"]

            elif bstatus[a[0]][a[1]] == glaf and q == glaf and r == glaf:
                value -= self.score_table["3inrow"]

            if value in [100, -100]:
                return value/100

            # 2 of self in row, one blank
            if p == flag and q == flag and r == '-':
                value += self.score_table["2inrow"]
            elif p == flag and q == '-'  and r == flag:
                value += self.score_table["2inrow"]
            elif p == '-'  and q == flag and r == flag:
                value += self.score_table["2inrow"]

            # 2 of opponent in row, one blank
            elif p == glaf and q == glaf and r == '-':
                value -= self.score_table["2inrow"]
            elif p == glaf and q == '-' and r == glaf:
                value -= self.score_table["2inrow"]
            elif p == '-' and q == glaf and r == glaf:
                value -= self.score_table["2inrow"]

            # 1 of self in row, two blank
            elif p == flag and q == '-' and r == '-':
                value += self.score_table["1inrow"]
            elif p == '-' and q == '-'  and r == flag:
                value += self.score_table["1inrow"]

            # 1 of opponent in row, two blank
            elif p == glaf and q == '-' and r == '-':
                value -= self.score_table["1inrow"]
            elif p == '-' and q == '-'  and r == glaf:
                value -= self.score_table["1inrow"]

            #  block1 by opponent
            elif p == flag and q == flag and r == glaf:
                value += self.score_table["block1inrow"]
            elif p == flag and q == glaf  and r == flag:
                value += self.score_table["block1inrow"]
            elif p == glaf  and q == flag and r == flag:
                value += self.score_table["block1inrow"]

                # 2 of opponent in row, one block
            elif p == glaf and q == glaf and r == flag:
                value -= self.score_table["block1inrow"]
            elif p == glaf and q == flag and r == glaf:
                value -= self.score_table["block1inrow"]
            elif p == flag and q == glaf and r == glaf:
                value -= self.score_table["block1inrow"]

            # 1 of self in row, two opponent
            elif p == flag and q == glaf and r == glaf:
                value += self.score_table["block2inrow"]
            elif p == glaf and q == glaf  and r == flag:
                value += self.score_table["block2inrow"]

            # 1 of opponent in row, two of us
            elif p == glaf and q == flag and r == flag:
                value -= self.score_table["block2inrow"]
            elif p == flag and q == flag  and r == glaf:
                value -= self.score_table["block2inrow"]

        # print("hfunc2:", value)
        return value

    def hfunc_block(self, bstatus, flag, block_coords, lineup_pos, win_pos):
        """ given the bigboard get the current moves block and possible
            row, colunm and diagonals associated with that block """
        for pos in win_pos:
            # print("pos:", pos)
            # print(block_coords[1], block_coords[3])
            block_x = block_coords[1]
            block_y = block_coords[3]
            ay = pos[0] / 3 + block_y * 3
            ax = pos[0] % 3 + block_x * 3
            by = pos[1] / 3 + block_y * 3
            bx = pos[1] % 3 + block_x * 3
            cy = pos[2] / 3 + block_y * 3
            cx = pos[2] % 3 + block_x * 3
            lineup_pos.append(([ax, ay], [bx, by], [cx, cy]))
            lineup_pos.append(([ay, ax], [by, bx], [cy, cx]))
            d1 = []
            d2 = []
            count = -1
        for a, b, c in lineup_pos:
            # print(a, b, c)
            count += 1
            if count == 0:
                d1.append([a[0], a[1]])
            if count == 1:
                d2.append([c[1], c[0]])
            if count == 2:
                d1.append([b[0], b[1]])
            if count == 3:
                d2.append([b[1], b[0]])
            if count == 4:
                d1.append([c[0], c[1]])
            if count == 5:
                d2.append([a[1], a[0]])

        lineup_pos.append(d2)
        lineup_pos.append(d1)

        return self.evaluate(lineup_pos, flag, bstatus)

    def hfunc_small_board(self, bstatus, flag, block_coords, lineup_pos, win_pos):
        """ given the smallboard status use block coords as cell coords and derive possible
            row, colunm and diagonals associated with that smallboard """
        for pos in win_pos:
            # print(pos)
            ax = block_coords[1]
            ay = block_coords[3]
            lineup_pos.append(([ax, pos[0]], [ax, pos[1]], [ax, pos[2]]))
            lineup_pos.append(([pos[0], ay], [pos[1], ay], [pos[2], ay]))
            if ax == 0 or  ax == 2:
                lineup_pos.append(([0, 0], [1, 1], [2, 2]))
                lineup_pos.append(([2, 0], [1, 1], [0, 2]))
            if ay == 0 or  ay == 2:
                lineup_pos.append(([0, 0], [1, 1], [2, 2]))
                lineup_pos.append(([2, 0], [1, 1], [0, 2]))

        return self.evaluate(lineup_pos, flag, bstatus)


    def hfunc2(self, flag, block_coords, bstatus, bstatuss):
        """ combine block, cell heuristic of the big board """
        value = 0
        self.big_board_lineup_pos = []
        value = self.hfunc_block(bstatus, flag, block_coords,
                                 self.big_board_lineup_pos, self.big_board_win_pos)
        self.small_board_lineup_pos = []
        value += self.hfunc_small_board(bstatuss, flag, block_coords,
                                        self.small_board_lineup_pos, self.small_board_win_pos)
        heuristic = 0

        if abs(value) in [0, 1]:
            return value
        if abs(value) in [1, 2]:
            heuristic = 1+(10-1)*(value-1)
        if abs(value) in [2, 3]:
            heuristic = 10+(100-90)*(value-2)
        if abs(value) == 3:
            heuristic = 100

        # print("hfunc22:", heuristic, heuristic/100.0)
        return heuristic/100.0

    def hfunc_over_all(self, board, flag, old_move):
        """ combine heuristic of the  2 big boards """
        block_coords = Team44.get_block_cords(old_move)
        bstatus = board.big_boards_status[0]
        bstatuss = board.small_boards_status[0]
        bstatus1 = board.big_boards_status[1]
        bstatuss1 = board.small_boards_status[1]
        heuristic1 = self.hfunc2(flag, block_coords, bstatus, bstatuss)
        heuristic2 = self.hfunc2(flag, block_coords, bstatus1, bstatuss1)
        heuristic = heuristic1**3 + heuristic2**3
        # print("heuristic:", heuristic1, heuristic2, heuristic)
        return heuristic


    def negamax(self, board, alpha, beta, color, old_move, depth, flag):
        """ negamax search to obtain best possible move """
        available_moves = board.find_valid_move_cells(old_move)
        temp_board = copy.deepcopy(board)

        if depth == 0:
            return self.hfunc_over_all(temp_board, flag, old_move)

        value = -self.inf
        for move in available_moves:
            temp_board.update(old_move, move, flag)
            next_flag = 'x' if flag == 'o' else 'o'
            value = max(value, -1*self.negamax(temp_board, -alpha, -beta,
                                               -color, move, depth-1, next_flag))
            if depth == self.max_depth:
                self.good_moves.append(move)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
            if datetime.datetime.utcnow()- self.starttime >= self.tdelta:
                print("time exceed\n")
                break
        return value

    def move(self, board, old_move, flag):
        """ obtain best possible move based on last move """

        if old_move == (-1, -1, -1):
            cells = board.find_valid_move_cells(old_move)
            return cells[random.randrange(len(cells))]
            # return (1, 8, 2)
        print(flag)
        self.good_moves = []
        self.starttime = datetime.datetime.utcnow()
        # print("time:", self.starttime)
        color = 1
        self.negamax(board, -self.inf, self.inf, color, old_move, self.max_depth, flag)
        idx = len(self.good_moves)
        return self.good_moves[idx-1]
