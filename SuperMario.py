import arcade
from Mario import Player
import arcade
# from Block import My_Blocks
import arcade.gui
import arcade.gui
import random

# Параметры экрана
CAMERA_LERP = 0.14
SCREEN_WIDTH = 32 * 16
SCREEN_HEIGHT = 29 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
CELL = 16
PLAYER_SPEED = 2.3
JUMP_FORCE = 8.8
TIMER_START = 400
JUMP_MAX_FRAMES = 12
GRAVITY = 0.4         # Низкая гравитация для плавности
FRICTION = 0.05
ACCEL = 0.02    # Долгое скольжение
MAX_WALK_SPEED = 0.5  # ОЧЕНЬ медленно (всего 1.5 пикселя за тик)
MAX_RUN_SPEED = 2.5   # Максимальный бег
JUMP_START_IMPULSE = 9.5
JUMP_ADD_FORCE = 0.5


class Koopa(arcade.Sprite):
    def __init__(self, x, y):
        self.textures1 = arcade.load_texture("Files/ForMario/Картинки/koopa1.png")
        self.textures2 = arcade.load_texture("Files/ForMario/Картинки/koopa2.png")
        self.walks = [self.textures1, self.textures2]
        self.shell = arcade.load_texture("Files/ForMario/Картинки/koopa_shell.png")
        super().__init__(scale=1)
        self.center_x = x
        self.center_y = y
        self.change_x = -0.5
        self.frame = 0
        self.in_shell = False

    def update(self):
        self.center_x += self.change_x

    def update_animation(self):
        if self.in_shell:
            return
        self.frame = (self.frame + 1) % 2
        self.texture = self.walks[self.frame]

    def stomp(self):
        self.in_shell = True
        self.change_x = 0
        self.texture = self.shell

    def kick(self, direction):
        self.change_x = 5 * direction

class Goomba(arcade.Sprite):
    def __init__(self, x, y):
        self.textures1 = arcade.load_texture("Files/ForMario/Картинки/goomba1.png")
        self.textures2 = arcade.load_texture("Files/ForMario/Картинки/goomba2.png")
        self.walks = [self.textures1, self.textures2]
        super().__init__(scale=1)
        self.nums_player = 1
        self.center_x = x
        self.center_y = y
        self.change_x = -0.4
        self.frame = 0
        self.dead = False

    def update(self):
        if not self.dead:
            self.center_x += self.change_x

    def update_animation(self):
        if self.dead:
            return
        self.frame = (self.frame + 1) % 2
        self.texture = self.walks[self.frame]

    def stomp(self):
        self.dead = True
        self.change_x = 0
        self.angle = 180

