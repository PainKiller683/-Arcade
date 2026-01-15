import arcade
from arcade import Sound
import random

from pyglet.graphics import Batch

# Параметры экрана
CAMERA_LERP = 0.14
SCREEN_WIDTH = 16 * 16
SCREEN_HEIGHT = 464 - 15 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
MOVE_SPEED = 1
GRAVITY = 1
MAX_JUMPS = 3
COYOTE_TIME = 0.08
JUMP_SPEED = 2
JUMP_POWER_INCREMENT = 1
JUMP_BUFFER = 0.5

# Инициализация

class SuperMario(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
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
        self.engine = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.wall_list)
        self.engine1 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.wall_list1)
        self.engine2 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.tubes)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list)
        self.physics_engine1 = arcade.PhysicsEngineSimple(
            self.player, self.wall_list1)
        self.physics_engine2 = arcade.PhysicsEngineSimple(
            self.player, self.tubes)
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_left = 1
        self.jump_buffer_timer = 5.0
        self.time_since_ground = 999.0
        self.go_to_tubes = False

    def on_draw(self):
        self.world_camera.use()
        self.scene.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time):
        move = 0
        self.update_jump_power()
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move
        grounded = self.engine.can_jump(y_distance=6)
        if grounded:
            self.time_since_ground = 0
            self.jump_left = MAX_JUMPS
        else:
            self.time_since_ground += delta_time
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= delta_time
        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)
        if want_jump:
            can_coyte = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyte:
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0
        self.engine.update()
        self.engine1.update()
        self.engine2.update()
        is_collision = arcade.check_for_collision(self.player, self.tubes_list[0]) + arcade.check_for_collision(self.player, self.tubes_list[1])
        if is_collision and self.go_to_tubes:
            self.player.center_x = CELL_SIZE * 49.5
            self.player.center_y = CELL_SIZE * 13.5
        is_collision1 = arcade.check_for_collision(self.player, self.tubes_list[3]) + arcade.check_for_collision(self.player, self.tubes_list[2])
        if is_collision1 and self.go_to_tubes:
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
        cx, cy = self.world_camera.position
        smooth = (cx + (position[0] - cx) * CAMERA_LERP,
                  cy + (position[1] - cy) * CAMERA_LERP)
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        world_w = 3360
        world_h = 464
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_w, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)

    def update_jump_power(self):
        global JUMP_SPEED
        if self.jump_pressed:
            JUMP_SPEED += JUMP_POWER_INCREMENT
            if JUMP_SPEED > 5:
                JUMP_SPEED = 5
        else:
            if JUMP_SPEED > 0:
                JUMP_SPEED -= 1

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
            self.go_to_tubes = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False


def main():
    game = SuperMario(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()