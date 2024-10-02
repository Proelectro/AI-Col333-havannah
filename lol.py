import numpy as np
from helper import get_neighbours, get_all_corners, get_all_edges
from typing import Tuple
from collections import deque
a = [
    [1, 0, 0, 0, 0, 0, 0],
    [0, 2, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 3],
    [3, 3, 0, 0, 0, 3, 3],
    [3, 3, 3, 0, 3, 3, 3]
]
state = np.array(a)
dim = 7

corners = get_all_corners(dim)
edges = get_all_edges(dim)
def static_score(state: np.array, move: Tuple[int, int], player: int) -> float:
    if move is None:
        return 0
    # if check_win(state, move, player)[0]:
    #     return float("inf") if player == 1 else -float("inf")
    # distance = np.zeros((dim, dim))
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
    print(" ------------------- ")
    print(move)
    print(state)
    print(connected)
    print(owner)
    print(" ------------------- ")
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
    
    print(" ------------------- ")
    print(corner_score)
    print(edges_score)
    print(" ------------------- ")

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
    
    


print(static_score(state, (1, 2), 1))