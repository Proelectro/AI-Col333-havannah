import time
import math
import random
import numpy as np
from helper import *
from collections import defaultdict, deque
from copy import deepcopy
from json import dumps, dump
from heapq import heappush, heappop

# conv = defaultdict(int)
# conv[1] = 1
# conv[2] = -1
corners = None
edges = None
dim = None
BRANCH = 5

def check_neighbours(pos1, pos2):
    if pos1[0] == pos2[0] or pos1[1] == pos2[1]:
        return True
    siz = dim//2
    if pos1 > pos2:
        pos1, pos2 = pos2, pos1
    if (pos1[1] < siz) ^ (pos2[1] + 1 == pos1[1]):
        return True
    return False

def iscorner(pos):
    a = [0, dim//2, dim - 1]
    if pos[0] in a and pos[1] in a:
        return True
    return False

def isedge(pos):
    if iscorner(pos):
        return False
    if not all(pos):
        return True
    if pos[1] == dim - 1:
        return True
    if sum(pos) == dim - 1 + dim//2:
        return True
    if pos[0] - pos[1] == dim//2:
        return True
    return False



def static_score(state: np.array, move: Tuple[int, int], player: int) -> float:
    if move is None:
        return 0
    if check_win(state, move, player)[0]:
        return float("inf") if player == 1 else -float("inf")
    distance = np.zeros((dim, dim))
    visited = np.zeros((dim, dim))
    indx = 0
    for check in [player, 3 - player]:
        for i in range(dim):   
            for j in range(dim):
                if state[i, j] != check or visited[i, j]:
                    continue
                indx += 1
                visited[i, j] = indx
                stack = [(i, j)]
                single = set()
                while stack:
                    top = stack.pop()
                    for nb in get_neighbours(dim, top):
                        if state[nb] == 3 or visited[nb] == indx:
                            continue
                        if state[top] == 0 and state[nb] == state[i, j]:
                            if nb in single:
                                visited[nb] = indx
                                stack.append(nb)
                                single.remove(nb)
                            elif visited[nb] != indx:
                                single.add(nb)
                        elif state[top] == state[i, j]:
                            if visited[nb] != indx:
                                if state[nb] == 0:
                                    visited[nb] = indx
                                    stack.append(nb)
                                elif state[nb] == state[i, j]:
                                    visited[nb] = indx
                                    stack.append(nb)
        if player == check:
            indx_move = visited[move]
            state[move] = 0
    state[move] = player
    visited[move] = indx_move
    connected = [[] for _ in range(indx + 1)]
    owner = [0 for _ in range(indx + 1)]
    for i in range(dim):
        for j in range(dim):
            if visited[i, j] and state[i, j] in (1, 2):
                connected[int(visited[i, j])].append((i, j))
                owner[int(visited[i, j])] = state[i, j]
    # print(" ------------------- ")
    # print(move)
    # print(state)
    # print(connected)
    # print(owner)
    # print(" ------------------- ")
    corner_score = [[] for _ in range(indx + 1)]
    active = np.zeros((dim, dim))
    for i, corner in enumerate(corners):
        if state[corner] in (1, 2):
            corner_score[int(visited[corner])].append(0)
        else:
            queue = deque([(0, corner)])
            depth = dim + 1
            while queue and depth > 0:
                depth -= 1
                d, top = queue.popleft()
                for nb in get_neighbours(dim, top):
                    if state[nb] in (1, 2):
                        corner_score[int(visited[nb])].append(1 + d)
                    elif state[nb] == 0 and active[nb] != i:
                        active[nb] = i
                        queue.append((d + 1, nb))
        
    edges_score = [[] for _ in range(indx + 1)]
    for side in edges:
        side_score = [0 for _ in range(indx + 1)]
        for pp, edge in enumerate(side, start=1):
            if state[edge] in (1, 2):
                side_score[int(visited[edge])] = -1
            elif state[edge] == 0:
                for nb in get_neighbours(dim, edge):
                    if state[nb] in (1, 2):
                        if side_score[int(visited[nb])] != pp and side_score[int(visited[nb])] != 0:
                            side_score[int(visited[nb])] = -1
                        else:
                            side_score[int(visited[nb])] = pp                     
        for i in range(1, indx + 1):
            if side_score[i] == -1:
                edges_score[i].append(0)
                
        queue = deque()
        for edge in side:
            if state[edge] == 0:
                queue.append((0, edge))
                
        depth = dim + 3
        while queue and depth > 0:
            depth -= 1
            d, top = queue.popleft()
            for nb in get_neighbours(dim, top):
                if state[nb] in (1, 2):
                    edges_score[int(visited[nb])].append(1 + d)
                elif state[nb] == 0 and active[nb] != i:
                    active[nb] = i
                    queue.append((d + 1, nb))
    
    # print(" ------------------- ")
    # print(corner_score)
    # print(edges_score)
    # print(" ------------------- ")

    score = 0
    for i in range(indx + 1):
        cs = 0
        # if len(corner_score[i]) == 1 and corner_score[i][0] == 0:
        #     cs = 100
        if len(corner_score[i]) >= 2:
            corner_score[i].sort()
            if corner_score[i][0] == corner_score[i][1] == 0:
                cs = 1000
            elif corner_score[i][0] == 0:
                cs = 30 + sum([10/x**2 for x in corner_score[i][1:]])
            else:
                cs = sum([10/x**2 for x in corner_score[i]])
        es = 0
        if len(edges_score[i]) >= 3:
            edges_score[i].sort()
            if edges_score[i][0] == edges_score[i][1] == edges_score[i][2] == 0:
                es = 1000
            elif edges_score[i][0] == edges_score[i][1] == 0:
                es = 50 + sum([10/x**2 for x in edges_score[i][2:]])
            elif edges_score[i][0] == 0:
                es = 12 + sum([10/x**2 for x in edges_score[i][1:]])
            else:
                es = sum([10/x**2 for x in edges_score[i]])
        # print(cs, es)
        ts = cs + es - 70
        score += ts if owner[i] == 1 else -ts
    return score

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
    def update(self, score):
        if self.player == 1:
            self.score = min(self.score, score)
        else:
            self.score = max(self.score, score)
        if self.parent is not None:
            self.parent.update(score)
        
    def expand(self, state: np.array):
        """State: After the move, the board will be in this state"""
        for move in get_valid_actions(state, 3 - self.player):
            new_state = deepcopy(state)
            new_state[move] = 3 - self.player
            score = static_score(new_state, move, 3 - self.player)
            self.children.append(Node(move, 3 - self.player, score, self, self.move_number + 1))
            if self.player == 1:
                self.score = min(self.score, score)
            else:
                self.score = max(self.score, score)
        if self.player == 1:
            self.children.sort(key = lambda x: x.score)
        else:
            self.children.sort(key = lambda x: x.score, reverse=True)
        if self.parent is not None:
            self.parent.update(self.score)    
        
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
            dim = state.shape[0]
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


        # ------------------------------------------
        while leaf:
            # So your job is to choose a leaf node wisely and expand it
            top:Node = leaf.pop()
            
            # and apply any condition to expand the leaf node
            if (top.move_number - self.root.move_number) < 2 and abs(top.static_score) != float("inf"):
                # expand the give leaf (top)
                new_state = deepcopy(state)
                lf = top
                while lf != self.root:
                    new_state[lf.move] = lf.player
                    lf = lf.parent
                top.expand(new_state)
                leaf.extend(top.children)


        # ------------------------------------------

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