import arcade
import random

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Thrift Shop Minigame (Sprites)"

ITEM_COUNT = 5
GAME_TIME = 30.0


class ThriftItem:
    def __init__(self, x, y):
        # Load random sprite
        textures = [
            "assets/shirt.png",
            "assets/dress.png",
            "assets/pants.png"
        ]
        texture_path = random.choice(textures)

        self.sprite = arcade.Sprite(texture_path, scale=0.3)
        self.sprite.center_x = x
        self.sprite.center_y = y

        # Gameplay values
        self.price = random.randint(5, 25)
        self.value = random.randint(0, 60)

        # Rarity color tint
        if self.value > 45:
            self.sprite.color = arcade.color.GOLD
        elif self.value > 25:
            self.sprite.color = arcade.color.LIGHT_GRAY
        else:
            self.sprite.color = arcade.color.WHITE

    def draw(self):
        self.sprite.draw()

        # Draw price under item
        arcade.draw_text(
            f"${self.price}",
            self.sprite.center_x - 20,
            self.sprite.center_y - 50,
            arcade.color.BLACK,
            12
        )

    def is_clicked(self, x, y):
        return self.sprite.collides_with_point((x, y))


class ThriftGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BEIGE)

        self.items = []
        self.score = 0
        self.time_left = GAME_TIME
        self.game_over = False

    def setup(self):
        self.items.clear()
        self.score = 0
        self.time_left = GAME_TIME
        self.game_over = False

        for _ in range(ITEM_COUNT):
            self.spawn_item()

    def spawn_item(self):
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.randint(150, SCREEN_HEIGHT - 100)
        self.items.append(ThriftItem(x, y))

    def on_draw(self):
        self.clear()

        # Draw items
        for item in self.items:
            item.draw()

        # UI
        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.BLACK, 16)
        arcade.draw_text(f"Time: {int(self.time_left)}", 680, 10, arcade.color.BLACK, 16)

        if self.game_over:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH / 2 - 100,
                SCREEN_HEIGHT / 2 + 20,
                arcade.color.RED,
                30
            )
            arcade.draw_text(
                "Click to Restart",
                SCREEN_WIDTH / 2 - 110,
                SCREEN_HEIGHT / 2 - 20,
                arcade.color.BLACK,
                18
            )

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.time_left -= delta_time

        if self.time_left <= 0:
            self.game_over = True

        # Keep items stocked
        while len(self.items) < ITEM_COUNT:
            self.spawn_item()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            self.setup()
            return

        for item in self.items:
            if item.is_clicked(x, y):
                profit = item.value - item.price
                self.score += profit
                self.items.remove(item)
                break


def main():
    game = ThriftGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
