from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable, Optional

import arcade

BASE_SCREEN_WIDTH = 800
BASE_SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Fashion Influencer Life"

SCALE_X = SCREEN_WIDTH / BASE_SCREEN_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_SCREEN_HEIGHT
UI_SCALE = min(SCALE_X, SCALE_Y)


def _sx(value: float) -> float:
    return value * SCALE_X


def _sy(value: float) -> float:
    return value * SCALE_Y


def _ss(value: float) -> float:
    return value * UI_SCALE

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BACKGROUND_IMAGE = ASSETS_DIR / "home_background.png"

BUTTON_IMAGE_PATHS = {
    "settings": ASSETS_DIR / "settings_button.png",
    "social media": ASSETS_DIR / "social_media_button.png",
    "closet": ASSETS_DIR / "closet_button.png",
    "clothing store": ASSETS_DIR / "clothing_store_button.png",
    "activity center": ASSETS_DIR / "activity_center_button.png",
}

BUTTON_ACTIVE_IMAGE_PATHS = {
    "social media": ASSETS_DIR / "social_media_button_active.png",
}

SIDE_BAR_X = _sx(64)
SIDE_BAR_Y = _sy(300)
SIDE_BAR_WIDTH = _sx(84)
SIDE_BAR_HEIGHT = _sy(410)

TOP_BAR_Y = SCREEN_HEIGHT - _sy(34)

HOME_BUTTON_WIDTH = _ss(60)
HOME_BUTTON_HEIGHT = _ss(60)
HOME_BUTTON_LEFT = _sx(40)
HOME_BUTTON_TOP = _sy(452)
HOME_BUTTON_GAP = _ss(15)

STATUS_LABEL_FONT_SIZE = _ss(9)
STATUS_VALUE_FONT_SIZE = _ss(15)
BUTTON_LABEL_FONT_SIZE = _ss(12)
WINDOW_TITLE_FONT_SIZE = _ss(18)
WINDOW_CLOSE_FONT_SIZE = _ss(18)
WINDOW_MARGIN = _ss(19)
WINDOW_HEADER_HEIGHT = _sy(50)
WINDOW_HEADER_TOP_PADDING = _sy(6)
WINDOW_TITLE_LEFT_PADDING = _sx(18)
WINDOW_CLOSE_HALF_SIZE = _ss(13)
WINDOW_CLOSE_OFFSET_X = _sx(24)
WINDOW_CLOSE_OFFSET_Y = _sy(21)
WINDOW_CLOSE_TEXT_OFFSET_Y = _sy(1)

PRESS_ANIMATION_TIME = 0.18
PRESS_SHRINK_SCALE = 0.86


def _current_time() -> float:
    """Return a monotonic timestamp for animation timing."""
    return time.perf_counter()


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


