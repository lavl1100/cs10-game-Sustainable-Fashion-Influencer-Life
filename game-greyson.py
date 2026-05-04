import arcade
from pathlib import Path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "WASD Sprite Movement"
MOVEMENT_SPEED = 5


class Player(arcade.Sprite):
    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
        if self.bottom < 0:
            self.bottom = 0
        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_list = None
        self.player_sprite = None

        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False

    def setup(self):
        self.player_list = arcade.SpriteList()

        image_path = Path(__file__).with_name("lil-image.png")
        self.player_sprite = Player(str(image_path), scale=1.0)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        self.player_list.append(self.player_sprite)

    def on_draw(self):
        self.clear()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.w_pressed and not self.s_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.s_pressed and not self.w_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED

        if self.a_pressed and not self.d_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.d_pressed and not self.a_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

        self.player_list.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.A:
            self.a_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True
        elif key == arcade.key.D:
            self.d_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.A:
            self.a_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False
        elif key == arcade.key.D:
            self.d_pressed = False


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
