# import arcade
# import random
#
# from pyglet.graphics import Batch
#
# # Параметры экрана
# SCREEN_WIDTH = 270
# SCREEN_HEIGHT = 360
# SCREEN_TITLE = "Сапёр"
# CELL_SIZE = 30
# GRID_WIDTH = 9
# GRID_HEIGHT = 9
#
#
# class SaperGame(arcade.Window):
#     def __init__(self, screen_width, screen_height, screen_title):
#         super().__init__(screen_width, screen_height, screen_title)
#         arcade.set_background_color(arcade.color.BLACK)
#         self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
#         self.bombs_counters = 10
#         self.bombs_location = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
#         self.next_grid = None
#         self.update_timer = 0
#         self.update_speed = 0.1
#         self.batch = Batch()
#
#     def setup(self):
#         self.fill()
#         self.fill_bombs()
#
#     def fill(self, density=0.3):
#         for row in range(GRID_HEIGHT - 60):
#             for col in range(GRID_WIDTH):
#                 self.grid[row][col] = 0
#     def fill_bombs(self):
#         for row in range(GRID_HEIGHT - 60):
#             for col in range(GRID_WIDTH):
#                 rand = random.randint(0, 1)
#                 print(rand)
#                 if self.bombs_counters != 0:
#                     if rand == 1:
#                         self.bombs_location[row][col] = 1
#                         self.bombs_counters -= 1
#         print(self.bombs_location)
#         print(self.bombs_counters)
#
#
#     def on_draw(self):
#         self.clear()
#         for row in range(GRID_HEIGHT):
#             for col in range(GRID_WIDTH):
#                 if self.grid[row][col] == 0:
#                     x = col * CELL_SIZE + CELL_SIZE // 2
#                     y = row * CELL_SIZE + CELL_SIZE // 2
#                     arcade.draw_rect_filled(arcade.rect.XYWH(x, y, CELL_SIZE - 1, CELL_SIZE - 1), arcade.color.ASH_GREY)
#         self.batch.draw()
#
#     def update_grid(self):
#         self.bombs_location = self.next_grid
#         self.grid = self.next_grid
#
#     def on_update(self, delta_time):
#         self.update_timer += delta_time
#         if self.update_timer >= self.update_speed:
#             self.update_timer = 0
#             self.update_grid()
#
#     def on_mouse_press(self, x, y, button, modifiers):
#         col = int(x // CELL_SIZE)
#         row = int(y // CELL_SIZE)
#         self.batch = Batch()
#         if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
#             if button == arcade.MOUSE_BUTTON_LEFT:
#                 if self.bombs_location[row][col] == 1:
#                     print("Сработало")
#                     self.grid[row][col] = 1 - self.grid[row][col]
#                 else:
#                     self.grid[row][col] = 1 - self.grid[row][col]
#
#     def on_key_press(self, key, modifiers):
#         pass
#
#
# def main():
#     game = SaperGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
#     game.setup()
#     arcade.run()
#
# if __name__ == "__main__":
#     main()

import arcade


# Creating MainGame class
class MainGame(arcade.Window):
    def __init__(self):
        super().__init__(600, 600, title="Player Movement")

        # Initializing the initial x and y coordinated
        self.x = 250
        self.y = 250

        # Initializing a variable to store
        # the velocity of the player
        self.vel = 300

    # Creating on_draw() function to draw on the screen
    def on_draw(self):
        arcade.start_render()

        # Drawing the rectangle using
        # draw_rectangle_filled function
        arcade.draw_rect_filled(self.x, self.y, 50, 50, arcade.color.GREEN)

    # Creating on_update function to
    # update the x coordinate
    def on_update(self, delta_time):
        self.x += self.vel * delta_time

        # Changing the direction of
        # movement if player crosses the screen
        if self.x >= 550 or self.x <= 50:
            self.vel *= -1

            # Loading the audio file
            audio = arcade.load_sound('Files/ForMario/music for mario/01. Ground Theme.mp3', False)

            # Printing "Playing Audio"
            print("Playing Audio.mp File")

            # Playing the audio
            arcade.play_sound(audio, 1.0, -1, False)


# Calling MainGame class
MainGame()
arcade.run()