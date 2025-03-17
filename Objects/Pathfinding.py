import heapq

import numpy as np
# Let op!: current position moet tuple zijn

class AStar:
    def __init__(self):
        pass

    def search_path(self, start, end, collors_allowed):
        # get collisions
        # self.get_collision_layer(collors_allowed)
        file = ("/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Data/Input/collisions/" +
                f"{collors_allowed}.txt")

        collisions = np.loadtxt(file, dtype=int)

        open_set = []
        heapq.heappush(open_set, (0, tuple(start)))  # Convert start to tuple
        came_from = {}
        g_score = {tuple(start): 0}  # Convert start to tuple
        f_score = {tuple(start): self.heuristic(start, end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == tuple(end):  # Ensure end comparison matches tuple
                path = []
                while current in came_from:
                    path.append(list(current))  # Convert back to list for consistency
                    current = came_from[current]
                path.append(list(start))  # Convert back to list
                return path[::-1]

            for neighbor in self.get_neighbors(current, collisions):
                neighbor_tuple = tuple(neighbor)  # Convert to tuple for dict key
                tentative_g_score = g_score[current] + 1
                if neighbor_tuple not in g_score or tentative_g_score < g_score[neighbor_tuple]:
                    came_from[neighbor_tuple] = current
                    g_score[neighbor_tuple] = tentative_g_score
                    f_score[neighbor_tuple] = tentative_g_score + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor_tuple], neighbor_tuple))
        print("No path", collors_allowed, start, end)
        return [list(start)]

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def get_neighbors(node, collisions):
        height, width = collisions.shape
        y, x = node
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and collisions[ny, nx] == 0:
                neighbors.append([ny, nx])  # Keep neighbors as lists
        return neighbors
