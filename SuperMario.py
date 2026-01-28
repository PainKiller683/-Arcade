import arcade
from Mario import Mario

# =====================
# НАСТРОЙКИ NES
# =====================
CELL = 16
SCREEN_WIDTH = 32 * CELL
SCREEN_HEIGHT = 29 * CELL

GRAVITY = 0.9
FRICTION = 0.05
ACCEL = 0.02
MAX_WALK = 1.0
MAX_RUN = 2.5

JUMP_START = 6
JUMP_ADD = 0.5
JUMP_MAX = 8

CAMERA_LERP = 0.14

# =====================
class SuperMario(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Super Mario Bros NES")

        arcade.set_background_color(arcade.color.BLACK)

        self.camera = arcade.Camera2D()
        self.scene = None
        self.player = None

        self.left = self.right = self.run = self.jump = False

        self.coins = 0
        self.score = 0
        self.timer = 400

        # Музыка
        self.music_ground = arcade.load_sound(
            "Files/ForMario/music for mario/01. Ground Theme.mp3", False)

        self.tile_map = arcade.load_tilemap(
            "Files/ForMario/Тайлы/World 1.1 SuperMario.tmx", scaling=1)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    # =====================
    def setup(self):
        self.player = Mario()
        self.player.center_x = CELL * 8
        self.player.center_y = 300

        self.scene.add_sprite("Player", self.player)

        # Слои
        self.walls = self.scene["Walls"]
        self.break_blocks = self.scene["Wall can break"]
        self.coins_list = self.scene["Coins"]
        self.nothing = self.scene["Nothing"]
        self.exit_tubes = self.scene["ExitTubes"]
        self.flag = self.scene["Flag"]
        self.castle = self.scene["Castle"]
        self.tubes = self.scene["Tubes"]

        # Физика
        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=GRAVITY,
            platforms=self.walls or self.break_blocks)
        self.phisics1 = arcade.PhysicsEngineSimple(self.player, walls=self.tubes)

        self.music_ground.play(volume=1)

    # =====================
    def on_draw(self):
        self.clear()
        self.camera.use()

        self.scene.draw()

        # HUD NES
        arcade.draw_text(f"MARIO {self.score:06}",
            self.camera.position[0] + 16, 220,
            arcade.color.WHITE, 8)
        arcade.draw_text(f"COIN x{self.coins:02}",
            self.camera.position[0] + 120, 220,
            arcade.color.WHITE, 8)
        arcade.draw_text(f"TIME {self.timer}",
            self.camera.position[0] + 200, 220,
            arcade.color.WHITE, 8)

    # =====================
    def on_update(self, delta_time):
        # ===== СМЕРТЬ =====
        if arcade.check_for_collision_with_list(self.player, self.nothing):
            self.player.dead = True

        if self.player.dead:
            self.player.change_x = 0
            self.player.change_y -= GRAVITY
            return

        # ===== ДВИЖЕНИЕ =====
        target_speed = MAX_RUN if self.run else MAX_WALK

        if self.right:
            self.player.face_right = True
            if self.player.change_x < target_speed:
                self.player.change_x += ACCEL
        elif self.left:
            self.player.face_right = False
            if self.player.change_x > -target_speed:
                self.player.change_x -= ACCEL
        else:
            if self.player.change_x > FRICTION:
                self.player.change_x -= FRICTION
            elif self.player.change_x < -FRICTION:
                self.player.change_x += FRICTION
            else:
                self.player.change_x = 0

        # Прыжок NES
        if self.jump and self.player.is_jumping:
            if self.player.jump_timer < JUMP_MAX:
                self.player.change_y += JUMP_ADD
                self.player.jump_timer += 1
            else:
                self.player.is_jumping = False

        self.physics.update()
        self.phisics1.update()
        self.player.update_animation()

        # ===== МОНЕТЫ =====
        for coin in arcade.check_for_collision_with_list(self.player, self.coins_list):
            coin.remove_from_sprite_lists()
            self.coins += 1
            self.score += 200

        # ===== ФЛАГ =====
        if arcade.check_for_collision_with_list(self.player, self.flag):
            self.player.on_flag = True
            self.player.change_x = 1.5
            self.player.change_y = -1

        # ===== КАМЕРА NES =====
        half_w = self.camera.viewport_width / 2
        world_width = 211 * CELL

        cam_x = max(half_w, min(world_width - half_w, self.player.center_x))
        self.camera.position = (cam_x, SCREEN_HEIGHT / 2)

    # =====================
    def on_key_press(self, key, _):
        if key == arcade.key.LEFT:
            self.left = True
        if key == arcade.key.RIGHT:
            self.right = True
        if key == arcade.key.Z:
            self.run = True
        if key == arcade.key.SPACE:
            if self.physics.can_jump():
                self.jump = True
                self.player.is_jumping = True
                self.player.jump_timer = 0
                self.player.change_y = JUMP_START + abs(self.player.change_x) * 0.2

    def on_key_release(self, key, _):
        if key == arcade.key.LEFT:
            self.left = False
        if key == arcade.key.RIGHT:
            self.right = False
        if key == arcade.key.Z:
            self.run = False
        if key == arcade.key.SPACE:
            self.jump = False
            self.player.is_jumping = False


def main():
    game = SuperMario()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()