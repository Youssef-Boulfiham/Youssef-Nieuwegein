import time
import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 300, 300  # Updated window size
CURSOR_SIZE = 10  # Cursor size in pixels
CURSOR_STEP = 10  # Cursor movement step size
BG_COLOR = (30, 30, 30)
BG_IMAGE = pygame.image.load("graphics/enviroment_easy.png")
walls = [[32, 80], [64, 64], [96, 48], [129, 32], [160, 48], [192, 64], [224, 80], [256, 96], [32, 112], [64, 128], [256, 128], [224, 144], [192, 160], [160, 176], [128, 160]]

# Map
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Omgeving Simulatie")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Camera Class
class Camera:
    def __init__(self):
        self.zoom = 1.0  # Camera zoom level (default 1)
        self.zoom_levels = [1.0, 2.0, 4.0]  # Defined zoom levels
        self.offset = [0, 0]  # Camera offset [x, y]
        self.cursor_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2]  # Cursor starts in center

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

# Layer Class
class Layer:
    def __init__(self, camera):
        self.camera = camera

    def draw_background(self):
        """Draw the background image scaled with zoom."""
        scaled_bg = pygame.transform.scale(
            pygame.image.load("graphics/enviroment_easy.png"),
            (int(WINDOW_WIDTH * self.camera.zoom), int(WINDOW_HEIGHT * self.camera.zoom))
        )
        bg_x = -self.camera.offset[0]
        bg_y = -self.camera.offset[1]
        screen.blit(scaled_bg, (bg_x, bg_y))

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



class Player:
    def __init__(self, x, y, camera, speed, walls):
        self.image = pygame.image.load("graphics/Agent_front.png").convert_alpha()
        self.x = x  # Lower middle x-coordinate (adjusted)
        self.y = y  # Lower middle y-coordinate (adjusted)
        self.camera = camera
        self.speed = speed
        self.last_move_time = time.time()  # Initialize the last move time
        self.walls = walls  # List of wall coordinates

        self.original_width = self.image.get_width()  # Original width of the agent image
        self.original_height = self.image.get_height()  # Original height of the agent image

    def wander(self):
        """Move the agent randomly, respecting walls and staying within bounds, with step size."""
        current_time = time.time()
        if current_time - self.last_move_time >= 1:  # 1-second interval
            self.last_move_time = current_time  # Update the last move time

            # Define the step sizes for x and y
            step_x = 32  # 32 pixels for horizontal movement
            step_y = 16  # 16 pixels for vertical movement

            # Randomly pick a direction that moves both x and y
            # Possible movements: Right-down, Left-down, Right-up, Left-up
            directions = [(step_x, step_y), (-step_x, step_y), (step_x, -step_y), (-step_x, -step_y)]
            random.shuffle(directions)  # Shuffle to try different directions randomly

            for dx, dy in directions:
                new_x = self.x + dx
                new_y = self.y + dy

                # Check if the new position is within bounds
                if 0 <= new_x <= 300 and 0 <= new_y <= 300:
                    # Check if the new position collides with a wall
                    if [new_x, new_y] not in self.walls:
                        self.x = new_x
                        self.y = new_y
                        break  # Exit the loop once a valid move is found
                    else:
                        # If the new position is blocked by a wall, print for debugging
                        print(f"Blocked at {new_x}, {new_y}")
            print(self.x, self.y)

    def draw(self):
        """Draw the player, scaling the image based on the zoom level."""
        scale_factor = self.camera.zoom  # Get current zoom level
        # Calculate the position based on zoom, camera offset, and lower middle alignment
        # The center of the image is at (x, y), we calculate the position accordingly
        x_pos = (self.x - self.original_width // 2) * scale_factor - self.camera.offset[0]
        y_pos = (self.y - self.original_height) * scale_factor - self.camera.offset[1]

        # Scale the agent image according to the zoom level
        scaled_image = pygame.transform.scale(self.image,
                                              (int(self.original_width * scale_factor),
                                               int(self.original_height * scale_factor)))

        # Blit the scaled agent image to the screen
        screen.blit(scaled_image, (x_pos, y_pos))



# Main Game Loop
camera = Camera()
layer = Layer(camera)
player = Player(96, 80, camera, 32, walls)
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

    # Zoom in/out
    if keys[pygame.K_1]:
        camera.zoom_out()
    if keys[pygame.K_2]:
        camera.zoom_in()

    # Draw Layers
    layer.draw_background()
    layer.draw_cursor()

    player.wander()
    player.draw()

    # Update Display
    pygame.display.flip()
    clock.tick(30)

# Quit pygame
pygame.quit()
sys.exit()
