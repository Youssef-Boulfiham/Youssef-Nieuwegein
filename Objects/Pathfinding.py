import heapq
import numpy as np

class AStar:
    def __init__(self, collisions):
        self.collisions = collisions

    def search_path(self, start, end, activity):
        collisions = self.collisions[activity]

        open_set = []
        heapq.heappush(open_set, (0, tuple(start)))  # Keep original input format
        came_from = {}
        g_score = {tuple(start): 0}
        f_score = {tuple(start): self.heuristic(start, end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == tuple(end):  # Ensure end comparison works
                path = []
                while current in came_from:
                    path.append(list(current))  # Maintain original format (y, x)
                    current = came_from[current]
                path.append(list(start))
                return path[::-1]

            for neighbor in self.get_neighbors(current, collisions):
                tentative_g_score = g_score[current] + 1
                if tuple(neighbor) not in g_score or tentative_g_score < g_score[tuple(neighbor)]:
                    came_from[tuple(neighbor)] = current
                    g_score[tuple(neighbor)] = tentative_g_score
                    f_score[tuple(neighbor)] = tentative_g_score + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[tuple(neighbor)], tuple(neighbor)))

        print(f"No path: {activity}, {start}, {end}")
        return [list(start)]

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Always evaluate [0] as x, [1] as y

    @staticmethod
    def get_neighbors(node, collisions):
        height, width = collisions.shape  # Ensure correct shape ordering
        x, y = node[0], node[1]  # Always use 0 as x, 1 as y
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy  # Maintain x-first order
            if 0 <= nx < width and 0 <= ny < height and collisions[ny, nx] == 0:
                neighbors.append([nx, ny])  # Maintain lists

        return neighbors  # Ensure it always returns a list, even if empty
