import pygame
import time
import sys
from maze_solver import *

class Button:
    def __init__(self, image_path, x, y, action=None):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (150, 75))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.action = action
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_hovered(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height

    def click(self):
        if self.action is not None:
            self.action()


class MazeVisualizer:
    def __init__(self, filename):
        # Initialize Pygame
        pygame.init()
        self.input_filename = filename
        self.font = pygame.font.SysFont(None, 36)
        self.screen_width = 1400
        self.screen_height = 900
        self.block_size = 75  # Size of each block in pixels

        # Set up the Pygame window
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Ares's adventure")
        self.clock = pygame.time.Clock()

        # Load images for each block type and background
        self.background_images = self.load_background_images()
        self.background_positions = [0, 0, 0, 0, 0] 
        self.background_speeds = [0.8, 1.2, 1.4, 1.6, 1.8] 
        self.block_images = self.load_images()

        # Buttons
        self.menu_buttons = [] #always show
        self.algorithm_buttons = []
        self.map_buttons = []
        self.show_algorithm_buttons = False
        self.show_map_buttons = False
        self.create_buttons()

        # Create solvers
        self.bfs_solver = MazeSolverBFS.from_file(filename)
        self.dfs_solver = MazeSolverDFS.from_file(filename)
        self.ucs_solver = MazeSolverUCS.from_file(filename)
        self.astar_solver = MazeSolverAStar.from_file(filename)
        self.current_solver = self.bfs_solver  # Default solver
        self.is_solved = False
        self.is_paused = False
        
    def start_button_action(self):
        self.show_algorithm_buttons = False
        self.show_map_buttons = False
        self.animate_solution()
    
    def quick_start_button_action(self):
        self.show_algorithm_buttons = False
        self.show_map_buttons = False
        self.animate_solution(quick_start=True)

    def pause_button_action(self):
        self.is_paused = not self.is_paused

    def reset_button_action(self):
        self.show_algorithm_buttons = False
        self.show_map_buttons = False
        self.is_paused = False

    def exit_button_action(self):
        pygame.quit()
        sys.exit()

    def algorithm_button_action(self):
        self.show_map_buttons = False
        self.show_algorithm_buttons = not self.show_algorithm_buttons

    def map_button_action(self):
        self.show_algorithm_buttons = False
        self.show_map_buttons = not self.show_map_buttons

    def set_solver_button_action(self, solver_name):
        self.set_solver(solver_name)
        self.show_algorithm_buttons = False

    def create_buttons(self):
        self.quick_start_button = Button("image/quick_start_btn.png", 1200, 10, action=self.quick_start_button_action)
        self.start_button = Button("image/start_btn.png", 1200, 85, action=self.start_button_action)
        self.pause_button = Button("image/pause_btn.png", 1200, 160, action=self.pause_button_action)
        self.continue_button = Button("image/continue_btn.png", 1200, 160, action=self.pause_button_action)
        self.reset_button = Button("image/reset_btn.png", 1200, 235, action=self.reset_button_action)
        self.exit_button = Button("image/exit_btn.png", 1200, 460, action=self.exit_button_action)

        self.menu_buttons = [
            self.quick_start_button,
            self.start_button,
            self.reset_button,
            Button("image/algorithm_btn.png", 1200, 310, action=self.algorithm_button_action),
            Button("image/map_btn.png", 1200, 385, action=self.map_button_action),
            self.exit_button
        ]

        self.algorithm_buttons = [
            Button("image/bfs_btn.png", 1000, 10, action=lambda: self.set_solver_button_action("BFS")),
            Button("image/dfs_btn.png", 1000, 85, action=lambda: self.set_solver_button_action("DFS")),
            Button("image/ucs_btn.png", 1000, 160, action=lambda: self.set_solver_button_action("UCS")),
            Button("image/a_star_btn.png", 1000, 235, action=lambda: self.set_solver_button_action("AStar"))
        ]

        for i in range(10):
            map_button = Button(f"image/map{i + 1}_btn.png", 1000, 10 + i * 75, action=lambda i=i: self.load_map(i + 1))  # Load map from 1 to 10
            self.map_buttons.append(map_button)
        

    def load_images(self):
    # Load and resize images for each block type
        return {
            "wall": pygame.transform.scale(pygame.image.load("image/wall.png").convert_alpha(), (self.block_size, self.block_size)),
            "space": pygame.transform.scale(pygame.image.load("image/space.png").convert_alpha(), (self.block_size, self.block_size)),
            "player": pygame.transform.scale(pygame.image.load("image/player.png").convert_alpha(), (self.block_size, self.block_size)),
            "switch_click": pygame.transform.scale(pygame.image.load("image/switch_click.png").convert_alpha(), (self.block_size, self.block_size)),
            "stone_on_switch": pygame.transform.scale(pygame.image.load("image/stone_on_switch.png").convert_alpha(), (self.block_size, self.block_size)),
            "switch": pygame.transform.scale(pygame.image.load("image/switch.png").convert_alpha(), (self.block_size, self.block_size)),
            "stone": pygame.transform.scale(pygame.image.load("image/stone.png").convert_alpha(), (self.block_size, self.block_size)),
            "player_top": pygame.transform.scale(pygame.image.load("image/player_top.png").convert_alpha(), (self.block_size, self.block_size))
        }
    
    def load_background_images(self):
        return [
            pygame.transform.scale(pygame.image.load("image/plx-1.png").convert_alpha(), (self.screen_width, self.screen_height)),
            pygame.transform.scale(pygame.image.load("image/plx-2.png").convert_alpha(), (self.screen_width, self.screen_height)),
            pygame.transform.scale(pygame.image.load("image/plx-3.png").convert_alpha(), (self.screen_width, self.screen_height)),
            pygame.transform.scale(pygame.image.load("image/plx-4.png").convert_alpha(), (self.screen_width, self.screen_height)),
            pygame.transform.scale(pygame.image.load("image/plx-5.png").convert_alpha(), (self.screen_width, self.screen_height))
        ]
    
    def load_map(self, map_number):
        file_path = f"input-{map_number:02d}.txt"
        self.input_filename = file_path
        self.bfs_solver = MazeSolverBFS.from_file(file_path)
        self.dfs_solver = MazeSolverDFS.from_file(file_path)
        self.ucs_solver = MazeSolverUCS.from_file(file_path)
        self.astar_solver = MazeSolverAStar.from_file(file_path)
        self.is_solved = False  # Reset solved status
        self.current_solver = self.bfs_solver
        self.is_paused = False
        self.show_map_buttons = False
    
    def set_solver(self, solver_name):
        if solver_name == "BFS":
            self.current_solver = self.bfs_solver
        elif solver_name == "DFS":
            self.current_solver = self.dfs_solver
        elif solver_name == "UCS":
            self.current_solver = self.ucs_solver
        elif solver_name == "AStar":
            self.current_solver = self.astar_solver
        # otherwise the current_solver remains unchanged

    def draw_stone_weight(self, weight, x, y):
        weight_text = self.font.render(str(weight), True, (255, 255, 255))
        text_rect = weight_text.get_rect(center=(x * self.block_size + self.block_size // 2, y * self.block_size + self.block_size // 2))
        self.screen.blit(weight_text, text_rect)  # Draw the weight text

    def is_inside_maze(self, state, i, j):
        # check above:
        check = False
        for row in range(i - 1, -1, -1):
            if state.grid[row][j] == '#':
                check = True
                break
        if not check:
            return False
        # check below:
        check = False
        for row in range(i + 1, state.height, 1):
            if state.grid[row][j] == '#':
                check = True
                break
        if not check:
            return False
        # check left:
        check = False
        for col in range(j - 1, -1, -1):
            if state.grid[i][col] == '#':
                check = True
                break
        if not check:
            return False
        # check right:
        check = False
        for col in range(j + 1, len(state.grid[i]), 1):
            if state.grid[i][col] == '#':
                check = True
                break
        return check
    
    def draw_background(self, parallax_bg: bool = False):
        """Draw parallax background layers horizontally"""
        if parallax_bg:
            for i, bg_image in enumerate(self.background_images):
                # Calculate position based on speed
                pos = self.background_positions[i]
                self.screen.blit(bg_image, (pos, 0)) 
                self.screen.blit(bg_image, (pos - self.screen_width, 0)) 

                # Update the position for next frame, moving right
                self.background_positions[i] += self.background_speeds[i]
                if self.background_positions[i] >= self.screen_width:
                    self.background_positions[i] = 0 
        else:
            for bg_image in self.background_images:
                self.screen.blit(bg_image, (0, 0))

    def draw_grid(self, state, parallax_bg: bool = False):
        """Draw background"""
        self.draw_background(parallax_bg)
        # for bg_image in self.background_images:
        #     self.screen.blit(bg_image, (0, 0))
        """Draw wall and space"""
        for y, row in enumerate(state.grid):
            for x, cell in enumerate(row):
                if cell == '#':
                    self.screen.blit(self.block_images["wall"], (x * self.block_size, y * self.block_size))
                elif self.is_inside_maze(state, y, x):
                    self.screen.blit(self.block_images["space"], (x * self.block_size, y * self.block_size))

        """Draw the objects"""
        for y, row in enumerate(state.grid):
            for x, cell in enumerate(row):
                if cell == '@':
                    self.screen.blit(self.block_images["player"], (x * self.block_size, y * self.block_size))
                elif cell == '+':
                    self.screen.blit(self.block_images["switch_click"], (x * self.block_size, y * self.block_size))
                    self.screen.blit(self.block_images["player_top"], (x * self.block_size, y * self.block_size))
                elif cell == '*':
                    self.screen.blit(self.block_images["stone_on_switch"], (x * self.block_size, y * self.block_size))
                    self.draw_stone_weight(state.stones_weight[(y, x)], x, y)
                elif cell == '.':
                    self.screen.blit(self.block_images["switch"], (x * self.block_size, y * self.block_size))
                elif cell == '$':
                    self.screen.blit(self.block_images["stone"], (x * self.block_size, y * self.block_size))
                    self.draw_stone_weight(state.stones_weight[(y, x)], x, y)

    def show_error_message(self, message):
        """Draw message on the screen."""
        text = self.font.render(message, True, (255, 0, 0))  # Red text
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        pygame.draw.rect(self.screen, (255, 255, 255), text_rect)
        self.screen.blit(text, text_rect)
        pygame.display.flip()
    
    def draw_solving_text(self):
        """Draw 'solving...' message on the screen."""
        solving_text = self.font.render("Solving...", True, (255, 255, 255))  # White text
        # text_rect = solving_text.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(solving_text, (10,750))  # Draw the solving text
        pygame.display.flip()

    def solve_and_save_output(self):
        """Solve the maze"""
        if not self.is_solved:
            self.draw_solving_text()
            if not self.astar_solver.solve_and_track_memory():
                self.show_error_message("The maze is not solvable!")
                return
            self.bfs_solver.solve_and_track_memory()
            self.dfs_solver.solve_and_track_memory()
            self.ucs_solver.solve_and_track_memory()
            self.grid = self.current_solver.initial_state.grid
            self.is_solved = True
        
        """Save output to file"""
        output_filename = "output-" + self.input_filename[6:]
        with open(output_filename, 'w', encoding='utf-8') as file:
            for (algo, solver) in (("BFS", self.bfs_solver),
                                   ("DFS", self.dfs_solver),
                                   ("UCS", self.ucs_solver),
                                   ("A*", self.astar_solver)):
                file.write(algo + "\n")
                file.write(f"Steps: {len(solver.path) - 1}, "\
                       f"Weight: {solver.cost}, "\
                       f"Node: {solver.state_visited}, "\
                       f"Time (ms): {solver.time_consume:.2f}, "\
                       f"Memory (MB): {solver.memory_consume:.2f}\n")
                file.write(solver.str_path + "\n")

    def solve(self):
        if not self.is_solved:
            self.draw_solving_text()
            if not self.astar_solver.solve_maze():
                self.show_error_message("The maze is not solvable!")
                return
        self.current_solver = self.astar_solver

    def animate_solution(self, quick_start=False):
        if quick_start == False and self.is_solved == False:
            self.solve_and_save_output()
        elif quick_start:
            self.solve()
        """Animate each step of the solution path."""
        weight_pushed = 0
        i = len(self.current_solver.path) - 1
        while (i >= 0):
            # Event handling to allow quitting the application
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_button_action()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if self.pause_button.is_hovered():
                        self.pause_button.click()
                    elif self.reset_button.is_hovered():
                        self.reset_button.click()
                        return
                    elif self.exit_button.is_hovered():
                        self.exit_button.click()

            if self.is_paused:
                self.continue_button.draw(self.screen)
                pygame.display.flip()
                time.sleep(0.1)
                continue

            state = self.current_solver.path[i]
            if i < len(self.current_solver.path) - 1:
                weight_pushed += MazeSolver.step_cost(self.current_solver.path[i + 1], self.current_solver.path[i])
            # Draw the current state of the grid
            self.screen.fill((0, 0, 0))
            self.draw_grid(state)
            self.draw_buttons()

            # Write statistic
            step_text = self.font.render(f"Step: {len(self.current_solver.path) - 1 - i}", True, (255, 255, 255))  # White color
            self.screen.blit(step_text, (10, 800))
            weight_text = self.font.render(f"Weight pushed: {weight_pushed}", True, (255, 255, 255)) 
            self.screen.blit(weight_text, (10, 850))
            
            # Display SOLVED text for both quickstart and normal mode when solution is found
            if i == 0 and (self.is_solved or quick_start):
                solved_text = self.font.render("SOLVED", True, (0, 255, 0))  
                self.screen.blit(solved_text, (10, 750))

            
            pygame.display.flip()  # Update the display

            time.sleep(0.17)  # Adjust delay for animation speed
            self.clock.tick(60)  # Limit to 60 frames per second
            i -= 1
        
        # After animation, keep screen until user do something
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_button_action()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if quick_start and self.quick_start_button.is_hovered():
                        self.quick_start_button.click()
                        return
                    if quick_start == False and self.start_button.is_hovered():
                        self.start_button.click()
                        return
                    if self.reset_button.is_hovered():
                        self.reset_button.click()
                        return
                    if self.exit_button.is_hovered():
                        self.exit_button.click()
                        return
    
    def draw_buttons(self):
        for button in self.menu_buttons:
            button.draw(self.screen)
        self.pause_button.draw(self.screen)
        if self.show_algorithm_buttons == True:
            for button in self.algorithm_buttons:
                button.draw(self.screen)
        if self.show_map_buttons == True:
            for button in self.map_buttons:
                button.draw(self.screen)

    def run(self):
        """Run the main loop of the application."""
        running = True
        while running:
            self.draw_grid(self.current_solver.initial_state, parallax_bg = True)
            self.draw_buttons()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                # Check for mouse button clicks on buttons
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    for button in self.menu_buttons:
                        if button.is_hovered():
                            button.click()

                    if self.show_algorithm_buttons == True:
                        for button in self.algorithm_buttons:
                            if button.is_hovered():
                                button.click()
                    if self.show_map_buttons == True:
                        for button in self.map_buttons:
                            if button.is_hovered():
                                button.click()
                        
            self.clock.tick(60)  # Maintain frame rate

        self.exit_button_action()

# Example usage
if __name__ == "__main__":
    visualizer = MazeVisualizer("input-01.txt")
    visualizer.run()
