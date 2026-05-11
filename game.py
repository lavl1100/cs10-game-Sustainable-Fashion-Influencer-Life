"""Fashion game home screen starter.

This file now provides the team-owned main menu for the game.
The five navigation buttons and the background are sprite-driven so
the art can be swapped in later without changing the screen logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fashionidísimitas"

HOME_BUTTON_WIDTH = 220
HOME_BUTTON_HEIGHT = 58
HOME_BUTTON_LEFT = 54
HOME_BUTTON_TOP = SCREEN_HEIGHT - 160
HOME_BUTTON_GAP = 14

PRESS_ANIMATION_TIME = 0.18
PRESS_SHRINK_SCALE = 0.86

ASSETS_DIR = Path("assets")
BACKGROUND_IMAGE = ASSETS_DIR / "backgrounds" / "home_background.png"
BUTTON_IMAGE_PATHS = {
    "settings": ASSETS_DIR / "buttons" / "settings_button.png",
    "social media": ASSETS_DIR / "buttons" / "social_media_button.png",
    "closet": ASSETS_DIR / "buttons" / "closet_button.png",
    "clothing store": ASSETS_DIR / "buttons" / "clothing_store_button.png",
    "activity center": ASSETS_DIR / "buttons" / "activity_center_button.png",
}


def _path_exists(path: Path) -> bool:
    return path.is_file()


def _make_sprite(
    image_path: Path,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fallback_color: arcade.Color,
) -> arcade.Sprite:
    """Load a sprite from disk when available, otherwise use a solid block."""
    if _path_exists(image_path):
        sprite = arcade.Sprite(str(image_path))
        sprite.center_x = center_x
        sprite.center_y = center_y
        sprite.width = width
        sprite.height = height
        return sprite

    sprite = arcade.SpriteSolidColor(int(width), int(height), fallback_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    return sprite


@dataclass
class StatusBox:
    """Top-bar info box for money, energy, and level."""

    label: str
    value: str
    center_x: float
    center_y: float
    width: float = 145
    height: float = 42
    fill_color: arcade.Color = arcade.color.BLACK_OLIVE
    border_color: arcade.Color = arcade.color.WHITE

    def __post_init__(self) -> None:
        self.sprite = arcade.SpriteSolidColor(int(self.width), int(self.height), self.fill_color)
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
        self.sprite.alpha = 210
        self.border = arcade.SpriteSolidColor(int(self.width + 4), int(self.height + 4), self.border_color)
        self.border.center_x = self.center_x
        self.border.center_y = self.center_y
        self.label_text = arcade.Text(
            self.label,
            self.center_x - self.width * 0.4,
            self.center_y + 8,
            arcade.color.LIGHT_GRAY,
            10,
            anchor_x="left",
            anchor_y="center",
        )
        self.value_text = arcade.Text(
            self.value,
            self.center_x - self.width * 0.4,
            self.center_y - 8,
            arcade.color.WHITE,
            14,
            anchor_x="left",
            anchor_y="center",
        )

    def draw(self) -> None:
        self.border.draw()
        self.sprite.draw()
        self.label_text.draw()
        self.value_text.draw()


class HomeButton:
    """A left-side navigation button with a press-and-release animation."""

    def __init__(
        self,
        label: str,
        center_x: float,
        center_y: float,
        on_activate: Callable[[float], None],
    ) -> None:
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.on_activate = on_activate
        self.base_width = HOME_BUTTON_WIDTH
        self.base_height = HOME_BUTTON_HEIGHT
        self.base_scale = 1.0
        self.target_scale = 1.0
        self.current_scale = 1.0
        self.press_started_at: Optional[float] = None
        self.pending_activation = False
        self.sprite = self._build_sprite()
        self.text = arcade.Text(
            label.title(),
            center_x,
            center_y,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            anchor_y="center",
        )

    def _build_sprite(self) -> arcade.Sprite:
        image_path = BUTTON_IMAGE_PATHS[self.label]
        if _path_exists(image_path):
            sprite = arcade.Sprite(str(image_path))
            sprite.center_x = self.center_x
            sprite.center_y = self.center_y
            sprite.width = self.base_width
            sprite.height = self.base_height
            return sprite

        sprite = arcade.SpriteSolidColor(
            self.base_width,
            self.base_height,
            arcade.color.DARK_SLATE_BLUE,
        )
        sprite.center_x = self.center_x
        sprite.center_y = self.center_y
        sprite.alpha = 230
        return sprite

    def hit_test(self, x: float, y: float) -> bool:
        return (
            abs(x - self.sprite.center_x) <= self.sprite.width / 2
            and abs(y - self.sprite.center_y) <= self.sprite.height / 2
        )

    def press(self, now: float) -> None:
        self.press_started_at = now
        self.pending_activation = True
        self.target_scale = PRESS_SHRINK_SCALE

    def update(self, dt: float, now: float) -> None:
        if self.press_started_at is None:
            self.current_scale += (1.0 - self.current_scale) * min(1.0, dt * 12)
        else:
            elapsed = now - self.press_started_at
            if elapsed < PRESS_ANIMATION_TIME / 2:
                self.current_scale = 1.0 - (1.0 - PRESS_SHRINK_SCALE) * (elapsed / (PRESS_ANIMATION_TIME / 2))
            elif elapsed < PRESS_ANIMATION_TIME:
                self.current_scale = PRESS_SHRINK_SCALE + (1.0 - PRESS_SHRINK_SCALE) * (
                    (elapsed - PRESS_ANIMATION_TIME / 2) / (PRESS_ANIMATION_TIME / 2)
                )
            else:
                self.current_scale = 1.0
                self.press_started_at = None
                if self.pending_activation:
                    self.pending_activation = False
                    self.on_activate(now)

        self.sprite.scale = self.current_scale
        self.text.font_size = max(11, int(16 * self.current_scale))

    def draw(self) -> None:
        self.sprite.draw()
        self.text.draw()


class BlankSectionView(arcade.View):
    """Empty placeholder screen for one of the future game areas."""

    def __init__(self, title: str, home_view_factory: Callable[[], arcade.View]) -> None:
        super().__init__()
        self.title = title
        self._home_view_factory = home_view_factory

    def on_show_view(self) -> None:
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self) -> None:
        self.clear()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self.window.show_view(self._home_view_factory())


class HomeView(arcade.View):
    """Main home screen with navigation and player status boxes."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.background_sprite = self._build_background_sprite()
        self.money_box = StatusBox("Money", "$120", 510, SCREEN_HEIGHT - 34)
        self.energy_box = StatusBox("Energy", "85%", 650, SCREEN_HEIGHT - 34)
        self.level_box = StatusBox("Level", "1", 740, SCREEN_HEIGHT - 34, width=100)
        self.buttons: list[HomeButton] = []
        self._pending_view_factory: Optional[Callable[[], arcade.View]] = None
        self._pending_view_started_at: Optional[float] = None
        self._build_buttons()

    def _build_background_sprite(self) -> arcade.Sprite:
        if _path_exists(BACKGROUND_IMAGE):
            sprite = arcade.Sprite(str(BACKGROUND_IMAGE))
            sprite.center_x = SCREEN_WIDTH / 2
            sprite.center_y = SCREEN_HEIGHT / 2
            sprite.width = SCREEN_WIDTH
            sprite.height = SCREEN_HEIGHT
            return sprite

        sprite = arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        sprite.center_x = SCREEN_WIDTH / 2
        sprite.center_y = SCREEN_HEIGHT / 2
        return sprite

    def _build_buttons(self) -> None:
        labels = [
            "settings",
            "social media",
            "closet",
            "clothing store",
            "activity center",
        ]
        for index, label in enumerate(labels):
            center_y = HOME_BUTTON_TOP - index * (HOME_BUTTON_HEIGHT + HOME_BUTTON_GAP)
        button = HomeButton(label, HOME_BUTTON_LEFT + HOME_BUTTON_WIDTH / 2, center_y, self._make_transition(label))
            self.buttons.append(button)

    def _make_transition(self, label: str) -> Callable[[float], None]:
        def transition(now: float) -> None:
            self._pending_view_factory = lambda: BlankSectionView(label.title(), self._home_factory)
            self._pending_view_started_at = now

        return transition

    def _home_factory(self) -> arcade.View:
        return HomeView()

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_draw(self) -> None:
        self.clear()
        self.background_sprite.draw()
        for box in (self.money_box, self.energy_box, self.level_box):
            box.draw()
        for button in self.buttons:
            button.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        now = arcade.get_time()
        for nav_button in self.buttons:
            if nav_button.hit_test(x, y):
                nav_button.press(now)
                self._pending_view_started_at = now
                break

    def on_update(self, delta_time: float) -> None:
        now = arcade.get_time()
        for nav_button in self.buttons:
            nav_button.update(delta_time, now)

        if self._pending_view_factory is not None and self._pending_view_started_at is not None:
            if now - self._pending_view_started_at >= PRESS_ANIMATION_TIME:
                self.window.show_view(self._pending_view_factory())
                self._pending_view_factory = None
                self._pending_view_started_at = None


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(HomeView())
    arcade.run()


if __name__ == "__main__":
    main()
