import arcade

CELL = 16


class Mario(arcade.Sprite):
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
        self.texture = self.idle_textures[0]

        # BIG MARIO
        # self.big_idle_r = arcade.load_texture("Files/ForMario/Картинки/idles.png")
        # self.big_idle_l = self.big_idle_r.flip_left_right()
        # self.big_jump_r = arcade.load_texture("Files/ForMario/Картинки/jumps.png")
        # self.big_jump_l = self.big_jump_r.flip_left_right()
        #
        # self.big_walk = []
        # for i in range(1, 4):
        #     t = arcade.load_texture(f"Files/ForMario/Картинки/walks{i}.png")
        #     self.big_walk.append((t, t.flip_left_right()))

        # STATE
        self.big = False
        self.dead = False
        self.on_flag = False
        self.control_locked = False
        self.invincible_timer = 0
        self.cur_frame = 0

        # для анимации смерти
        self.death_jump = False
        self.death_timer = 0

    # def grow(self):
    #     if not self.big:
    #         self.big = True
    #         self.scale = 1.2
    #
    # def shrink(self):
    #     self.big = False
    #     self.scale = 1
    #     self.invincible_timer = 120

    def hit(self):
        if self.invincible_timer > 0:
            return
        if self.big:
            return
        else:
            self.dead = True
            self.control_locked = True
            self.death_jump = True
            self.change_y = 10

    def hit_block(self):
        if self.change_y > 0:
            self.change_y = 0

    def start_flag_slide(self):
        self.on_flag = True
        self.control_locked = True
        self.change_x = 0
        self.change_y = -2

    def update_flag_slide(self):
        if self.on_flag:
            self.center_y += self.change_y
            if self.center_y <= CELL * 3:
                self.on_flag = False
                self.control_locked = False
                self.change_y = 0

    def update_animation(self, delta_time=1 / 60):
        if self.change_x > 0:
            self.face_right = True
        elif self.change_x < 0:
            self.face_right = False

        idx = 0 if self.face_right else 1

        # 1. Анимация ПРЫЖКА (Приоритет №1)
        if abs(self.change_y) > 0.2:
            self.texture = self.jump[idx]
            return

        elif abs(self.change_y) < 0.1:
            self.texture = self.idle_textures[idx]
        # 2. Анимация ЗАНОСА (Приоритет №2)
        # Если Марио бежит в одну сторону, а игрок жмет в другую
        is_skidding = (idx == 0 and self.change_x < -0.1) or \
                      (idx == 1 and self.change_x > 0.1)
        if is_skidding:
            self.texture = self.slide[idx]
            return

        if abs(self.change_x) < 0.1:
            self.texture = self.idle_textures[idx]
        # 3. Анимация БЕГА / ПОКОЯ
        if abs(self.change_x) > 0.05:
            self.cur_frame += abs(self.change_x) * 0.1
            frame = int(self.cur_frame) % 3
            self.texture = self.walk_textures[frame][idx]
            return

        # СОСТОЯНИЕ: Бег
        self.cur_frame += 1
        frame_index = self.cur_frame // 10
        if frame_index < len(self.walk_textures):
            self.texture = self.walk_textures[int(frame_index)][idx]
        else:
            self.cur_frame = 0
        # ПРИОРИТЕТ 4: Покой
        self.texture = self.idle_textures[idx]