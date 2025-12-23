import arcade
import random

from pyglet.graphics import Batch

# Параметры экрана
SCREEN_WIDTH = 3376
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 30
GRID_WIDTH = 9
GRID_HEIGHT = 9


class SaperGame(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        super().__init__(screen_width, screen_height, screen_title)
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.all_sprites = arcade.SpriteList()
        self.player_texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png")
        self.texture = arcade.load_texture("For BackGrounds/NES - Super Mario Bros. - Stages - World 1-1.png")
        self.player = arcade.Sprite(self.player_texture, scale=0.5)
        y = 480
        x = 50
        self.player.center_x = x
        self.player.center_y = y
        self.all_sprites.append(self.player)

    def setup(self):
        self.fill()

    def fill(self, density=0.3):
        pass

    def on_draw(self):
        self.world_camera.use()
        self.all_sprites.draw()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))

    def on_update(self, delta_time):
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            0.14,
        )

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 5
        elif key == arcade.key.DOWN:
            self.player.change_y = -5
        elif key == arcade.key.LEFT:
            self.player.change_x = -5
        elif key == arcade.key.RIGHT:
            self.player.change_x = 5

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or arcade.key.RIGHT:
            self.player.change_x = 0


def main():
    game = SaperGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()