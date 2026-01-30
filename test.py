import arcade
from Mario import Mario

# ==================================================
# CONSTANTS
# ==================================================
ACCEL = 0.02
MAX_RUN_SPEED = 2.5
CELL = 16
FRICTION = 0.05
GRAVITY = 0.85
PLAYER_SPEED = 2.3
JUMP_FORCE = 8.8
TIMER_START = 400
MAX_WALK_SPEED = 8.8
JUMP_MAX_FRAMES = 12
CAMERA_LERP = 0.14
SCREEN_WIDTH = 32 * 16
SCREEN_HEIGHT = 29 * 16


# ==================================================
# ENEMIES
# ==================================================

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


# ==================================================
# GAME
# ==================================================

class Game(arcade.Window):
    def __init__(self, CELL_SIZE=16):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Super Mario Bros NES")
        self.left_down = False
        self.right_down = False
        self.jump_down = False
        self.b_button_down = False
        arcade.set_background_color(arcade.color.BLACK)

        self.camera = arcade.Camera2D()
        self.state = "START"
        self.level = 1
        self.player = Mario()
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

    def setup(self, CELL_SIZE=16):
        self.player_list = arcade.SpriteList()
        self.player = Mario()
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

    # ------------------------------------------------

    def on_draw(self):
        self.clear()
        if self.state == "START":
            arcade.draw_text(
                "SUPER MARIO BROS",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 40,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )
            arcade.draw_text(
                "PRESS ENTER",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 20,
                arcade.color.WHITE,
                10,
                anchor_x="center",
            )
            return

        self.camera.use()
        self.scene.draw()
        self.items.draw()
        self.enemies.draw()
        self.all_sprites.draw()
        self.player_list.draw()
        cam_x = self.camera.position[0]
        arcade.draw_text(f"MARIO {self.score:06}", cam_x + 16, 560, arcade.color.WHITE, 8)
        arcade.draw_text(f"COIN x{self.coins:02}", cam_x + 120, 560, arcade.color.WHITE, 8)
        arcade.draw_text(f"TIME {int(self.timer)}", cam_x + 220, 560, arcade.color.WHITE, 8)

    # ------------------------------------------------

    def on_update(self, dt, JUMP_ADD_FORCE=0.5, CELL_SIZE=16):
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.coins += 1
        hit_list = arcade.check_for_collision_with_list(self.player, self.nothing)
        if hit_list:
            self.player.center_x = CELL_SIZE * 8
            self.player.center_y = 300
        is_collision = arcade.check_for_collision(self.player, self.tubes_list[0]) + arcade.check_for_collision(
            self.player, self.tubes_list[1])

        if self.state != "GAME":
            return
        self.timer -= dt
        if self.timer <= 0:
            self.player.dead = True
        if self.player.dead:
            self.lives -= 1
            if self.lives > 0:
                return
            else:
                with open("file.txt", "w") as file:
                    file.write(f"Player{self.nums_player} {self.score}")
                self.state = "START"
            return

        self.physics_engine.update()
        self.physics_engine1.update()
        self.physics_engine2.update()
        self.player.update_animation(dt)

        self.engine.update()
        self.engine1.update()
        self.engine2.update()

        self.items.update()

        for enemy in self.enemies:
            enemy.update()
            enemy.update_animation()

            if arcade.check_for_collision(self.player, enemy):
                if self.player.change_y < 0:
                    if isinstance(enemy, Koopa) and not enemy.in_shell:
                        enemy.stomp()
                    elif isinstance(enemy, Goomba):
                        enemy.stomp()
                    self.score += 100
                    self.player.change_y = 5
                else:
                    self.player.hit()

        if self.player.center_y < -CELL:
            self.player.dead = True

        cam_lock = CELL * (15 if self.level == 1 else 30)
        cam_x = max(self.player.center_x, cam_lock)
        self.camera.position = (cam_x, SCREEN_HEIGHT / 2)

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

    # ------------------------------------------------

    def on_key_press(self, key, modifiers):
        if self.state == "START" and key == arcade.key.ENTER:
            self.state = "GAME"
            self.level += 1

        if self.player.control_locked:
            return

        if key == arcade.key.LEFT:
            self.left_down = True
        if key == arcade.key.RIGHT:
            self.right_down = True
        if key == arcade.key.Z:
            self.b_button_down = True
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump() or self.physics_engine1.can_jump() or self.physics_engine2.can_jump():
                self.jump_down = True

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

    class QuestionBlock(arcade.Sprite):
        def __init__(self, x, y, content="coin"):
            super().__init__("Files/ForMario/Картинки/question.png", scale=1)
            self.center_x = x
            self.center_y = y
            self.content = content
            self.used = False

        def hit(self, game):
            if self.used:
                return
            self.used = True
            self.texture = arcade.load_texture("Files/ForMario/Картинки/empty.png")

            if self.content == "coin":
                self.update()
                game.score += 200

    class BrickBlock(arcade.Sprite):
        def __init__(self, x, y):
            super().__init__("Files/ForMario/Картинки/brick.png", scale=1)
            self.center_x = x
            self.center_y = y
            self.broken = False

        def hit(self, game):
            if self.broken:
                return

    class InvisibleBlock(arcade.Sprite):
        def __init__(self, x, y):
            super().__init__(None)
            self.center_x = x
            self.center_y = y
            self.visible = False

        def hit(self):
            if self.visible:
                return
            self.visible = True
            self.texture = arcade.load_texture("Files/ForMario/Картинки/empty.png")

    class FlagPole(arcade.Sprite):
        def __init__(self, x, y):
            super().__init__("Files/ForMario/Картинки/pole.png", scale=1)
            self.center_x = x
            self.center_y = y
            self.activated = False

        def activate(self, game):
            if self.activated:
                return
            self.activated = True
            game.player.start_flag_slide()
            game.player.control_locked = True
            game.flag_finish = True

        def handle_flag_finish(self, dt):
            if not self.flag_finish:
                return

            if self.timer > 0:
                self.timer -= dt * 5
                self.score += 50
            else:
                self.flag_finish = False
                self.load_level(self.level + 1)

    class HUD:
        def draw(self, game, cam_x):
            arcade.draw_text(
                f"MARIO {game.score:06}",
                cam_x + 16, 220, arcade.color.WHITE, 8
            )
            arcade.draw_text(
                f"COIN x{game.coins:02}",
                cam_x + 120, 220, arcade.color.WHITE, 8
            )
            arcade.draw_text(
                f"TIME {int(game.timer)}",
                cam_x + 220, 220, arcade.color.WHITE, 8
            )

    def convert_time_to_score(self):
        if self.timer <= 0:
            return False

        self.timer -= 1
        self.score += 100
        return True

    def update_camera(self):
        lock_x = 16 * (15 if self.level == 1 else 30)
        target_x = max(self.player.center_x, lock_x)
        self.camera.position = (target_x, SCREEN_HEIGHT // 2)

    class MovingPlatformDown(arcade.Sprite):
        def __init__(self, x, start_y, end_y, speed=0.6):
            super().__init__("Files/ForMario/Картинки/platform.png", scale=1)
            self.center_x = x
            self.start_y = start_y
            self.end_y = end_y
            self.center_y = start_y
            self.speed = speed

        def update(self):
            self.center_y -= self.speed
            if self.center_y <= self.end_y:
                self.center_y = self.start_y

    class MovingPlatformUp(arcade.Sprite):
        def __init__(self, x, start_y, end_y, speed=0.6):
            super().__init__("Files/ForMario/Картинки/platform.png", scale=1)
            self.center_x = x
            self.start_y = start_y
            self.end_y = end_y
            self.center_y = start_y
            self.speed = speed

        def update(self):
            self.center_y += self.speed
            if self.center_y >= self.end_y:
                self.center_y = self.start_y

    class MovingPlatformHorizontal(arcade.Sprite):
        def __init__(self, y, start_x, end_x, speed=0.8):
            super().__init__("Files/ForMario/Картинки/platform.png", scale=1)
            self.center_y = y
            self.start_x = start_x
            self.end_x = end_x
            self.center_x = start_x
            self.speed = speed
            self.direction = 1

        def update(self):
            self.center_x += self.speed * self.direction
            if self.center_x >= self.end_x or self.center_x <= self.start_x:
                self.direction *= -1

    class PlatformManager:
        def __init__(self):
            self.platforms = arcade.SpriteList()

        def add(self, platform):
            self.platforms.append(platform)

        def update(self):
            self.platforms.update()

        def draw(self):
            self.platforms.draw()

    def handle_platform_collision(player, platforms):
        collisions = arcade.check_for_collision_with_list(player, platforms)
        for platform in collisions:
            if player.change_y <= 0:
                player.bottom = platform.top
                player.change_y = 0
                player.center_x += platform.change_x if hasattr(platform, "change_x") else 0


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
