import arcade
from arcade import Sound
import random

from pyglet.graphics import Batch

# Параметры экрана
SCREEN_WIDTH = 16 * 16
SCREEN_HEIGHT = 464 - 15 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)

class KeyboardState:
    def __init__(self):
        self.keys = {} # Словарь для хранения состояния клавиш

    def pressed(self, key):
        return self.keys.get(key, False)

    def set_pressed(self, key, pressed):
        self.keys[key] = pressed

# Инициализация
keyboard = KeyboardState()

class SuperMario(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        self.keyboard = keyboard
        super().__init__(screen_width, screen_height, screen_title)
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.all_sprites = arcade.SpriteList()
        self.music = arcade.load_sound("Files/ForMario/music for mario/01. Ground Theme.mp3", False)
        self.player_texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png")
        self.player = arcade.Sprite(self.player_texture, scale=0.2)
        self.tile_map = arcade.load_tilemap("Files/ForMario/World 1.1 SuperMario.tmx", scaling=1)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def setup(self):
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.tubes_list = self.tile_map.sprite_lists["ExitTubes"]
        self.wall_list1 = self.tile_map.sprite_lists["Under Walls"]
        self.tubes = self.tile_map.sprite_lists["Tubes"]
        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300
        self.player_music = self.music.play(volume=1)
        self.all_sprites.append(self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list)
        self.physics_engine1 = arcade.PhysicsEngineSimple(
            self.player, self.wall_list1)
        self.physics_engine2 = arcade.PhysicsEngineSimple(
            self.player, self.tubes)

    def on_draw(self):
        self.world_camera.use()
        self.scene.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time):
        is_collision = arcade.check_for_collision(self.player, self.tubes_list[0]) + arcade.check_for_collision(self.player, self.tubes_list[1])
        if is_collision:
            self.player.center_x = CELL_SIZE * 49.5
            self.player.center_y = CELL_SIZE * 13.5
        is_collision1 = arcade.check_for_collision(self.player, self.tubes_list[3]) + arcade.check_for_collision(self.player, self.tubes_list[2])
        if is_collision1:
            self.player.center_x = CELL_SIZE * 164
            self.player.center_y = CELL_SIZE * 20.5
        self.player_music.play()
        self.physics_engine.update()
        self.physics_engine1.update()
        self.physics_engine2.update()
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, position, 0.14,)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 2
        elif key == arcade.key.DOWN:
            self.player.change_y = -2
        elif key == arcade.key.LEFT:
            self.player.change_x = -2
        elif key == arcade.key.RIGHT:
            self.player.change_x = 2
        # self.keyboard.set_pressed(key, True)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or arcade.key.RIGHT:
            self.player.change_x = 0


def main():
    game = SuperMario(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()