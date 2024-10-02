import numpy as np
from helper import get_neighbours, get_all_corners, get_all_edges, get_corner, get_edge
from typing import Tuple
from collections import deque, defaultdict
dim = 7
def check_neighbours(pos1, pos2):
    for nb in get_neighbours(dim, pos1):
        if nb == pos2:
            return True
    return False

x = check_neighbours((1, 3), (2,2 ))
print(x)
corners = get_all_corners(dim)
edges = get_all_edges(dim)
def static_score(state: np.array, move: Tuple[int, int], player: int) -> float:
    if move is None:
        return 0
    # if check_win(state, move, player)[0]:
    #     return float("inf") if player == 1 else -float("inf")
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
    def check_safe(i, node):
        for nb1 in get_neighbours(dim, node):
            if nb1 not in ring_set:
                continue
            for nb2 in get_neighbours(dim, node):
                if nb1 == nb2 or check_neighbours(nb1, nb2):
                    continue
                if nb2 not in ring_set:
                    continue
                if sum(state[q] == owner[i] for q in [node, nb1, nb2]) < 2:
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
        print(connected[i])
        print(ring_set)
        priority = list(ring_set)
        while priority:
            node = priority.pop()
            if node in ring_set and not check_safe(i, node):
                print(node)
                ring_set.remove(node)
                priority.extend(get_neighbours(dim, node))
    
        if ring_set:
            print(ring_set)
            if len(ring_set) > 5:
                ring_score[i] += 1000 - 50 * sum(1 for node in ring_set if state[node] == 0) ** 2
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

    
a = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 3],
    [3, 3, 0, 0, 0, 3, 3],
    [3, 3, 3, 0, 3, 3, 3]
]
state = np.array(a)



print(static_score(state, (2, 2), 1))