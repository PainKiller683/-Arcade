import arcade
# Физика мира
GRAVITY = 0.8
FRICTION = 0.12        # Сила трения (скольжение)
ACCEL = 0.15           # Ускорение при ходьбе

# Скоростные лимиты
MAX_WALK_SPEED = 3.2   # Обычный шаг
MAX_RUN_SPEED = 5.5    # Предел разгона (зажата кнопка ускорения)

# Прыжок (SMB1 Style)
JUMP_START_IMPULSE = 6.0 # Начальный рывок (отрыв от земли)
JUMP_ADD_FORCE = 0.65    # Прирост скорости за кадр удержания
JUMP_MAX_FRAMES = 14     # Сколько времени можно "качать" прыжок

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.face_right = True
        self.cur_frame = 0
        self.is_jumping = False
        self.jump_timer = 0

        # Загрузка текстур
        self.idle_tex = [arcade.load_texture("idle.png"), arcade.load_texture("idle.png").flip_left_right()]
        self.jump_tex = [arcade.load_texture("jump.png"), arcade.load_texture("jump.png").flip_left_right()]
        self.skid_tex = [arcade.load_texture("skid.png"),
                         arcade.load_texture("skid.png").flip_left_right()]  # Кадр торможения

        self.walk_textures = []
        for i in range(1, 4):
            t = arcade.load_texture(f"walk{i}.png")
            self.walk_textures.append([t, t.flip_left_right()])

        self.texture = self.idle_tex[0]

    def update_animation(self, delta_time):
        # Выбор стороны
        idx = 0 if self.face_right else 1

        # 1. Анимация ПРЫЖКА (Приоритет №1)
        if abs(self.change_y) > 0.2:
            self.texture = self.jump_tex[idx]
            return

        # 2. Анимация ЗАНОСА (Приоритет №2)
        # Если Марио бежит в одну сторону, а игрок жмет в другую
        is_skidding = (self.change_x > 1 and arcade.key.LEFT) or (self.change_x < -1 and arcade.key.RIGHT)
        if is_skidding:
            self.texture = self.skid_tex[idx]
            return

        # 3. Анимация БЕГА / ПОКОЯ
        if abs(self.change_x) < 0.2:
            self.texture = self.idle_tex[idx]
        else:
            # Скорость анимации ног зависит от скорости движения
            self.cur_frame += abs(self.change_x) * 0.2
            frame = int(self.cur_frame) % 3
            self.texture = self.walk_textures[frame][idx]


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "NES Mario Physics")
        self.player = Player()
        self.physics_engine = None

        # Состояния ввода
        self.left_down = False
        self.right_down = False
        self.jump_down = False
        self.b_button_down = False  # Кнопка ускорения/огня (в SMB1 это B)

    def setup(self):
        self.walls = arcade.SpriteList()
        # Генерация пола и одной трубы (32px высота)
        for x in range(0, 1600, 16):
            ground = arcade.SpriteSolidColor(16, 16, arcade.color.BROWN)
            ground.position = (x, 8)
            self.walls.append(ground)

        # Труба (два блока по 16px = 32px)
        for y in (24, 40):
            pipe = arcade.SpriteSolidColor(32, 16, arcade.color.GREEN)
            pipe.position = (300, y)
            self.walls.append(pipe)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.walls, gravity_constant=GRAVITY
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_down = True
        if key == arcade.key.RIGHT: self.right_down = True
        if key == arcade.key.Z: self.b_button_down = True  # Кнопка ускорения
        if key == arcade.key.X or key == arcade.key.SPACE:  # Кнопка прыжка
            if self.physics_engine.can_jump():
                self.jump_down = True
                self.player.is_jumping = True
                self.player.jump_timer = 0
                # Начальный импульс зависит от того, бежим ли мы (фишка SMB1)
                self.player.change_y = JUMP_START_IMPULSE + (abs(self.player.change_x) * 0.2)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT: self.left_down = False
        if key == arcade.key.RIGHT: self.right_down = False
        if key == arcade.key.Z: self.b_button_down = False
        if key == arcade.key.X or key == arcade.key.SPACE:
            self.jump_down = False
            self.player.is_jumping = False

    def on_update(self, delta_time):
        # 1. ГОРИЗОНТАЛЬНОЕ ДВИЖЕНИЕ
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

        self.physics_engine.update()
        self.player.update_animation(delta_time)

    def on_draw(self):
        self.clear()
        self.walls.draw()
        self.player.draw()


if __name__ == "__main__":
    arcade.run()