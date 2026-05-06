import arcade
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Thrift & Fashion Impact Game"

STARTING_MONEY = 100
RACK_SIZE = 12
SPACING = 120


FAST_FASHION_FABRICS = ["polyester", "nylon", "rayon", "acrylic"]
ECO_FABRICS = ["cotton", "linen", "wool", "hemp"]


class ThriftItem:
    def __init__(self):
        textures = [
            "assets/shirt.png",
            "assets/dress.png",
            "assets/pants.png"
        ]

        self.sprite = arcade.Sprite(random.choice(textures), scale=0.4)

        if random.random() < 0.5:
            self.fabric = random.choice(FAST_FASHION_FABRICS)
            self.eco = False
        else:
            self.fabric = random.choice(ECO_FABRICS)
            self.eco = True

        if self.eco:
            self.price = random.randint(15, 35)
            self.value = random.randint(30, 70)
            self.sprite.color = (180, 255, 200)
        else:
            self.price = random.randint(5, 20)
            self.value = random.randint(10, 40)
            self.sprite.color = (255, 220, 220)


class ThriftGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color((245, 240, 230))

        self.rack = []
        self.sprite_list = arcade.SpriteList()

        self.inventory = []

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

        self.game_over = False

    def setup(self):
        self.rack.clear()
        self.sprite_list = arcade.SpriteList()
        self.inventory.clear()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""
        self.game_over = False

        for _ in range(RACK_SIZE):
            item = ThriftItem()
            self.rack.append(item)
            self.sprite_list.append(item.sprite)

        self.update_positions()

    def update_positions(self):
        center_x = SCREEN_WIDTH // 2

        for i, item in enumerate(self.rack):
            offset = (i * SPACING) - self.current_offset
            x = center_x + offset

            dist = abs(i - self.current_index)

            scale = max(0.25, 0.5 - dist * 0.05)
            alpha = max(120, 255 - dist * 40)

            item.sprite.scale = scale
            item.sprite.alpha = alpha

            item.sprite.center_x = x
            item.sprite.center_y = SCREEN_HEIGHT // 2 + 50 - dist * 10

    def on_draw(self):
        self.clear()

        if self.game_over:
            self.draw_summary_screen()
            return

        # Background
        arcade.draw_lbwh_rectangle_filled(
            0, 0,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (245, 240, 230)
        )

        arcade.draw_lbwh_rectangle_filled(
            0, 0,
            SCREEN_WIDTH, 200,
            (220, 210, 190)
        )

        arcade.draw_line(
            100, SCREEN_HEIGHT // 2 + 120,
            800, SCREEN_HEIGHT // 2 + 120,
            (120, 80, 40), 6
        )

        self.sprite_list.draw()

        # Center item info
        if self.rack:
            item = self.rack[self.current_index]

            arcade.draw_text(
                f"{item.fabric}",
                SCREEN_WIDTH // 2 - 50,
                150,
                arcade.color.BLACK,
                16
            )

        # UI
        arcade.draw_text(f"Money: ${self.money}", 20, 20, arcade.color.BLACK, 16)
        arcade.draw_text(f"Score: {self.score}", 20, 50, arcade.color.BLACK, 16)

        # 🛑 END BUTTON
        arcade.draw_lbwh_rectangle_filled(
            720, 30,
            160, 50,
            (200, 200, 200)
        )

        arcade.draw_text(
            "END THRIFTING",
            735, 50,
            arcade.color.BLACK,
            12
        )

        arcade.draw_text(self.message, 320, 50, arcade.color.RED, 16)

    def draw_summary_screen(self):
        arcade.draw_lbwh_rectangle_filled(
            0, 0,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (30, 30, 30)
        )

        arcade.draw_text(
            "THRIFTING SUMMARY",
            300,
            520,
            arcade.color.WHITE,
            30
        )

        arcade.draw_text(
            f"Final Score: {self.score}",
            350,
            450,
            arcade.color.GREEN,
            20
        )

        eco_count = sum(1 for item in self.inventory if item.eco)
        fast_count = len(self.inventory) - eco_count

        arcade.draw_text(
            f"Eco Items Bought: {eco_count}",
            320,
            400,
            arcade.color.GREEN,
            16
        )

        arcade.draw_text(
            f"Fast Fashion Items: {fast_count}",
            320,
            370,
            arcade.color.RED,
            16
        )

        arcade.draw_text(
            "CLICK TO RESTART",
            320,
            250,
            arcade.color.WHITE,
            20
        )

    def on_update(self, delta_time):
        speed = 8
        self.current_offset += (self.target_offset - self.current_offset) / speed
        self.update_positions()

    def on_key_press(self, key, modifiers):
        if self.game_over:
            self.setup()
            return

        if not self.rack:
            return

        if key == arcade.key.RIGHT:
            self.current_index = (self.current_index + 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        elif key == arcade.key.LEFT:
            self.current_index = (self.current_index - 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            self.setup()
            return

        # 🛑 END THRIFTING BUTTON
        if 720 <= x <= 880 and 30 <= y <= 80:
            self.game_over = True
            return

        if not self.rack:
            return

        item = self.rack[self.current_index]

        if item.price > self.money:
            self.message = "Not enough money!"
            return

        self.money -= item.price

        if item.eco:
            profit = (item.value - item.price) * 2
            self.score += profit
        else:
            profit = (item.price + 10) * -1
            self.score += profit

        self.inventory.append(item)

        self.sprite_list.remove(item.sprite)
        self.rack.pop(self.current_index)

        new_item = ThriftItem()
        self.rack.append(new_item)
        self.sprite_list.append(new_item.sprite)

        if self.current_index >= len(self.rack):
            self.current_index = 0

        self.target_offset = self.current_index * SPACING


def main():
    game = ThriftGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
