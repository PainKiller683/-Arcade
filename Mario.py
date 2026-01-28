import arcade

CELL = 16

class Mario(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # ====== ТЕКСТУРЫ ======
        self.idle = arcade.load_texture("Files/ForMario/Картинки/StopMario.png")
        self.idle_l = self.idle.flip_left_right()

        self.jump = arcade.load_texture("Files/ForMario/Картинки/JumpMario.png")
        self.jump_l = self.jump.flip_left_right()

        self.slide = arcade.load_texture("Files/ForMario/Картинки/SlideMario.png")
        self.slide_l = self.slide.flip_left_right()

        self.walk = []
        for i in range(1, 4):
            t = arcade.load_texture(f"Files/ForMario/Картинки/MarioGo{i}.png")
            self.walk.append((t, t.flip_left_right()))

        self.texture = self.idle
        self.face_right = True

        # ====== СОСТОЯНИЯ ======
        self.is_jumping = False
        self.jump_timer = 0
        self.on_flag = False
        self.dead = False

        self.cur_frame = 0

    def update_animation(self, delta_time=1/60):
        idx = 0 if self.face_right else 1

        # Падение / прыжок
        if abs(self.change_y) > 0.2:
            self.texture = self.jump if idx == 0 else self.jump_l
            return

        # Занос (NES)
        skidding = (idx == 0 and self.change_x < -0.1) or \
                   (idx == 1 and self.change_x > 0.1)
        if skidding:
            self.texture = self.slide if idx == 0 else self.slide_l
            return

        # Бег
        if abs(self.change_x) > 0.05:
            self.cur_frame += abs(self.change_x) * 0.15
            frame = int(self.cur_frame) % 3
            self.texture = self.walk[frame][idx]
            return

        # Покой
        self.texture = self.idle if idx == 0 else self.idle_l