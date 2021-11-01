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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    lst = []
    counter = 0
    goals = generate_goals(num_human + num_random + len(smart_players))

    for _ in range(num_human):
        lst.append(HumanPlayer(counter, goals[counter]))
        counter += 1

    for _ in range(num_random):
        lst.append(RandomPlayer(counter, goals[counter]))
        counter += 1

    for diff in smart_players:
        lst.append(SmartPlayer(counter, goals[counter], diff))
        counter += 1

    return lst


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    block_x, block_y, size = block.position[0], block.position[1], block.size
    location_x, location_y = location[0], location[1]

    # check if x is in range
    if location_x < block_x or location_x >= (block_x + size):
        return None

    # check if y in range
    if location_y < block_y or location_y >= (block_y + size):
        return None

    child_size = round(block.size / 2.0)

    left_x, middle_x, right_x = block_x, block_x + child_size, block_x + size
    top_y, middle_y, bottom_y = block_y, block_y + child_size, block_y + size

    if block.level == level or (block.level < level and len(block.children)
                                == 0):
        return block
    else:  # block.level < level and len(block.children) == 4:
        if middle_x <= location_x < right_x and top_y <= location_y < middle_y:
            return _get_block(block.children[0], location, level)
        elif left_x <= location_x < middle_x and top_y <= location_y < middle_y:
            return _get_block(block.children[1], location, level)
        elif left_x <= location_x < middle_x and \
                middle_y <= location_y < bottom_y:
            return _get_block(block.children[2], location, level)
        else:  # child 3 (middle_x - right_x, middle_y - bottom_y)
            return _get_block(block.children[3], location, level)


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A random player.
    """
    # === Public Attributes ===
    # id:
    #   This player's number.
    # goal:
    #   This player's assigned goal for the game.
    #
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    id: int
    goal: Goal
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        actions = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, SWAP_HORIZONTAL,
                   SWAP_VERTICAL, SMASH, PAINT, COMBINE]

        check = False
        action, block = '', ''

        while check is False:
            copy = board.create_copy()
            level = random.randint(0, copy.max_depth)
            x = random.randint(copy.position[0], copy.position[0] + copy.size-1)
            y = random.randint(copy.position[1], copy.position[1] + copy.size-1)
            block = _get_block(copy, (x, y), level)
            action = random.choice(actions)

            if action == ROTATE_CLOCKWISE:
                check = block.rotate(1)
            elif action == ROTATE_COUNTER_CLOCKWISE:
                check = block.rotate(3)
            elif action == SWAP_HORIZONTAL:
                check = block.swap(0)
            elif action == SWAP_VERTICAL:
                check = block.swap(1)
            elif action == SMASH:
                check = block.smashable()
            elif action == PAINT:
                check = block.paint(self.goal.colour)
            elif action == COMBINE:
                check = block.combine()

        block_on_board = _get_block(board, block.position, block.level)

        self._proceed = False  # Must set to False before returning!
        return _create_move(action, block_on_board)


class SmartPlayer(Player):
    """A smart player.
    """
    # === Public Attributes ===
    # id:
    #   This player's number.
    # goal:
    #   This player's assigned goal for the game.
    #
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _difficulty:
    #   the player's level of difficulty, the higher the level the more
    #   challenging the player will be to play against
    id: int
    goal: Goal
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        actions = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, SWAP_HORIZONTAL,
                   SWAP_VERTICAL, SMASH, PAINT, COMBINE]

        valid_moves = []

        while len(valid_moves) < self._difficulty:

            copy = board.create_copy()
            x = random.randint(copy.position[0], copy.position[0] +
                               copy.size-1)
            y = random.randint(copy.position[1], copy.position[1] +
                               copy.size-1)
            block = _get_block(copy, (x, y), random.randint(0, copy.max_depth))
            action = random.choice(actions)

            # check move validity
            if self._check_move_validity(action, block):
                valid_moves.append((action, block.position, block.level))

        current_score = self.goal.score(board)

        best_score, best_move = current_score, ()

        for move in valid_moves:

            copy = board.create_copy()
            block = _get_block(copy, move[1], move[2])

            if move[0] == ROTATE_CLOCKWISE:
                block.rotate(1)
            elif move[0] == ROTATE_COUNTER_CLOCKWISE:
                block.rotate(3)
            elif move[0] == SWAP_HORIZONTAL:
                block.swap(0)
            elif move[0] == SWAP_VERTICAL:
                block.swap(1)
            elif move[0] == SMASH:
                block.smash()
            elif move[0] == PAINT:
                block.paint(self.goal.colour)
            elif move[0] == COMBINE:
                block.combine()

            move_score = self.goal.score(copy)

            if move_score > best_score:
                best_score = move_score
                best_move = move

        self._proceed = False  # Must set to False before returning!
        if current_score >= best_score:
            return _create_move(PASS, board)
        else:
            block_on_board = _get_block(board, best_move[1], best_move[2])
            return _create_move(best_move[0], block_on_board)

    def _check_move_validity(self, action: Tuple[str, Optional[int]],
                             block: Block) -> bool:
        """Return if the action can be validly performed on block."""
        if action == ROTATE_CLOCKWISE:
            return block.rotate(1)
        elif action == ROTATE_COUNTER_CLOCKWISE:
            return block.rotate(3)
        elif action == SWAP_HORIZONTAL:
            return block.swap(0)
        elif action == SWAP_VERTICAL:
            return block.swap(1)
        elif action == SMASH:
            return block.smashable()
        elif action == PAINT:
            return block.paint(self.goal.colour)
        elif action == COMBINE:
            return block.combine()


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
