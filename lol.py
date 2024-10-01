import numpy as np
from helper import get_neighbours
from typing import Tuple
a = [
    [2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 0],
    [0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0],
    [3, 0, 0, 0, 1, 0, 3],
    [3, 3, 0, 0, 0, 3, 3],
    [3, 3, 3, 1, 3, 3, 3]
]
state = np.array(a)
dim = 4
def static_score(state: np.array, move: Tuple[int, int], player: int, base_score: float) -> float:
    if move is None:
        return 0
    
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
                if (i, j) == (2, 3):
                    print(stack)
                top = stack.pop()
                for nb in get_neighbours(dim*2-1, top):
                    if state[nb] == 3 or visited[nb] == indx:
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
    


static_score(state, (0, 0), 2, 0.0)