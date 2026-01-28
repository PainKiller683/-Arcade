import arcade
from enum import Enum

# ==========================
# КОНСТАНТЫ
# ==========================
TILE = 16
SCREEN_W, SCREEN_H = 256, 240
GRAVITY = 0.5
MAX_FALL = -8
JUMP = 9
RUN_SPEED = 2.2
AUTO_RUN = 2.0
START_TIME = 400

# ==========================
# СОСТОЯНИЯ
# ==========================
class GameState(Enum):
    TITLE = 0
    PLAY = 1
    CLEAR = 2

# ==========================
# СПРАЙТЫ
# ==========================
class Mario(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(16, arcade.color.RED, 255)
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False
        self.big = False
        self.on_flag = False
        self.auto_run = False

    def grow(self):
        if not self.big:
            self.height = 32
            self.center_y += 8
            self.big = True

class Goomba(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(16, arcade.color.BROWN, 255)
        self.center_x = x
        self.center_y = y
        self.change_x = -1

class Koopa(arcade.Sprite):
    WALK, SHELL_IDLE, SHELL_MOVE = range(3)
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(16, arcade.color.GREEN, 255)
        self.center_x = x
        self.center_y = y
        self.state = Koopa.WALK
        self.change_x = -1

    def stomp(self, direction):
        if self.state == Koopa.WALK:
            self.state = Koopa.SHELL_IDLE
            self.change_x = 0
        elif self.state == Koopa.SHELL_IDLE:
            self.state = Koopa.SHELL_MOVE
            self.change_x = 5 * direction

class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(12, arcade.color.YELLOW, 255)
        self.center_x = x
        self.center_y = y

# ==========================
# ИГРА
# ==========================
class MarioGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, "SUPER MARIO BROS")
        self.camera = arcade.camera.Camera2D()
        self.state = GameState.TITLE

        self.scene = None
        self.player = None
        self.level = "maps/level_1_1.json"
        self.underground = "maps/level_1_2.json"

        self.score = 0
        self.coins = 0
        self.timer = START_TIME
        self.time_acc = 0

        # self.snd = {k: arcade.load_sound(f"sounds/{k}.wav") for k in
        #     ["jump","coin","powerup","stomp","kick","break","flag","stage_clear"]}

    # ==========================
    def load_level(self, path):
        tilemap = arcade.load_tilemap(
            path,
            scaling=1,
            layer_options={
                "Ground": {"use_spatial_hash": True},
                "Bricks": {"use_spatial_hash": True},
                "Pipes": {"use_spatial_hash": True},
                "UndergroundCeiling": {"use_spatial_hash": True},
            }
        )

        self.scene = arcade.Scene.from_tilemap(tilemap)

        spawn = tilemap.object_lists["PlayerSpawn"][0]
        self.player = Mario(spawn.center_x, spawn.center_y)
        self.scene.add_sprite("Player", self.player)

        self.scene.add_sprite_list("Enemies")
        for o in tilemap.object_lists.get("Enemies", []):
            if o.name == "Koopa":
                self.scene.add_sprite("Enemies", Koopa(o.center_x, o.center_y))
            else:
                self.scene.add_sprite("Enemies", Goomba(o.center_x, o.center_y))

        self.scene.add_sprite_list("Coins")
        for o in tilemap.object_lists.get("Coins", []):
            self.scene.add_sprite("Coins", Coin(o.center_x, o.center_y))

        self.flag = tilemap.object_lists.get("Flag", [None])[0]
        self.exit = tilemap.object_lists.get("Exit", [None])[0]
        self.pipe = tilemap.object_lists.get("Pipe", [])

        self.timer = START_TIME

    # ==========================
    def setup(self):
        self.load_level(self.level)

    # ==========================
    def on_draw(self):
        self.clear(arcade.color.BLACK)

        if self.state == GameState.TITLE:
            arcade.draw_text("SUPER MARIO BROS.",
                             32, 150, arcade.color.WHITE, 16)
            arcade.draw_text("PRESS ENTER",
                             80, 100, arcade.color.WHITE, 10)
            return

        self.camera.use()
        self.scene.draw()

        # HUD
        arcade.draw_text(f"MARIO {self.score:06}",
                         self.camera.position[0]+8, 220,
                         arcade.color.WHITE, 8)
        arcade.draw_text(f"COIN x{self.coins:02}",
                         self.camera.position[0]+104, 220,
                         arcade.color.WHITE, 8)
        arcade.draw_text(f"TIME {self.timer}",
                         self.camera.position[0]+184, 220,
                         arcade.color.WHITE, 8)

    # ==========================
    def update(self, dt):
        if self.state != GameState.PLAY:
            return

        self.time_acc += dt
        if self.time_acc >= 1:
            self.timer -= 1
            self.time_acc = 0

        if not self.player.on_flag:
            self.player.change_y = max(self.player.change_y - GRAVITY, MAX_FALL)

        self.scene.update()
        self.resolve_collisions()
        self.collect_coins()
        self.check_pipe()
        self.check_flag()
        self.update_camera()

    # ==========================
    def resolve_collisions(self):
        walls = []
        for name in ["Ground","Bricks","Pipes","UndergroundCeiling"]:
            if name in self.scene:
                walls += self.scene[name]

        self.player.on_ground = False

        # Y
        for w in walls:
            if arcade.check_for_collision(self.player, w):
                if self.player.change_y < 0:
                    self.player.bottom = w.top
                    self.player.change_y = 0
                    self.player.on_ground = True
                elif self.player.change_y > 0:
                    self.player.top = w.bottom
                    self.player.change_y = 0
                    if w in self.scene.get("Bricks", []) and self.player.big:
                        w.remove_from_sprite_lists()
                        arcade.play_sound(self.snd["break"])

        # X
        self.player.center_x += self.player.change_x
        for w in walls:
            if arcade.check_for_collision(self.player, w):
                if self.player.change_x > 0:
                    self.player.right = w.left
                elif self.player.change_x < 0:
                    self.player.left = w.right

        # Enemies
        for e in self.scene["Enemies"]:
            e.change_y -= GRAVITY
            if arcade.check_for_collision(self.player, e):
                direction = 1 if self.player.center_x < e.center_x else -1
                if self.player.change_y < 0:
                    if isinstance(e, Koopa):
                        e.stomp(direction)
                    else:
                        e.remove_from_sprite_lists()
                    arcade.play_sound(self.snd["stomp"])
                    self.player.change_y = JUMP / 2
                elif isinstance(e, Koopa) and e.state == Koopa.SHELL_IDLE:
                    e.stomp(direction)
                    arcade.play_sound(self.snd["kick"])

    # ==========================
    def collect_coins(self):
        for c in arcade.check_for_collision_with_list(self.player, self.scene["Coins"]):
            c.remove_from_sprite_lists()
            self.coins += 1
            self.score += 200
            arcade.play_sound(self.snd["coin"])

    # ==========================
    def check_pipe(self):
        for p in self.pipe:
            if abs(self.player.center_x - p.center_x) < 8 and self.player.on_ground:
                if arcade.key.DOWN in self._keys:
                    self.load_level(self.underground)

    # ==========================
    def check_flag(self):
        if self.flag and abs(self.player.center_x - self.flag.center_x) < 8:
            self.player.on_flag = True
            self.player.change_x = AUTO_RUN
            self.player.change_y = -1
            arcade.play_sound(self.snd["flag"])

        if self.player.on_flag and self.exit and self.player.center_x >= self.exit.center_x:
            self.state = GameState.CLEAR
            arcade.play_sound(self.snd["stage_clear"])

    # ==========================
    def update_camera(self):
        self.camera.move_to((self.player.center_x - SCREEN_W//2, 0), 0.2)

    # ==========================
    def on_key_press(self, key, _):
        if self.state == GameState.TITLE and key == arcade.key.ENTER:
            self.state = GameState.PLAY
            self.setup()
            return

        if self.state != GameState.PLAY:
            return

        if key == arcade.key.RIGHT:
            self.player.change_x = RUN_SPEED
        if key == arcade.key.LEFT:
            self.player.change_x = -RUN_SPEED
        if key == arcade.key.SPACE and self.player.on_ground:
            self.player.change_y = JUMP
            arcade.play_sound(self.snd["jump"])

    def on_key_release(self, key, _):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0

# ==========================
def main():
    MarioGame()
    arcade.run()

if __name__ == "__main__":
    main()
