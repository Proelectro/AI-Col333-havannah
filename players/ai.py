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
    corner_list = [[] for _ in range(indx + 1)]
    edges_list = [[] for _ in range(indx + 1)]
    score = [0] * (indx + 1)
    ring_score = [0] * (indx + 1)
    metagraph = defaultdict(lambda: float("inf"))
    def check_safe(node):
        for nb1 in get_neighbours(dim, node):
            if nb1 not in ring_set:
                continue
            for nb2 in get_neighbours(dim, node):
                if nb1 == nb2 or check_neighbours(nb1, nb2):
                    continue
                if nb2 not in ring_set:
                    continue
                return True
        return False
    for i in range(indx + 1):
        if owner[i] == 0:
            continue
        visi = set()
        virtual_edges = set()
        done_edges = set()
        queue = deque((0, k) for k in connected[i])
        depth = dim
        if dim > 10 and len(connected[i]) < 4 and indx > 4:
            depth = 3
        
        while queue:
            d, top = queue.popleft()
            if d > depth:
                break
            if top in visi:
                continue
            visi.add(top)
            c1 = get_corner(top, dim)
            e1 = get_edge(top, dim)
            if c1 != -1:
                corner_list[i].append(d)            
            elif e1 != -1:
                if e1 not in done_edges:
                    if d == 1:
                        if e1 in virtual_edges:
                            edges_list[i].append(0)
                            done_edges.add(e1)
                        else:
                            virtual_edges.add(e1)                
                    else:
                        edges_list[i].append(d)
                        done_edges.add(e1)
            
            elif visited[top] != i and state[top] == owner[i]:
                metagraph[(visited[top], i)] = min(metagraph[(visited[top], i)], d)
                
            for nb in get_neighbours(dim, top):
                if nb in visi:
                    continue
                if state[nb] != 3 - owner[i]:
                    queue.append((d+1, nb))
    
        ring_set = set()
        for node in connected[i]:
            ring_set.add(node)
            for nb in get_neighbours(dim, node):
                if state[nb] == 0:
                    ring_set.add(nb)
        priority = list(ring_set)
        while priority:
            node = priority.pop()
            if node in ring_set and not check_safe(node):
                ring_set.remove(node)
                priority.extend(get_neighbours(dim, node))
    
        if ring_set:
            if len(ring_set) > 5:
                
                ring_score[i] += 3000 - 50 * sum(1 for node in ring_set if state[node] == 0) ** 2
    # print(" ------------------- ")
    # print(corner_list)
    # print(edges_list)
    # print(" ------------------- ")

    for i in range(indx + 1):
        cz = corner_list[i].count(0)
        ez = edges_list[i].count(0)
        cl = len(corner_list[i])
        el = len(edges_list[i])
        score[i] -= 100
        # score[i] += ring_score[i]
        if cz >= 2 or ez >= 3:
            conn_comp = 0
            visi = set()
            for node in connected[i]:
                if node in visi:
                    continue
                stack = [node]
                conn_comp += 1
                while stack:
                    top = stack.pop()
                    for nb in get_neighbours(dim, top):
                        if nb in visi:
                            continue
                        if state[nb] == owner[i]:
                            stack.append(nb)
                            visi.add(nb)
            score[i] += 3000 - 200 * conn_comp         
            continue
        if cl == 1 and cz == 1:
            score[i] += 100
        
        if cl >= 2:
            if cz == 1:
                score[i] += 400 / min(k for k in corner_list[i] if k)
                for j in corner_list[i]:
                    if j > 0:
                        score[i] += 200 / j**2
            else:
                for j in corner_list[i]:
                    if j > 0:
                        score[i] += 50 / j**2
        if el >= 3:
            if ez == 2:
                score[i] += 700 / min(k for k in edges_list[i] if k)
                for j in edges_list[i]:
                    if j > 0:
                        score[i] += 300 / j**2
            elif ez == 1:
                score[i] += 200 / min(k for k in edges_list[i] if k)
                for j in edges_list[i]:
                    if j > 0:
                        score[i] += 50 / j**2
            else:
                for j in edges_list[i]:
                    if j > 0:
                        score[i] += 30 / j**2
    total = 0
    for i in range(indx + 1):
        if owner[i] == 0:
            continue
        # print(owner[i], score[i])
        total += score[i] if owner[i] == 1 else -score[i]
    
    for i, j in metagraph:
        p = (50 / metagraph[(i, j)])
        total += p * (1 if owner[int(i)] == 1 else -1)
    
    return total

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
            if (top.move_number - self.root.move_number) < 1 and abs(top.static_score) != float("inf"):
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