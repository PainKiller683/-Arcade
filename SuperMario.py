import arcade
from Mario import Player
from arcade import Sound
# from Block import My_Blocks
import arcade.gui
from arcade.examples.camera_platform import JUMP_SPEED
from arcade.gui import UIManager
import random

# Параметры экрана
CAMERA_LERP = 0.14
SCREEN_WIDTH = 32 * 16
SCREEN_HEIGHT = 29 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
MOVE_SPEED = 0.5
GRAVITY = 0.4
PLAYER_GRAVITY = 1
JUMP_SPEED = 10
MIN_JUMP_SPEED = 5

class Mainwindow(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        super().__init__(screen_width, screen_height, screen_title)
        self.player_list = None
        self.player = None
        self.animation_speed = 10
        self.frame_counter = 0
        self.coins = 0
        self.world_camera = arcade.camera.Camera2D()
        arcade.set_background_color(arcade.color.BLACK)
        self.all_sprites = arcade.SpriteList()
        self.music = arcade.load_sound("Files/ForMario/music for mario/01. Ground Theme.mp3", False)
        self.tile_map = arcade.load_tilemap("Files/ForMario/Тайлы/World 1.1 SuperMario.tmx", scaling=1)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def setup(self):
        #Игрок и его данные
        self.player_list = arcade.SpriteList()
        self.player = Player()
        # self.blocks = My_Blocks()
        self.player_list.append(self.player)
        self.left = self.right = self.up = self.down = False
        self.go_to_tubes_down = False
        self.go_to_tubes_right = False

        #Загрузка спрайтой
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.tubes_list = self.tile_map.sprite_lists["ExitTubes"]
        self.wall_list1 = self.tile_map.sprite_lists["Under Walls"]
        self.tubes = self.tile_map.sprite_lists["Tubes"]
        self.nothing = self.tile_map.sprite_lists["Nothing"]
        self.fall = self.tile_map.sprite_lists["fall"]
        self.coin_list = self.tile_map.sprite_lists["Coins"]
        self.funct_tubes = self.tile_map.sprite_lists["ExitTubes"]

        #Начальное положение игрока
        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300

        #Музыка и звуки
        self.player_music = self.music.play(volume=1)

        #Движки для прыжков
        self.engine = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=PLAYER_GRAVITY, walls=self.wall_list)
        self.engine1 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=PLAYER_GRAVITY, walls=self.wall_list1)
        self.engine2 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=PLAYER_GRAVITY, walls=self.tubes)
        self.engine3 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=PLAYER_GRAVITY,walls=self.funct_tubes)

        #Движки для взаимодействия(ударов)
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
        self.player_list.draw()

    def on_update(self, delta_time):
        #Обновление игрока
        self.physics_engine.update()
        self.player.update_animation(delta_time)
        #Движение
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move

        #Движки для прыжков обновляются
        self.engine.update()
        self.engine1.update()
        self.engine2.update()
        self.engine3.update()

        #Колизии игрока и предметов
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.coins += 1
        for i in self.nothing:
            is_death = arcade.check_for_collision(self.player, i)
            if is_death:
                self.player.center_x = CELL_SIZE * 8
                self.player.center_y = 300
        is_collision = arcade.check_for_collision(self.player, self.tubes_list[0]) + arcade.check_for_collision(self.player, self.tubes_list[1])
        # if arcade.check_for_collision_with_list(self.blocks):
        #     self.blocks.center_y += self.blocks.bump_speed
        #     if self.blocks.center_y > self.blocks.original_y + 10:
        #         self.blocks.bump_speed = -5
        #     if self.blocks.center_y <= self.blocks.original_y:
        #         self.blocks.center_y = self.blocks.original_y
        #         self.blocks.is_bumping = False
        #         self.blocks.bump_speed = 5
        if is_collision and self.go_to_tubes_down:
            self.player.center_x = CELL_SIZE * 49.5
            self.player.center_y = CELL_SIZE * 13.5
            self.go_to_tubes_down = False
        is_collision1 = arcade.check_for_collision(self.player, self.tubes_list[3]) + arcade.check_for_collision(self.player, self.tubes_list[2])
        if is_collision1 and self.go_to_tubes_right:
            self.player.center_x = CELL_SIZE * 164
            self.player.center_y = CELL_SIZE * 20.5
            self.go_to_tubes_right = False
        self.go_to_tubes_down = False
        self.go_to_tubes_right = False

        #Музыка и звуки
        self.player_music.play()

        #Обновление движков с взаимодействиями
        self.physics_engine.update()
        self.physics_engine1.update()
        self.physics_engine2.update()
        # self.blocks.update()

        #Все что нужно для камеры
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
        world_h = 30 * 16
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_w, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        #Уменьшить скорость прыжка и менять картинку
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right = True
            self.go_to_tubes_right = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down = True
            self.go_to_tubes_down = True
        elif key == arcade.key.SPACE:
            if self.engine.can_jump() or self.engine1.can_jump() or self.engine2.can_jump() or self.engine3.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
            self.go_to_tubes_right = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
            self.go_to_tubes_right = False
        elif key == arcade.key.SPACE:
            if self.player.change_y > MIN_JUMP_SPEED:
                self.player.change_y = MIN_JUMP_SPEED


def main():
    game = Mainwindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()