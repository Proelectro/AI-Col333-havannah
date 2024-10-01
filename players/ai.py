import time
import math
import random
import numpy as np
from helper import *
from collections import defaultdict
from copy import deepcopy
from json import dumps, dump
from heapq import heappush, heappop

conv = defaultdict(int)
conv[1] = 1
conv[2] = -1
corners = None
edges = None
dim = None
BRANCH = 5
def static_score(state: np.array, move: Tuple[int, int], player: int, base_score: float) -> float:
    """
    Given the current state of the board, return the score of the move
    high score means player1 is winning, low score means player2 is winning
    
    # Parameters
    `state: Tuple[np.array]`
        - a numpy array containing the state of the board using the following encoding:
        - the board maintains its same two dimensions
        - spaces that are unoccupied are marked as 0
        - spaces that are blocked are marked as 3
        - spaces that are occupied by player 1 have a 1 in them
        - spaces that are occupied by player 2 have a 2 in them

    `move: Tuple[int, int]`
        - a tuple containing the coordinates of the move state is after the move

    `player: int`
        - the player number

    # Returns
    float: score
    """
    if move is None:
        return 0
    if check_win(state, move, player)[0]:
        return float('inf') * conv[player]

    distance = np.zeros((2 * dim - 1, 2 * dim - 1))
    distance.fill(float('inf'))
    visited = np.zeros((2 * dim - 1, 2 * dim - 1))
    indx = 0
    for i in range(2 * dim - 1):   
        for j in range(2 * dim - 1):
            if state[i, j] == 3 or state[i, j] == 0 or visited[i, j]:
                continue
            indx += 1
            visited[i, j] = indx
            distance[i, j] = 0
            stack = [(i, j)]
            while stack:
                top = stack.pop()
                for nb in get_neighbours(dim, top):
                    if state[nb] == 3 or visited[nb]:
                        continue
                    if state[top] == 0 and state[nb] == state[i, j]:
                        if visited[nb] == indx and distance[nb] == 2:
                            distance[nb] = 0
                            stack.append(nb)
                        elif visited[nb] != indx:
                            visited[nb] = indx
                            distance[nb] = 2
                    elif state[top] == state[i, j]:
                        if visited[nb] != indx:
                            if state[nb] == 0:
                                visited[nb] = indx
                                distance[nb] = 1
                                stack.append(nb)
                            elif state[nb] == state[i, j]:
                                visited[nb] = indx
                                distance[nb] = 0
                                stack.append(nb)
    player1_connected = [[] for _ in range(indx + 1)]
    player2_connected = [[] for _ in range(indx + 1)]
    for i in range(2 * dim - 1):
        for j in range(2 * dim - 1):
            if visited[i, j]:
                if state[i, j] == 1:
                    player1_connected[int(visited[i, j])].append((i, j))
                elif state[i, j] == 2:
                    player2_connected[int(visited[i, j])].append((i, j))
    print(" ------------------- ")
    print(move)
    print(state)
    print(player1_connected)
    print(player2_connected)
    print(" ------------------- ")
    return random.random()
    corner_score = []
    for corner in corners:
        corner_score.append(distance[corner])
    edges_score = []
    for side in edges:
        mn = float('inf')
        for edge in side:
            mn = min(mn, distance[edge])
        edges_score.append(mn)
    score = 0
    for corner in corner_score:
        score += 1/(corner + 0.1)**2
    score *= 2
    for edge in edges_score:
        score += 1/(edge + 0.1)**2
    return base_score + score * conv[player]
                
class Node:
    def __init__(self, move, player, score, parent, number) -> None:
        """
        Move: After the move, the board will be in this state
        Player: The player who played this move
        Score: The score of the move
        """
        self.move = move
        self.player = player
        self.children = []
        self.score = score
        self.static_score = score
        self.parent = parent
        self.move_number = number
    
    def json(self):
        
        return ({
            'move': (int(self.move[0]), int(self.move[1])) if self.move is not None else None,
            'player': self.player,
            'score': self.score,
            'static_score': self.static_score,
            'children': [child.json() for child in self.children]
        })
    
    def expand(self, state: np.array):
        """State: After the move, the board will be in this state"""
        for move in get_valid_actions(state, 3 - self.player):
            new_state = deepcopy(state)
            new_state[move] = 3 - self.player
            score = static_score(new_state, move, 3 - self.player, self.static_score)
            self.children.append(Node(move, 3 - self.player, score, self, self.move_number + 1))
            if self.player == 1:
                self.score = min(self.score, score)
            else:
                self.score = max(self.score, score)
        if self.parent:
            if self.player == 1:
                self.parent.score = max(self.parent.score, self.score)
            else:
                self.parent.score = min(self.parent.score, self.score)
            
class AIPlayer:
    def __init__(self, player_number: int, timer):
        """
        Intitialize the AIPlayer Agent

        # Parameters
        `player_number (int)`: Current player number, num==1 starts the game
        
        `timer: Timer`
            - a Timer object that can be used to fetch the remaining time for any player
            - Run `fetch_remaining_time(timer, player_number)` to fetch remaining time of a player
        """
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = 'Player {}: ai'.format(player_number)
        self.timer = timer
        self.root = None
        self.state = None

    def get_move(self, state: np.array) -> Tuple[int, int]:
        """
        Given the current state of the board, return the next move

        # Parameters
        `state: Tuple[np.array]`
            - a numpy array containing the state of the board using the following encoding:
            - the board maintains its same two dimensions
            - spaces that are unoccupied are marked as 0
            - spaces that are blocked are marked as 3
            - spaces that are occupied by player 1 have a 1 in them
            - spaces that are occupied by player 2 have a 2 in them

        # Returns
        Tuple[int, int]: action (coordinates of a board cell)
        """
        global corners, edges, dim
        if corners is None:
            dim = state.shape[0] + 1 >> 1
            corners = get_all_corners(dim)
            edges = get_all_edges(dim)
        
        if self.root is None:
            self.root = Node(None, 3 - self.player_number, 0, None, 0)
            self.state = state
        else:
            diff = None
            for move in get_valid_actions(self.state, 3 - self.player_number):
                if self.state[move] != state[move]:
                    diff = move
                    break
            self.state = state
            assert diff is not None
            for child in self.root.children:
                if child.move == diff:
                    self.root = child
                    self.root.parent = None
                    break
            else:
                self.root = Node(diff, 3 - self.player_number, 0, None, 0)
        leaf = []
        stack = [self.root]
        while stack:
            top = stack.pop()
            if not top.children:
                leaf.append(top)
            else:
                stack.extend(top.children)

        while leaf:
            top:Node = leaf.pop()
            if (top.move_number - self.root.move_number) < 2:
                new_state = deepcopy(state)
                lf = top
                while lf != self.root:
                    new_state[lf.move] = lf.player
                    lf = lf.parent
                top.expand(new_state)
                leaf.extend(top.children)


        with open("root.json", "w") as f:
            dump(self.root.json(), f)


        if self.root.children:
            if self.player_number == 1:
                self.root = max(self.root.children, key = lambda x: x.score)
            else:
                self.root = min(self.root.children, key = lambda x: x.score)
            self.root.parent = None
            self.state[self.root.move] = self.player_number        
            return self.root.move    
        else:
            mv = self.root.move
            self.root = None
            self.state = None
            return mv