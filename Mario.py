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
UPDATES_PER_FRAME = 4
MIN_JUMP_SPEED = 5

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.face_right = True
        stop = arcade.load_texture("Files/ForMario/Картинки/StopMario.png")
        self.idle_textures = [stop, stop.flip_left_right()]
        jump = arcade.load_texture("Files/ForMario/Картинки/JumpMario.png")
        self.jump = [jump, jump.flip_left_right()]
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

        if abs(self.change_y) > 0.1:
            self.texture = self.jump[idx]
            return

        if abs(self.change_x) < 0.1 or abs(self.change_y) < 0.1:
            self.texture = self.idle_textures[idx]
            return

        # СОСТОЯНИЕ: Бег
        self.cur_frame += 1
        frame_index = self.cur_frame // 10
        if frame_index < len(self.walk_textures):
            self.texture = self.walk_textures[frame_index][idx]
        else:
            self.cur_frame = 0