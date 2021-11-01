"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)

    >>> result = generate_goals(4)
    >>> g0 = result[0]
    >>> g0.description()
    'Hello, world!"
    """
    colour_list = []  # [REAL_RED, PACIFIC_POINT]
    # 2 < 2 => False
    while len(colour_list) < num_goals:
        random_int = random.randint(0, len(COLOUR_LIST) - 1)  # 1
        random_color_tuple = COLOUR_LIST[random_int]  # REAL_RED

        if random_color_tuple not in colour_list:
            colour_list.append(random_color_tuple)

    result = []  # [b0, b1]
    random_int2 = random.randint(0, 1)  # 1
    for colour_tuple in colour_list:
        if random_int2 == 0:
            # PerimeterGoal
            goal = PerimeterGoal(colour_tuple)
        else:
            # Blobgoal
            goal = BlobGoal(colour_tuple)
        result.append(goal)

    return result


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    lst = []

    for i in range(2**(block.max_depth - block.level)):
        lst.append([])

    if block.colour is not None:
        for sub_lst in lst:
            for i in range(2**(block.max_depth - block.level)):
                sub_lst.append(block.colour)
    else:
        lst_0 = _flatten(block.children[0])
        lst_1 = _flatten(block.children[1])
        lst_2 = _flatten(block.children[2])
        lst_3 = _flatten(block.children[3])

        for i in range(len(lst)//2):
            lst[i] = lst_1[i] + lst_2[i]

        for i in range(len(lst)//2, len(lst)):
            lst[i] = lst_0[i-(len(lst)//2)] + lst_3[i-(len(lst)//2)]

    return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A perimeter player goal in the game of Blocky. Player must aim to have
    as many unit cells on the perimeter of the board be their target colour.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """The player must aim to put the most possible units of a given colour
        c on the outer perimeter of the board. The player’s score is the total
        number of unit cells of colour c that are on the perimeter. There is a
        premium on corner cells: they count twice towards the score."""
        count = 0
        c = self.colour
        lst = _flatten(board)

        for i in range(len(lst)):
            if i in (0, len(lst) - 1) and lst[0][i] == c:
                count += 2
            elif lst[0][i] == c:
                count += 1

        for i in range(len(lst)):
            if i in (0, len(lst) - 1) and lst[len(lst)-1][i] == c:
                count += 2
            elif lst[len(lst)-1][i] == c:
                count += 1

        for i in range(1, len(lst)-1):
            if lst[i][0] == c:
                count += 1
            if lst[i][len(lst)-1] == c:
                count += 1

        return count

    def description(self) -> str:

        colour = ''

        if self.colour == (1, 128, 181):
            colour = 'PACIFIC POINT'
        elif self.colour == (199, 44, 58):
            colour = 'REAL RED'
        elif self.colour == (138, 151, 71):
            colour = 'OLD OLIVE'
        elif self.colour == (255, 211, 92):
            colour = 'DAFFODIL DELIGHT'
        elif self.colour == (255, 255, 255):
            colour = 'WHITE'
        elif self.colour == (0, 0, 0):
            colour = 'BLACK'
        elif self.colour == (234, 62, 112):
            colour = 'MELON MAMBO'
        elif self.colour == (75, 196, 213):
            colour = 'TEMPTING TURQUOISE'

        return 'PLAY TO COLOUR THE PERIMETER {}'.format(colour)


class BlobGoal(Goal):
    """A blob player goal in the game of Blocky. Player must aim to form the
    largest possible blob in their target colour.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        flattened_board = _flatten(board)
        visited = []
        for i in range(len(flattened_board)):
            a = []
            for j in range(len(flattened_board)):
                a.append(-1)
            visited.append(a)

        ret = 0
        for i in range(0, len(flattened_board)):
            for j in range(0, len(flattened_board)):
                ret = max(ret, self._undiscovered_blob_size(
                    (i, j), flattened_board, visited))

        return ret

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if 0 <= pos[0] < len(board) and 0 <= pos[1] < len(board) and \
                visited[pos[0]][pos[1]] == -1:
            if board[pos[0]][pos[1]] == self.colour:
                visited[pos[0]][pos[1]] = 1
                return self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                    board, visited) + \
                       self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                    board, visited) + \
                       self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                    board, visited) + \
                       self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                    board, visited) + 1
            else:
                visited[pos[0]][pos[1]] = 0
                return 0
        return 0

    def description(self) -> str:

        colour = ''

        if self.colour == (1, 128, 181):
            colour = 'PACIFIC POINT'
        elif self.colour == (199, 44, 58):
            colour = 'REAL RED'
        elif self.colour == (138, 151, 71):
            colour = 'OLD OLIVE'
        elif self.colour == (255, 211, 92):
            colour = 'DAFFODIL DELIGHT'
        elif self.colour == (255, 255, 255):
            colour = 'WHITE'
        elif self.colour == (0, 0, 0):
            colour = 'BLACK'
        elif self.colour == (234, 62, 112):
            colour = 'MELON MAMBO'
        elif self.colour == (75, 196, 213):
            colour = 'TEMPTING TURQUOISE'

        return 'PLAY TO CREATE THE LARGEST {} BLOB POSSIBLE'.format(colour)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