def _make_panel(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fill_color: arcade.Color,
    alpha: int,
) -> arcade.Sprite:
    sprite = arcade.SpriteSolidColor(int(width), int(height), fill_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    sprite.alpha = alpha
    return sprite


class DrawableSprite:
    """Small wrapper that renders a single sprite through a SpriteList."""

    def __init__(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(sprite)

    def draw(self) -> None:
        self._sprite_list.draw()

    def collides_with_point(self, point: tuple[float, float]) -> bool:
        return self._sprite.collides_with_point(point)

    @property
    def sprite(self) -> arcade.Sprite:
        return self._sprite

    @property
    def center_x(self) -> float:
        return self._sprite.center_x

    @center_x.setter
    def center_x(self, value: float) -> None:
        self._sprite.center_x = value

    @property
    def center_y(self) -> float:
        return self._sprite.center_y

    @center_y.setter
    def center_y(self, value: float) -> None:
        self._sprite.center_y = value

    @property
    def width(self) -> float:
        return self._sprite.width

    @width.setter
    def width(self, value: float) -> None:
        self._sprite.width = value

    @property
    def height(self) -> float:
        return self._sprite.height

    @height.setter
    def height(self, value: float) -> None:
        self._sprite.height = value

    @property
    def scale(self) -> float:
        return self._sprite.scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._sprite.scale = value

    @property
    def alpha(self) -> int:
        return self._sprite.alpha

    @alpha.setter
    def alpha(self, value: int) -> None:
        self._sprite.alpha = value

    def replace(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list.clear()
        self._sprite_list.append(sprite)


@dataclass
class StatusBox:
    """Small HUD block for money, energy, or level."""

    label: str
    value: str
    center_x: float
    center_y: float
    width: float = _ss(132)
    height: float = _ss(42)
    fill_color: arcade.Color = arcade.color.DARK_SLATE_GRAY
    border_color: arcade.Color = arcade.color.WHITE
    accent_color: arcade.Color = arcade.color.DARK_SEA_GREEN
    label_size: float = STATUS_LABEL_FONT_SIZE
    value_size: float = STATUS_VALUE_FONT_SIZE

    def __post_init__(self) -> None:
        self.shadow = DrawableSprite(_make_panel(self.center_x + _ss(3), self.center_y - _ss(3), self.width, self.height, arcade.color.BLACK, 110))
        self.border = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width + _ss(4), self.height + _ss(4), self.border_color, 255))
        self.panel = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width, self.height, self.fill_color, 220))
        self.accent = DrawableSprite(_make_panel(self.center_x - self.width * 0.36, self.center_y, _ss(4), self.height - _ss(10), self.accent_color, 255))
        self.label_text = arcade.Text(
            self.label.upper(),
            self.center_x - self.width * 0.24,
            self.center_y + _sy(9),
            arcade.color.LIGHT_GRAY,
            self.label_size,
            anchor_x="left",
            anchor_y="center",
        )
        self.value_text = arcade.Text(
            self.value,
            self.center_x - self.width * 0.24,
            self.center_y - _sy(8),
            arcade.color.WHITE,
            self.value_size,
            anchor_x="left",
            anchor_y="center",
        )

    def draw(self) -> None:
        self.shadow.draw()
        self.border.draw()
        self.panel.draw()
        self.accent.draw()
        self.label_text.draw()
        self.value_text.draw()


class HomeButton:
    """A left-side navigation button with a press animation and two visual states."""

    def __init__(
        self,
        label: str,
        center_x: float,
        center_y: float,
        on_activate: Callable[[], None],
        active: bool = False,
    ) -> None:
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.on_activate = on_activate
        self.press_started_at: Optional[float] = None
        self.pending_activation = False
        self.current_scale = 1.0
        self.normal_sprite = DrawableSprite(self._build_sprite(active=False))
        self.active_sprite = DrawableSprite(self._build_sprite(active=True))
        self.sprite = self.active_sprite if active else self.normal_sprite
        self.show_label = not _path_exists(BUTTON_IMAGE_PATHS[self.label])
        self.text = arcade.Text(
            label.title(),
            center_x,
            center_y,
            arcade.color.WHITE,
            BUTTON_LABEL_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
        )

    def _build_sprite(self, active: bool) -> arcade.Sprite:
        image_path = BUTTON_ACTIVE_IMAGE_PATHS.get(self.label) if active else BUTTON_IMAGE_PATHS[self.label]
        fallback_color = arcade.color.TAN if active else arcade.color.DARK_SLATE_BLUE
        sprite = _make_sprite(image_path if image_path is not None else BUTTON_IMAGE_PATHS[self.label], self.center_x, self.center_y, HOME_BUTTON_WIDTH, HOME_BUTTON_HEIGHT, fallback_color)
        sprite.alpha = 230
        return sprite

    def set_active(self, is_active: bool) -> None:
        self.sprite = self.active_sprite if is_active else self.normal_sprite
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
        self.sprite.scale = self.current_scale

    def hit_test(self, x: float, y: float) -> bool:
        return self.sprite.collides_with_point((x, y))

    def press(self, now: float) -> None:
        self.press_started_at = now
        self.pending_activation = True

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
                    self.on_activate()

        self.sprite.scale = self.current_scale

    def draw(self) -> None:
        self.sprite.draw()
        if self.show_label:
            self.text.font_size = max(11, int(BUTTON_LABEL_FONT_SIZE * self.current_scale))
            self.text.draw()


