import arcade

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Анимация бега 2026"
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 7  # Каждые 7 обновлений экрана меняется кадр


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # 1. Загружаем текстуры (для примера используем встроенные ресурсы arcade)
        # В реальном проекте замени на свои файлы: "run1.png", "run2.png" и т.д.
        main_path = ":resources:images/animated_characters/female_person/female_person"

        # Текстура когда стоим
        self.idle_texture = arcade.load_texture(f"{main_path}_idle.png")

        # Список текстур для бега (4 кадра)
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Начальная текстура
        self.texture = self.idle_texture
        self.cur_frame = 0

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0 and self.character_face_direction == 0:
            self.character_face_direction = 1  # Повернулся влево
        elif self.change_x > 0 and self.character_face_direction == 1:
            self.character_face_direction = 0  # Повернулся вправо

            # ЕСЛИ ПЕРСОНАЖ СТОИТ
        if self.change_x == 0:
            # Показываем картинку "стоит" в текущем направлении
            self.texture = self.idle_texture_pair[self.character_face_direction]
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


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_list = None
        self.player = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.player.center_x = 100
        self.player.center_y = 100
        self.player_list.append(self.player)

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.player_list.update()
        # Важно: вызываем обновление анимации!
        self.player_list.update_animation(delta_time)

    def on_key_press(self, key, modifiers):
        # При нажатии меняем change_x
        if key == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        # При отпускании обнуляем
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0


if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()