class Mainwindow(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        super().__init__(screen_width, screen_height, screen_title, fixed_rate=1/60, vsync=True)
        self.left_down = False
        self.right_down = False
        self.jump_down = False
        self.b_button_down = False
        arcade.set_background_color(arcade.color.BLACK)

        self.camera = arcade.Camera2D()
        self.state = "START"
        self.level = 1
        self.player = Player()
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.timer = TIMER_START
        self.level = 1

        map_path = "Files/ForMario/Тайлы/World 1.1 SuperMario.tmx"
        map_path1 = "Files/ForMario/Тайлы/1.2.tmx"
        if self.level != 2:
            self.tilemap = arcade.load_tilemap(map_path, scaling=1)
            self.enemies = arcade.SpriteList()
            self.enemies.append(Goomba(CELL * 30, CELL * 30))
            self.enemies.append(Goomba(CELL * 60, CELL * 30))
            self.enemies.append(Koopa(CELL * 90, CELL * 30))
            self.wall_list = self.tilemap.sprite_lists["Walls"]
            self.tubes_list = self.tilemap.sprite_lists["ExitTubes"]
            self.wall_list1 = self.tilemap.sprite_lists["Under Walls"]
            self.tubes = self.tilemap.sprite_lists["Tubes"]
            self.nothing = self.tilemap.sprite_lists["Nothing"]
            self.fall = self.tilemap.sprite_lists["fall"]
            self.coin_list = self.tilemap.sprite_lists["Coins"]
            self.music = arcade.load_sound("Files/ForMario/music for mario/01. Ground Theme.mp3", False)
        else:
            self.tilemap = arcade.load_tilemap(map_path1, scaling=1)
            self.wall_list = self.tilemap.sprite_lists["walls"]
            self.tubes_list = self.tilemap.sprite_lists["exittubes"]
            self.wall_list1 = self.tilemap.sprite_lists["Under Walls"]
            self.tubes = self.tilemap.sprite_lists["tubes"]
            self.nothing = self.tilemap.sprite_lists["Nothing"]
            self.fall = self.tilemap.sprite_lists["fall"]
            self.coin_list = self.tilemap.sprite_lists["coins"]
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        self.items = arcade.SpriteList()
        self.enemies = arcade.SpriteList()

        self.player_list = None
        self.animation_speed = 10
        self.frame_counter = 0
        self.coins = 0

        self.left_down = False
        self.right_down = False
        self.jump_down = False
        self.b_button_down = False

        self.world_camera = arcade.camera.Camera2D()
        arcade.set_background_color(arcade.color.BLACK)
        self.all_sprites = arcade.SpriteList()

        self.player_list = arcade.SpriteList()
        self.jump_button_pressed = False

        self.player_list.append(self.player)
        self.left = self.right = self.up = self.down = False
        self.go_to_tubes_down = False
        self.go_to_tubes_right = False

        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300

        # Музыка и звуки
        self.player_music = self.music.play(volume=1)

        # Движки для прыжков
        self.engine = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY,
                                                     platforms=self.wall_list)
        self.engine1 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY,
                                                      platforms=self.wall_list1)
        self.engine2 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY,
                                                      platforms=self.tubes)

        # Движки для взаимодействия(ударов)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list)
        self.physics_engine1 = arcade.PhysicsEnginePlatformer(self.player, self.wall_list1)
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(self.player, self.tubes)

    def setup(self):
        #Игрок и его данные
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.jump_button_pressed = False

        # self.blocks = My_Blocks()
        self.player_list.append(self.player)
        self.go_to_tubes_down = False
        self.go_to_tubes_right = False

        #Загрузка спрайтой

        #Начальное положение игрока
        self.player.center_x = CELL_SIZE * 8
        self.player.center_y = 300

        #Музыка и звуки
        self.player_music = self.music.play(volume=1)

        #Движки для прыжков
        self.engine = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, platforms=self.wall_list)
        self.engine1 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, platforms=self.wall_list1)
        self.engine2 = arcade.PhysicsEnginePlatformer(player_sprite=self.player, gravity_constant=GRAVITY, platforms=self.tubes)

        #Движки для взаимодействия(ударов)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list)
        self.physics_engine1 = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list1)
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player, self.tubes)

    def on_draw(self):
        self.enemies.draw()
        self.world_camera.use()
        self.scene.draw()
        self.all_sprites.draw()
        self.player_list.draw()

    def on_fixed_update(self, delta_time: float):
        target_max_speed = MAX_RUN_SPEED if self.b_button_down else MAX_WALK_SPEED
        if self.right_down:
            self.player.face_right = True
            if self.player.change_x < target_max_speed:
                self.player.change_x += ACCEL
        elif self.left_down:
            self.player.face_right = False
            if self.player.change_x > -target_max_speed:
                self.player.change_x -= ACCEL
        else:
            # Трение (инерция остановки)
            if self.player.change_x > FRICTION:
                self.player.change_x -= FRICTION
            elif self.player.change_x < -FRICTION:
                self.player.change_x += FRICTION
            else:
                self.player.change_x = 0

        # 2. ВЕРТИКАЛЬНОЕ ДВИЖЕНИЕ (Прыжок)
        if self.jump_down and self.player.is_jumping:
            if self.player.jump_timer < JUMP_MAX_FRAMES:
                self.player.change_y += JUMP_ADD_FORCE
                self.player.jump_timer += 1
            else:
                self.player.is_jumping = False
        if self.player.change_y < -12:
            self.player.change_y = -12

        #Обновление игрока
        self.physics_engine.update()
        self.player.update_animation(delta_time)
        #Движение

        #Движки для прыжков обновляются
        self.engine.update()
        self.engine1.update()
        self.engine2.update()

        #Колизии игрока и предметов
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.coins += 1
        hit_list = arcade.check_for_collision_with_list(self.player, self.nothing)
        if hit_list:
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
        is_collision1 = arcade.check_for_collision(self.player, self.tubes_list[3]) + arcade.check_for_collision(self.player, self.tubes_list[2])
        if is_collision1 and self.go_to_tubes_right:
            self.player.center_x = CELL_SIZE * 164
            self.player.center_y = CELL_SIZE * 20.5
        self.go_to_tubes_down = False
        self.go_to_tubes_right = False

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
        world_h = 30 * 16
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_w, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)

    def update(self, delta_time):
        self.engine.update(delta_time)


    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_down = True
        if key == arcade.key.RIGHT:
            self.right_down = True
        if key == arcade.key.Z:
            self.b_button_down = True
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump() or self.physics_engine1.can_jump() or self.physics_engine2.can_jump():
                self.jump_down = True
                self.player.is_jumping = True
                self.player.jump_timer = 0
                self.player.change_y = JUMP_START_IMPULSE + (abs(self.player.change_x) * 0.2)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_down = False
        if key == arcade.key.RIGHT:
            self.right_down = False
        if key == arcade.key.Z:
            self.b_button_down = False
        if key == arcade.key.SPACE:
            self.jump_down = False
            self.player.is_jumping = False


def main():
    game = Mainwindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()