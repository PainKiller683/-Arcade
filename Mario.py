import arcade
import arcade.gui
import arcade.gui
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
JUMP_SPEED = 3
UPDATES_PER_FRAME = 4
MAX_JUMP_SPEED = 6

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.is_jumping = False
        self.face_right = True
        stop = arcade.load_texture("Files/ForMario/Картинки/StopMario.png")
        self.idle_textures = [stop, stop.flip_left_right()]
        jump = arcade.load_texture("Files/ForMario/Картинки/JumpMario.png")
        self.jump = [jump, jump.flip_left_right()]
        slide = arcade.load_texture("Files/ForMario/Картинки/SlideMario.png")
        self.slide = [slide, slide.flip_left_right()]
        self.walk_textures = []
        for i in range(1, 4):
            walk = arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png")
            self.walk_textures.append([walk, walk.flip_left_right()])
        self.cur_frame = 0
        self.texture = self.idle_textures[0]

    def update_animation(self, delta_time: float = 1 / 60):
        idx = 0 if self.face_right else 1

        # 1. Анимация ПРЫЖКА (Приоритет №1)
        if abs(self.change_y) > 0.2:
            self.texture = self.jump[idx]
            return

        # 2. Анимация ЗАНОСА (Приоритет №2)
        # Если Марио бежит в одну сторону, а игрок жмет в другую
        is_skidding = (idx == 0 and self.change_x < -0.1) or \
                  (idx == 1 and self.change_x > 0.1)
        if is_skidding:
            self.texture = self.slide[idx]
            return

        # 3. Анимация БЕГА / ПОКОЯ
        if abs(self.change_x) > 0.05:
            self.cur_frame += abs(self.change_x) * 0.1
            frame = int(self.cur_frame) % 3
            self.texture = self.walk_textures[frame][idx]
            return

        # ПРИОРИТЕТ 4: Покой
        self.texture = self.idle_textures[idx]