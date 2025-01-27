import time
import pygame
import sys
import random
import numpy as np  # Import NumPy for easier array handling

from Objects.Player import Player


# Camera Class
class Camera:
    def __init__(self):
        self.zoom = 1.0  # Camera zoom level (default 1)
        self.zoom_levels = [1.0, 2.0, 4.0]  # Defined zoom levels
        self.offset = [0, 0]  # Camera offset [x, y]
        self.cursor_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2]  # Cursor starts in center
        self.image_player = pygame.image.load("graphics/Agent_front.png").convert_alpha()
        self.image_player_width = self.image_player.get_width()  # Original width of the agent image
        self.image_player_height = self.image_player.get_height()  # Original height of the agent image

        # Load the border data from the text file (assuming it's a space-separated text file)
        self.borders = self.load_borders("objects/array.txt")

    def load_borders(self, filename):
        """Load the borders from the array text file."""
        # Read the file and convert it into a 2D numpy array
        with open(filename, 'r') as file:
            lines = file.readlines()
            # Convert lines into a list of lists (2D array of integers)
            return np.array([list(map(int, line.split())) for line in lines])

    def move_cursor(self, dx, dy):
        """Move the cursor and adjust camera offset."""
        self.cursor_pos[0] = max(0, min(WINDOW_WIDTH - CURSOR_SIZE, self.cursor_pos[0] + dx * CURSOR_STEP))
        self.cursor_pos[1] = max(0, min(WINDOW_HEIGHT - CURSOR_SIZE, self.cursor_pos[1] + dy * CURSOR_STEP))
        self.adjust()

    def adjust(self):
        """Adjust camera offset based on cursor position."""
        self.offset[0] = self.cursor_pos[0] * self.zoom - WINDOW_WIDTH // 2 + CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - WINDOW_HEIGHT // 2 + CURSOR_SIZE // 2
        self.clamp()

    def clamp(self):
        """Ensure the camera view stays within the screen boundaries."""
        max_offset_x = max(0, WINDOW_WIDTH * self.zoom - WINDOW_WIDTH)
        self.offset[0] = max(0, min(self.offset[0], max_offset_x))

        max_offset_y = max(0, WINDOW_HEIGHT * self.zoom - WINDOW_HEIGHT)
        self.offset[1] = max(0, min(self.offset[1], max_offset_y))

    def zoom_in(self):
        """Zoom in while ensuring the cursor remains centered."""
        if self.zoom < max(self.zoom_levels):
            self.zoom = self.zoom_levels[self.zoom_levels.index(self.zoom) + 1]
            self.center_cursor()
            time.sleep(0.2)  # Small delay to prevent skipping zoom levels

    def zoom_out(self):
        """Zoom out while ensuring the cursor remains centered."""
        if self.zoom > min(self.zoom_levels):
            self.zoom = self.zoom_levels[self.zoom_levels.index(self.zoom) - 1]
            self.center_cursor()
            time.sleep(0.2)  # Small delay to prevent skipping zoom levels

    def center_cursor(self):
        """Ensure the cursor remains centered on zoom."""
        self.offset[0] = self.cursor_pos[0] * self.zoom - WINDOW_WIDTH // 2 + CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - WINDOW_HEIGHT // 2 + CURSOR_SIZE // 2
        self.clamp()

    def draw_background(self):
        """Draw the background image scaled with zoom."""
        scaled_bg = pygame.transform.scale(
            pygame.image.load("graphics/enviroment_easy.png"),
            (int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom))
        )
        bg_x = -self.offset[0]
        bg_y = -self.offset[1]
        screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_borders(self):
        """Draw the borders from the 2D array on top of the background."""
        border_color = (255, 0, 0)  # Red color for borders

        # Loop through the borders array and draw a red square for each border
        for y in range(self.borders.shape[0]):
            for x in range(self.borders.shape[1]):
                if self.borders[y, x] == 0:  # Check if it's a border cell
                    # Calculate the position on the screen based on the zoom and offset
                    screen_x = x * self.zoom - self.offset[0]
                    screen_y = y * self.zoom - self.offset[1]

                    # Draw a small square for the border
                    pygame.draw.rect(screen, border_color,
                                     (screen_x, screen_y, self.zoom, self.zoom))

    def draw_cursor(self):
        """Draw the cursor as a red dot."""
        cursor_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - CURSOR_SIZE // 2,
            WINDOW_HEIGHT // 2 - CURSOR_SIZE // 2,
            CURSOR_SIZE,
            CURSOR_SIZE
        )
        cursor_color = (255, 0, 0)
        pygame.draw.ellipse(screen, cursor_color, cursor_rect)

    def draw_player(self, player_position_next):
        """Draw the player, scaling the image based on the zoom level."""
        scale_factor = self.zoom  # Get current zoom level
        # Calculate the position based on zoom, camera offset, and lower middle alignment
        x_pos = (player_position_next[0] - self.image_player_width // 2) * scale_factor - self.offset[0]
        y_pos = (player_position_next[1] - self.image_player_height) * scale_factor - self.offset[1]

        # Scale the agent image according to the zoom level
        scaled_image = pygame.transform.scale(self.image_player,
                                              (int(self.image_player_width * scale_factor),
                                               int(self.image_player_height * scale_factor)))

        # Blit the scaled agent image to the screen
        screen.blit(scaled_image, (x_pos, y_pos))


# Main Game Loop
WINDOW_WIDTH, WINDOW_HEIGHT = 300, 300  # Updated window size
CURSOR_SIZE = 10  # Cursor size in pixels
CURSOR_STEP = 10  # Cursor movement step size
BG_COLOR = (30, 30, 30)
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
camera = Camera()
player = Player(camera)
BG_IMAGE = pygame.image.load("graphics/enviroment_easy.png")
pygame.display.set_caption("Omgeving Simulatie")
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        camera.move_cursor(0, -1)
    if keys[pygame.K_DOWN]:
        camera.move_cursor(0, 1)
    if keys[pygame.K_LEFT]:
        camera.move_cursor(-1, 0)
    if keys[pygame.K_RIGHT]:
        camera.move_cursor(1, 0)
    if keys[pygame.K_1]:
        camera.zoom_out()
    if keys[pygame.K_2]:
        camera.zoom_in()

    # Draw the background, borders, cursor, and player
    camera.draw_background()
    # camera.draw_borders()  # Draw borders layer
    camera.draw_cursor()
    player.step()
    if not player.borders[tuple(player.position_current)]:
        print(True)

    camera.draw_player(player.position_current)

    pygame.display.flip()
    clock.tick(60)
    # time.sleep(0.2)

pygame.quit()
sys.exit()
