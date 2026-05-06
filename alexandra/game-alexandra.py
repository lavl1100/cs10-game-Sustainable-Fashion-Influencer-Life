import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Photo Button"

show_square = False


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.WHITE)

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

    def on_mouse_press(self, x, y, button, modifiers):
        global show_square
        if self.photo.collides_with_point((x, y)):
            show_square = not show_square


def main():
    MyWindow()
    arcade.run()


if __name__ == "__main__":
    main()
