import arcade
from arcade import Sound
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
MAX_JUMPS = 1
JUMP_SPEED = 8
JUMP_POWER_INCREMENT = 1
JUMP_BUFFER = 0.5
UPDATES_PER_FRAME = 4
MIN_JUMP_SPEED = 6

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.face_right = True
        stop = arcade.load_texture("Files/ForMario/Картинки/StopMario.png")
        self.idle_textures = [stop, stop.flip_left_right()]
        self.jump = arcade.load_texture("Files/ForMario/Картинки/JumpMario.png")
        self.walk_textures = []
        for i in range(1, 4):
            walk = arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png")
            self.walk_textures.append([walk, walk.flip_left_right()])
        self.cur_frame = 0
        self.texture = self.idle_textures[0]

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x > 0:
            self.face_right = True
        elif self.change_x < 0:
            self.face_right = False

        idx = 0 if self.face_right else 1

        # СОСТОЯНИЕ: Прыжок (если мы не на земле)
        # В Arcade change_y != 0 значит, что мы либо летим, либо падаем
        if abs(self.change_y) > 0.1:
            self.texture = self.jump
            return

        # СОСТОЯНИЕ: Покой
        if abs(self.change_x) < 0.1:
            self.texture = self.idle_textures[idx]
            return

        # СОСТОЯНИЕ: Бег
        self.cur_frame += 1
        frame_index = self.cur_frame // 10
        if frame_index < len(self.walk_textures):
            self.texture = self.walk_textures[frame_index][idx]
        else:
            self.cur_frame = 0

class SuperMario(arcade.Window):
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
        self.player_list.append(self.player)
        self.left = self.right = self.up = self.down = False
        self.go_to_tubes = False

        #Загрузка спрайтой
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.tubes_list = self.tile_map.sprite_lists["ExitTubes"]
        self.wall_list1 = self.tile_map.sprite_lists["Under Walls"]
        self.tubes = self.tile_map.sprite_lists["Tubes"]
        self.nothing = self.tile_map.sprite_lists["fall"]
        self.coin_list = self.tile_map.sprite_lists["Coins"]

        #Начальное положение игрока
        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300

        #Музыка и звуки
        self.player_music = self.music.play(volume=1)

        #Движки для прыжков
        self.engine = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.wall_list)
        self.engine1 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.wall_list1)
        self.engine2 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, walls=self.tubes)

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
        move = 0
        #Движение
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move

        #Движки для прыжков обновляются
        self.engine.update()
        self.engine1.update()
        self.engine2.update()

        #Колизии игрока и предметов
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.coins += 1
        is_death = arcade.check_for_collision(self.player, self.nothing[0]) + arcade.check_for_collision(self.player, self.nothing[1])
        if is_death:
            self.player.center_x = CELL_SIZE * 1
            self.player.center_y = CELL_SIZE * 2
        is_collision = arcade.check_for_collision(self.player, self.tubes_list[0]) + arcade.check_for_collision(self.player, self.tubes_list[1])
        if is_collision and self.go_to_tubes:
            self.player.center_x = CELL_SIZE * 49.5
            self.player.center_y = CELL_SIZE * 13.5
            self.go_to_tubes = False
        is_collision1 = arcade.check_for_collision(self.player, self.tubes_list[3]) + arcade.check_for_collision(self.player, self.tubes_list[2])
        if is_collision1 and self.go_to_tubes:
            self.player.center_x = CELL_SIZE * 164
            self.player.center_y = CELL_SIZE * 20.5
            self.go_to_tubes = False

        #Музыка и звуки
        self.player_music.play()

        #Обновление движков с взаимодействиями
        self.physics_engine.update()
        self.physics_engine1.update()
        self.physics_engine2.update()

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
        world_h = 35 * 16
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
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down = True
            self.go_to_tubes = True
        elif key == arcade.key.SPACE:
            if self.engine.can_jump() or self.engine1.can_jump() or self.engine2.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            if self.player.change_y > MIN_JUMP_SPEED:
                self.player.change_y = MIN_JUMP_SPEED


def main():
    game = SuperMario(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()