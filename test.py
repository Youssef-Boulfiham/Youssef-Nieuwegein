import pygame

class PygameApp:
    def __init__(self, width=800, height=600, caption="Single Window App"):
        """
        Initializes the Pygame application.

        Args:
            width (int): The width of the Pygame window.
            height (int): The height of the Pygame window.
            caption (str): The caption for the Pygame window.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.Font(None, 48)  # Default font, adjust size as needed
        self.small_font = pygame.font.Font(None, 36)

        self.input1 = ""
        self.input2 = ""
        self.active_input = 1  # 1 for input1, 2 for input2

        # --- Game States ---
        # 0: Input Screen
        # 1: Display Screen
        self.current_state = 0

    def _handle_input_screen_event(self, event):
        """Handles events specifically for the input screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.active_input == 1:
                    self.active_input = 2  # Switch to input2
                else:
                    # Both inputs entered, switch to display screen
                    self.current_state = 1
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == 1:
                    self.input1 = self.input1[:-1]
                else:
                    self.input2 = self.input2[:-1]
            else:
                if self.active_input == 1:
                    self.input1 += event.unicode
                else:
                    self.input2 += event.unicode

    def _handle_display_screen_event(self, event):
        """Handles events specifically for the display screen (e.g., exit)."""
        # For this simple example, we don't have interactive elements on the display screen,
        # but you could add buttons or other actions here.
        pass

    def _draw_input_screen(self):
        """Draws the elements for the input screen."""
        self.screen.fill((0, 0, 0))  # Black background

        # Input 1 prompt and text box
        text_surface1 = self.font.render("Enter Input 1:", True, (255, 255, 255))
        self.screen.blit(text_surface1, (50, 100))
        input_rect1 = pygame.Rect(50, 150, 700, 50)
        pygame.draw.rect(self.screen, (50, 50, 50), input_rect1)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect1, 2) # Border
        input_text_surface1 = self.font.render(self.input1, True, (255, 255, 255))
        self.screen.blit(input_text_surface1, (input_rect1.x + 5, input_rect1.y + 5))
        if self.active_input == 1:
            pygame.draw.rect(self.screen, (0, 255, 0), input_rect1, 4) # Green highlight for active input

        # Input 2 prompt and text box
        text_surface2 = self.font.render("Enter Input 2:", True, (255, 255, 255))
        self.screen.blit(text_surface2, (50, 250))
        input_rect2 = pygame.Rect(50, 300, 700, 50)
        pygame.draw.rect(self.screen, (50, 50, 50), input_rect2)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect2, 2) # Border
        input_text_surface2 = self.font.render(self.input2, True, (255, 255, 255))
        self.screen.blit(input_text_surface2, (input_rect2.x + 5, input_rect2.y + 5))
        if self.active_input == 2:
            pygame.draw.rect(self.screen, (0, 255, 0), input_rect2, 4) # Green highlight for active input

        # Instructions
        instruction_text = self.small_font.render("Press ENTER to switch fields or submit", True, (150, 150, 150))
        self.screen.blit(instruction_text, (50, 400))


    def _draw_display_screen(self):
        """Draws the elements for the display screen."""
        self.screen.fill((0, 50, 0))  # Dark green background

        # Display Input 1
        display_text1 = self.font.render(f"Input 1: {self.input1}", True, (255, 255, 255))
        self.screen.blit(display_text1, (50, 100))

        # Display Input 2
        display_text2 = self.font.render(f"Input 2: {self.input2}", True, (255, 255, 255))
        self.screen.blit(display_text2, (50, 200))

        # Optional: Instruction to quit
        quit_instruction = self.small_font.render("Press ESC to quit", True, (150, 150, 150))
        self.screen.blit(quit_instruction, (50, 500))


    def run(self):
        """
        The main game loop. This is the single while loop for the application.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # Allow ESC to quit from anywhere
                        self.running = False

                # Delegate event handling based on the current state
                if self.current_state == 0:
                    self._handle_input_screen_event(event)
                elif self.current_state == 1:
                    self._handle_display_screen_event(event)

            # Drawing based on the current state
            if self.current_state == 0:
                self._draw_input_screen()
            elif self.current_state == 1:
                self._draw_display_screen()

            pygame.display.flip()  # Update the full display Surface to the screen
            self.clock.tick(60)  # Limit frame rate to 60 FPS

        pygame.quit() # Clean up Pygame resources when the loop exits

if __name__ == "__main__":
    app = PygameApp()
    app.run()