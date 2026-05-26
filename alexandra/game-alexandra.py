import arcade
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
UI_FONT_PATH = ":resources:/fonts/ttf/Kenney/Kenney_Future_Narrow.ttf"
UI_FONT_NAME = "Kenney Future Narrow"
TUTORIAL_BUBBLE_PATH = ASSETS_DIR / "speech_bubble.png"
TUTORIAL_SPRITE_PATH = ASSETS_DIR / "sprite_happy.png"

arcade.load_font(UI_FONT_PATH)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Click Detection Test"

show_square = False


class TutorialGuide:
    def __init__(self):
        self.bubble = arcade.Sprite(str(TUTORIAL_BUBBLE_PATH))
        self.bubble.center_x = SCREEN_WIDTH - 240
        self.bubble.center_y = 110
        self.bubble.width = 380
        self.bubble.height = 150
        self.sprite = arcade.Sprite(str(TUTORIAL_SPRITE_PATH))
        self.sprite.center_x = SCREEN_WIDTH - 72
        self.sprite.center_y = 56
        self.sprite.width = 110
        self.sprite.height = 110
        self.text = arcade.Text(
            "Click the photo to toggle the red square.",
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


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        self.tutorial_guide = TutorialGuide()

        self.photo = arcade.Sprite("Screenshot 2026-04-29 141019.png", scale=1.0)
        self.photo.center_x = 250
        self.photo.center_y = 300

        self.photo_list = arcade.SpriteList()
        self.photo_list.append(self.photo)

    def on_draw(self):
        self.clear()
        self.photo_list.draw()

        if show_square:
            arcade.draw_lbwh_rectangle_filled(500, 250, 100, 100, arcade.color.RED)
        self.tutorial_guide.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        global show_square
        if self.photo.collides_with_point((x, y)):
            show_square = not show_square


def main():
    MyWindow()
    arcade.run()


if __name__ == "__main__":
    main()
