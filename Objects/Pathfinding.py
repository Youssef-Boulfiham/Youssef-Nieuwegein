import heapq

import numpy as np
from PIL import Image


class AStar:
    def __init__(self):
        pass

    def search_path(self, start, goal, allowed_colors):
        # get collisions
        self.get_collision_layer(allowed_colors)
        collisions = np.loadtxt(f"{allowed_colors}.txt", dtype=int)

        open_set = []
        heapq.heappush(open_set, (0, tuple(start)))  # Convert start to tuple
        came_from = {}
        g_score = {tuple(start): 0}  # Convert start to tuple
        f_score = {tuple(start): self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == tuple(goal):  # Ensure goal comparison matches tuple
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
                    f_score[neighbor_tuple] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor_tuple], neighbor_tuple))

        print("No path")
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

    @staticmethod
    def get_collision_layer(allowed_colors):
        """
        "blue": (30, 49, 227),
        "black": (0, 0, 0),
        "grey": (128, 128, 128),
        "green": (41, 161, 39),
        "brown": (143, 110, 26)
        """
        colors = {
            "blue": (0, 0, 255),
            "black": (0, 0, 0),
            "grey": (128, 128, 128),
            "green": (41, 161, 39),
            "brown": (143, 110, 26),
            "red": (255, 0, 0),
            "red dark": (155, 0, 0)
        }
        allowed_colors_rgb = [colors[color] for color in allowed_colors]
        image = Image.open(
            "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/graphics/enviroment_activity.png").convert(
            "RGB")
        width, height = image.size
        pixels = image.load()
        collision_layer = np.zeros((height, width), dtype=int)
        for y in range(height):
            for x in range(width):
                if pixels[x, y] not in allowed_colors_rgb:
                    collision_layer[y, x] = 1  # Block the color
        np.savetxt(f"{allowed_colors}.txt", collision_layer, fmt='%d')
