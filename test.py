import arcade

# Константы
import arcade

# Константы
GRAVITY = 0.4  # МЕНЬШЕ = медленнее прыжок (в 2026 году стандарт 0.4-0.5)
JUMP_SPEED = 10  # Мощность прыжка
MOVEMENT_SPEED = 5


class QuestionBlock(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(":resources:images/tiles/boxCrate_double.png", 0.5)
        self.center_x = x
        self.center_y = y
        self.original_y = y
        self.is_bumping = False
        self.bump_speed = 5  # Насколько резко блок дергается

    def update(self):
        # Если по блоку ударили
        if self.is_bumping:
            self.center_y += self.bump_speed
            # Когда блок поднялся на 10 пикселей, начинаем возвращать
            if self.center_y > self.original_y + 10:
                self.bump_speed = -5
            # Когда вернулся на место — останавливаемся
            if self.center_y <= self.original_y:
                self.center_y = self.original_y
                self.is_bumping = False
                self.bump_speed = 5


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Mario Block Bump 2026")
        self.player = arcade.Sprite(":resources:images/animated_characters/female_person/female_person_idle.png", 0.5)
        self.player.center_x = 100
        self.player.center_y = 100

        self.wall_list = arcade.SpriteList()
        # Создаем блок над головой
        self.block = QuestionBlock(100, 250)
        self.wall_list.append(self.block)

        # Пол
        for x in range(0, 800, 64):
            wall = arcade.SpriteSolidColor(64, 20, arcade.color.BROWN)
            wall.center_x = x
            wall.center_y = 10
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.wall_list, gravity_constant=GRAVITY
        )

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.block.update()  # Обновляем анимацию блока

        # ПРОВЕРКА УДАРА ГОЛОВОЙ
        # Проверяем коллизию (столкновение)
        if self.player.change_y > 0:  # Только если игрок летит ВВЕРХ
            hit_list = arcade.check_for_collision_with_list(self.player, self.wall_list)
            for hit in hit_list:
                if isinstance(hit, QuestionBlock) and not hit.is_bumping:
                    hit.is_bumping = True  # Запускаем анимацию блока
                    self.player.change_y = 0  # Останавливаем игрока (головой в блок)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        # Механика короткого/длинного прыжка (из прошлого ответа)
        if key == arcade.key.SPACE and self.player.change_y > 3:
            self.player.change_y = 3

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.player.draw()


if __name__ == "__main__":
    arcade.run()