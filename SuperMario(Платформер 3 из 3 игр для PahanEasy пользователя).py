import arcade
from arcade import Sound
import arcade.gui
from arcade.gui import UIManager
import random

# Параметры экрана
CAMERA_LERP = 0.14
SCREEN_WIDTH = 32 * 16
SCREEN_HEIGHT = 29 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
MOVE_SPEED = 0.5
GRAVITY = 1
MAX_JUMPS = 1
COYOTE_TIME = 0.08
JUMP_SPEED = 0
JUMP_POWER_INCREMENT = 1
JUMP_BUFFER = 0.5
UPDATES_PER_FRAME = 4

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = 0
        self.img = arcade.load_texture("Files/ForMario/Картинки/StopMario.png", flipped_horizontally=True)
        self.walk_textures = []
        for i in range(1, 4):
            self.walk_textures.append(arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png"))
            r = arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png")
            l = arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png", flipped_horizontally=True)
            self.walk_textures.append([r, l])
        self.cur_frame = 0
        self.texture = self.stop_texture

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0 and self.character_face_direction == 0:
            self.character_face_direction = 1  # Повернулся влево
        elif self.change_x > 0 and self.character_face_direction == 1:
            self.character_face_direction = 0  # Повернулся вправо

            # ЕСЛИ ПЕРСОНАЖ СТОИТ
        if self.change_x == 0:
            # Показываем картинку "стоит" в текущем направлении
            self.texture = self.stop_texture[self.character_face_direction]
            return

            # ЕСЛИ ПЕРСОНАЖ БЕЖИТ (АНИМАЦИЯ)
        self.cur_frame += 1

        # Зацикливаем 4 кадра
        # Умножаем на UPDATES_PER_FRAME, чтобы замедлить смену картинок
        if self.cur_frame > 3 * UPDATES_PER_FRAME:
            self.cur_frame = 0

        # Вычисляем индекс текущего кадра (0, 1, 2 или 3)
        frame_index = self.cur_frame // UPDATES_PER_FRAME

        # Устанавливаем текстуру: [номер_кадра][направление]
        self.texture = self.walk_textures[frame_index][self.character_face_direction]

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
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.player_list.append(self.player)
        self.player.velocity_y = 0
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.tubes_list = self.tile_map.sprite_lists["ExitTubes"]
        self.wall_list1 = self.tile_map.sprite_lists["Under Walls"]
        self.tubes = self.tile_map.sprite_lists["Tubes"]
        self.nothing = self.tile_map.sprite_lists["fall"]
        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300
        self.player_music = self.music.play(volume=1)
        self.coin_list = self.tile_map.sprite_lists["Coins"]
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
        self.player_list.draw()

    def on_update(self, delta_time):
        self.player_list.update()
        self.player_list.update_animation(delta_time)
        self.player.velocity_y -= GRAVITY * delta_time
        self.player.center_y += self.player.velocity_y * delta_time
        move = 0
        #Движение
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move
        grounded = self.engine.can_jump(y_distance=1)
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
        world_h = 35 * 16
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_w, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        #Уменьшить скорость прыжка и менять картинку
        if key == arcade.key.UP or key == arcade.key.W:
            self.jump = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.player_texture = arcade.load_texture("Files/ForMario/Картинки/JumpMario.png")
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
            self.jump_pressed = False
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