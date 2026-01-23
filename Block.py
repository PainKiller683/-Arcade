# import arcade
# class My_Blocks(arcade.Sprite):
#     def __init__(self):
#         super().__init__()
#         self.tile_map = arcade.load_tilemap("Files/ForMario/Тайлы/World 1.1 SuperMario.tmx", scaling=1)
#         self.blocks = self.tile_map.sprite_lists["Wall can break"]
#         self.is_bumping = False
#         self.bump_speed = 5
#
#     def update(self):
#         self.collision = arcade.check_for_collision_with_list(self.blocks)
#         if self.collision:
#             self.center_y += self.bump_speed
#             if self.center_y > self.original_y + 10:
#                 self.bump_speed = -5
#             if self.center_y <= self.original_y:
#                 self.center_y = self.original_y
#                 self.is_bumping = False
#                 self.bump_speed = 5