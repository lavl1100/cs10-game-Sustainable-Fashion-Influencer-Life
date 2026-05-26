import arcade
import random
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
UI_FONT_PATH = ":resources:/fonts/ttf/Kenney/Kenney_Future_Narrow.ttf"
UI_FONT_NAME = "Kenney Future Narrow"
TUTORIAL_BUBBLE_PATH = ASSETS_DIR / "speech_bubble.png"
TUTORIAL_SPRITE_PATH = ASSETS_DIR / "sprite_happy.png"

arcade.load_font(UI_FONT_PATH)

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Thrift vs Fast Fashion Impact Game"

STARTING_MONEY = 100
RACK_SIZE = 12
SPACING = 120


FAST_FASHION_FABRICS = ["polyester", "nylon", "rayon", "acrylic"]
ECO_FABRICS = ["cotton", "linen", "wool", "hemp"]


class TutorialGuide:
    def __init__(self):
        self.bubble = arcade.Sprite(str(TUTORIAL_BUBBLE_PATH))
        self.bubble.center_x = SCREEN_WIDTH - 230
        self.bubble.center_y = 130
        self.bubble.width = 380
        self.bubble.height = 160
        self.sprite = arcade.Sprite(str(TUTORIAL_SPRITE_PATH))
        self.sprite.center_x = SCREEN_WIDTH - 72
        self.sprite.center_y = 62
        self.sprite.width = 120
        self.sprite.height = 120
        self.text = arcade.Text(
            "Use the arrow keys to move through the rack, then press SPACE to buy the highlighted thrift find.",
            self.bubble.center_x,
            self.bubble.center_y,
            arcade.color.DARK_SLATE_GRAY,
            12,
            font_name=UI_FONT_NAME,
            width=320,
            align="center",
            anchor_x="center",
            anchor_y="center",
            multiline=True,
        )

    def draw(self):
        self.bubble.draw()
        self.text.draw()
        self.sprite.draw()


class ThriftItem:
    def __init__(self):
        textures = [
            "shirt.png",
            "dress.png",
            "pants.png"
        ]

        self.sprite = arcade.Sprite(random.choice(textures), scale=0.4)

        # Fabric type
        if random.random() < 0.5:
            self.fabric = random.choice(FAST_FASHION_FABRICS)
            self.eco = False
        else:
            self.fabric = random.choice(ECO_FABRICS)
            self.eco = True

        # Pricing
        if self.eco:
            self.price = random.randint(15, 35)
            self.value = random.randint(30, 70)
            self.sprite.color = (180, 255, 200)  # green tint
        else:
            self.price = random.randint(5, 20)
            self.value = random.randint(10, 40)
            self.sprite.color = (255, 220, 220)  # red tint


class ThriftGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color((245, 240, 230))

        self.rack = []
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""
        self.tutorial_guide = TutorialGuide()

        # Reusable text objects avoid the slow draw_text helper warnings.
        self.selected_fabric_text = arcade.Text(
            "",
            0,
            0,
            arcade.color.BLACK,
            12,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.eco_status_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            130,
            arcade.color.BLACK,
            12,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.price_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            170,
            arcade.color.BLACK,
            16,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.detail_fabric_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            148,
            arcade.color.DARK_GRAY,
            14,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.money_text = arcade.Text(
            "",
            40,
            84,
            arcade.color.BLACK,
            16,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.score_text = arcade.Text(
            "",
            40,
            58,
            arcade.color.BLACK,
            16,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.instructions_text = arcade.Text(
            "← → browse   SPACE buy",
            40,
            34,
            arcade.color.DARK_GRAY,
            14,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.message_text = arcade.Text(
            "",
            380,
            58,
            arcade.color.RED,
            16,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )

    def setup(self):
        self.rack.clear()
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

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

        # Fabric label for selected item
        if self.rack:
            item = self.rack[self.current_index]

            self.selected_fabric_text.text = item.fabric.upper()
            self.selected_fabric_text.x = item.sprite.center_x
            self.selected_fabric_text.y = item.sprite.center_y - 68
            self.selected_fabric_text.draw()

            eco_text = "ECO 🌱 + BONUS" if item.eco else "FAST FASHION ❌ PENALTY"
            self.eco_status_text.text = eco_text
            self.eco_status_text.color = arcade.color.GREEN if item.eco else arcade.color.RED
            self.eco_status_text.draw()

        # Center panel
        if self.rack:
            item = self.rack[self.current_index]

            arcade.draw_lbwh_rectangle_filled(
                SCREEN_WIDTH // 2 - 130,
                120,
                260,
                100,
                (255, 255, 255)
            )

            self.price_text.text = f"Price: ${item.price}"
            self.price_text.draw()

            self.detail_fabric_text.text = item.fabric
            self.detail_fabric_text.draw()

        # UI
        arcade.draw_lbwh_rectangle_filled(
            20, 20,
            340, 90,
            (255, 255, 255)
        )

        self.money_text.text = f"Money: ${self.money}"
        self.money_text.draw()

        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()

        self.instructions_text.draw()

        self.message_text.text = self.message
        self.message_text.draw()
        self.tutorial_guide.draw()

    def on_update(self, delta_time):
        speed = 8
        self.current_offset += (self.target_offset - self.current_offset) / speed
        self.update_positions()

    def on_key_press(self, key, modifiers):
        if not self.rack:
            return

        if key == arcade.key.RIGHT:
            self.current_index = (self.current_index + 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        elif key == arcade.key.LEFT:
            self.current_index = (self.current_index - 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        elif key == arcade.key.SPACE:
            item = self.rack[self.current_index]

            if item.price > self.money:
                self.message = "Not enough money!"
                return

            self.money -= item.price

            # 🌍 IMPACT-BASED SCORING SYSTEM
            if item.eco:
                profit = min(120, 100 + item.price)
                self.score += profit
                self.message = f"Eco buy +{profit} 🌱"
            else:
                penalty = (item.price + 10) * -1
                self.score += penalty
                self.message = f"Fast fashion penalty {penalty} ❌"

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