class HomeView(arcade.View):
    """Main dashboard with button sprites and top status boxes."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.background_sprite = DrawableSprite(self._build_background_sprite())
        self.top_bar = DrawableSprite(_make_panel(SCREEN_WIDTH / 2, TOP_BAR_Y, SCREEN_WIDTH, _sy(92), arcade.color.BLACK, 100))
        self.side_bar = DrawableSprite(_make_panel(SIDE_BAR_X, SIDE_BAR_Y, SIDE_BAR_WIDTH, SIDE_BAR_HEIGHT, arcade.color.DARK_SLATE_GRAY, 205))
        self.money_box = StatusBox("Money", "$120", _sx(410), TOP_BAR_Y)
        self.energy_box = StatusBox("Energy", "85%", _sx(558), TOP_BAR_Y)
        self.level_box = StatusBox("Level", "1", _sx(699), TOP_BAR_Y, width=_ss(108), accent_color=arcade.color.TAN)
        self.buttons: list[HomeButton] = []
        self.active_window: Optional[ComputerWindowOverlay] = None
        self._pending_action: Optional[Callable[[], None]] = None
        self._build_buttons()

    def _build_background_sprite(self) -> arcade.Sprite:
        return _make_sprite(
            BACKGROUND_IMAGE,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY,
        )

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
            button = HomeButton(label, HOME_BUTTON_LEFT + HOME_BUTTON_WIDTH / 2, center_y, self._make_open_action(label))
            self.buttons.append(button)

    def _make_open_action(self, label: str) -> Callable[[], None]:
        def open_window() -> None:
            if self.active_window is not None and self.active_window.title == label.title():
                window = self.active_window
                self._pending_action = window.close
                return
            self._pending_action = lambda: self._open_window(label)

        return open_window

    def _open_window(self, label: str) -> None:
        if self.active_window is not None and self.active_window.title == "Social Media" and label != "social media":
            self._set_button_active("social media", False)
        if label == "social media":
            self._set_button_active(label, True)
        self.active_window = ComputerWindowOverlay(
            title=label.title(),
            on_close=lambda: self._close_window(label),
        )

    def _set_button_active(self, label: str, is_active: bool) -> None:
        for button in self.buttons:
            if button.label == label:
                button.set_active(is_active)
                break

    def _close_window(self, label: str) -> None:
        self.active_window = None
        if label == "social media":
            self._set_button_active(label, False)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_draw(self) -> None:
        self.clear()
        self.background_sprite.draw()
        self.top_bar.draw()
        self.side_bar.draw()
        self.money_box.draw()
        self.energy_box.draw()
        self.level_box.draw()
        for button in self.buttons:
            button.draw()
        if self.active_window is not None:
            self.active_window.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.active_window is not None and self.active_window.on_mouse_press(x, y, button, modifiers):
            return

        now = _current_time()
        for nav_button in self.buttons:
            if nav_button.hit_test(x, y):
                if nav_button.label == "social media":
                    nav_button.set_active(True)
                nav_button.press(now)
                break

    def on_update(self, delta_time: float) -> None:
        now = _current_time()
        for nav_button in self.buttons:
            nav_button.update(delta_time, now)

        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            action()

    def on_mouse_drag(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        buttons: int,
        modifiers: int,
    ) -> None:
        if self.active_window is not None:
            self.active_window.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.active_window is not None:
            self.active_window.on_mouse_release(x, y, button, modifiers)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE and self.active_window is not None:
            self.active_window.close()


class ComputerWindowOverlay:
    """A draggable computer-style window drawn on top of the home screen."""

    def __init__(self, title: str, on_close: Callable[[], None]) -> None:
        self.title = title
        self.on_close = on_close
        self.window_width = _sx(560)
        self.window_height = _sy(390)
        self.window_x = SCREEN_WIDTH / 2
        self.window_y = SCREEN_HEIGHT / 2 - _sy(8)
        self.is_dragging = False
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        self.title_text = arcade.Text(
            self.title,
            self.window_x - self.window_width / 2 + WINDOW_TITLE_LEFT_PADDING,
            self.window_y + self.window_height / 2 - _sy(38),
            arcade.color.WHITE,
            WINDOW_TITLE_FONT_SIZE,
            anchor_x="left",
            anchor_y="center",
        )
        self.close_text = arcade.Text(
            "x",
            self.window_x + self.window_width / 2 - WINDOW_CLOSE_OFFSET_X,
            self.window_y + self.window_height / 2 - WINDOW_CLOSE_OFFSET_Y - WINDOW_CLOSE_TEXT_OFFSET_Y,
            arcade.color.WHITE,
            WINDOW_CLOSE_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
        )
        self._sync_text_positions()

    def _close(self) -> None:
        self.on_close()

    def _bounds(self) -> tuple[float, float, float, float]:
        left = self.window_x - self.window_width / 2
        right = self.window_x + self.window_width / 2
        bottom = self.window_y - self.window_height / 2
        top = self.window_y + self.window_height / 2
        return left, right, bottom, top

    def _header_bounds(self) -> tuple[float, float, float, float]:
        left, right, _, top = self._bounds()
        return left, right, top - WINDOW_HEADER_HEIGHT, top - WINDOW_HEADER_TOP_PADDING

    def _close_bounds(self) -> tuple[float, float, float, float]:
        _, right, _, top = self._bounds()
        center_x = right - WINDOW_CLOSE_OFFSET_X
        center_y = top - WINDOW_CLOSE_OFFSET_Y
        return (
            center_x - WINDOW_CLOSE_HALF_SIZE,
            center_x + WINDOW_CLOSE_HALF_SIZE,
            center_y - WINDOW_CLOSE_HALF_SIZE,
            center_y + WINDOW_CLOSE_HALF_SIZE,
        )

    def _sync_text_positions(self) -> None:
        left, right, _, top = self._bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        self.title_text.x = left + WINDOW_TITLE_LEFT_PADDING
        self.title_text.y = top - _sy(38)
        self.close_text.x = (close_left + close_right) / 2
        self.close_text.y = (close_bottom + close_top) / 2 - WINDOW_CLOSE_TEXT_OFFSET_Y

    def _clamp_position(self, center_x: float, center_y: float) -> tuple[float, float]:
        half_width = self.window_width / 2
        half_height = self.window_height / 2
        min_x = half_width + WINDOW_MARGIN
        max_x = SCREEN_WIDTH - half_width - WINDOW_MARGIN
        min_y = half_height + WINDOW_MARGIN
        max_y = SCREEN_HEIGHT - half_height - WINDOW_MARGIN
        return (
            max(min_x, min(center_x, max_x)),
            max(min_y, min(center_y, max_y)),
        )

    def _set_center(self, center_x: float, center_y: float) -> None:
        self.window_x, self.window_y = self._clamp_position(center_x, center_y)
        self._sync_text_positions()

    def on_draw(self) -> None:
        left, right, bottom, top = self._bounds()
        header_left, header_right, header_bottom, header_top = self._header_bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        shadow_offset = _ss(5)
        arcade.draw_lrbt_rectangle_filled(
            left + shadow_offset,
            right + shadow_offset,
            bottom - shadow_offset,
            top - shadow_offset,
            arcade.color.BLACK,
        )
        arcade.draw_lrbt_rectangle_filled(
            left,
            right,
            bottom,
            top,
            arcade.color.BEIGE,
        )
        arcade.draw_lrbt_rectangle_outline(
            left,
            right,
            bottom,
            top,
            arcade.color.WHITE,
            3,
        )
        arcade.draw_lrbt_rectangle_filled(
            header_left,
            header_right,
            header_bottom,
            header_top,
            arcade.color.BLACK_OLIVE,
        )
        self.title_text.draw()
        arcade.draw_lrbt_rectangle_filled(
            close_left,
            close_right,
            close_bottom,
            close_top,
            arcade.color.RED_ORANGE,
        )
        self.close_text.draw()

    def draw(self) -> None:
        self.on_draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False

        close_left, close_right, close_bottom, close_top = self._close_bounds()
        if close_left <= x <= close_right and close_bottom <= y <= close_top:
            self._close()
            return True

        left, right, _, top = self._bounds()
        header_left, header_right, header_bottom, header_top = self._header_bounds()
        bottom = self.window_y - self.window_height / 2
        if left <= x <= right and bottom <= y <= top:
            if header_left <= x <= header_right and header_bottom <= y <= header_top:
                self.is_dragging = True
                self.drag_offset_x = x - self.window_x
                self.drag_offset_y = y - self.window_y
                return True
            return True
        return False

    def on_mouse_drag(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        buttons: int,
        modifiers: int,
    ) -> None:
        if self.is_dragging and buttons & arcade.MOUSE_BUTTON_LEFT:
            self._set_center(x - self.drag_offset_x, y - self.drag_offset_y)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_dragging = False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._close()

    def close(self) -> None:
        self._close()


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(HomeView())
    arcade.run()


if __name__ == "__main__":
    main()
