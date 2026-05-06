from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import random
import time
import warnings
from typing import Callable, Optional

warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API\.",
    module=r"pygame\.pkgdata",
)

import arcade

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

BASE_SCREEN_WIDTH = 800
BASE_SCREEN_HEIGHT = 600
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
SCREEN_TITLE = "Fashion Influencer Life"

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

# Base layout values expressed in the original 800x600 design space.
SIDE_BAR_X = 64
SIDE_BAR_Y = 270
SIDE_BAR_WIDTH = 84
SIDE_BAR_HEIGHT = 450

TOP_BAR_Y = 567
TOP_HUD_LEFT = 70
TOP_HUD_GAP = 120
TOP_CLOCK_RIGHT = 1466
TOP_CLOCK_DATE_Y = 577
TOP_CLOCK_TIME_Y = 555

HOME_BUTTON_WIDTH = 60
HOME_BUTTON_HEIGHT = 60
HOME_BUTTON_LEFT = 40
HOME_BUTTON_TOP = 448
HOME_BUTTON_GAP = 30

STATUS_LABEL_FONT_SIZE = 9
STATUS_VALUE_FONT_SIZE = 15
BUTTON_LABEL_FONT_SIZE = 12
WINDOW_TITLE_FONT_SIZE = 18
WINDOW_CLOSE_FONT_SIZE = 18
WINDOW_MARGIN = 19
WINDOW_HEADER_HEIGHT = 50
WINDOW_HEADER_TOP_PADDING = 6
WINDOW_TITLE_LEFT_PADDING = 18
WINDOW_CLOSE_HALF_SIZE = 13
WINDOW_CLOSE_OFFSET_X = 24
WINDOW_CLOSE_OFFSET_Y = 21
WINDOW_CLOSE_TEXT_OFFSET_Y = 1
SETTINGS_SLIDER_LEFT_PADDING = 36
SETTINGS_SLIDER_RIGHT_PADDING = 36
SETTINGS_SLIDER_TOP_PADDING = 115
SETTINGS_SLIDER_BAR_HEIGHT = 10
SETTINGS_SLIDER_KNOB_RADIUS = 13
SETTINGS_SLIDER_LABEL_SIZE = 18
SETTINGS_SLIDER_VALUE_SIZE = 16
UI_FONT_PATH = ":resources:/fonts/ttf/Kenney/Kenney_Future_Narrow.ttf"
UI_FONT_NAME = "Kenney Future Narrow"

arcade.load_font(UI_FONT_PATH)

THEME_DEEP_PURPLE = (170, 96, 200)
THEME_LAVENDER = (214, 154, 222)
THEME_SOFT_LILAC = (234, 189, 230)
THEME_PALE_PINK = (255, 221, 239)
THEME_TEXT_PURPLE = (106, 47, 130)
THEME_OVERLAY_ALPHA = 70

PRESS_ANIMATION_TIME = 0.18
PRESS_SHRINK_SCALE = 0.86

THRIFT_ITEM_NAMES = [
    "Vintage Blazer",
    "Silk Scarf",
    "Denim Skirt",
    "Pearl Cardigan",
    "Platform Boots",
    "Floral Dress",
    "Velvet Bag",
    "Striped Tee",
    "Corduroy Pants",
    "Lace Cami",
]


class BackgroundMusicPlaylist:
    """Play the asset folder's songs back-to-back and loop them forever."""

    def __init__(self, music_dir: Path) -> None:
        self.track_paths = sorted(
            path for path in music_dir.glob("*.mp3") if path.is_file()
        )
        self._sounds: list[object] = []
        self._channel: Optional[object] = None
        self._current_sound: Optional[object] = None
        self._started = False
        self._available = pygame is not None and bool(self.track_paths)
        self._volume = 0.7

    def start(self) -> None:
        if self._started or not self._available:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_reserved(1)
            self._sounds = []
            for path in self.track_paths:
                try:
                    self._sounds.append(pygame.mixer.Sound(str(path)))
                except pygame.error:
                    continue
            if not self._sounds:
                raise pygame.error("No playable music tracks were found.")
            self._channel = pygame.mixer.Channel(0)
            self._channel.set_volume(self._volume)
            self._current_sound = self._sounds[0]
            self._channel.play(self._current_sound)
            self._queue_next_track()
            self._started = True
        except pygame.error:
            self._available = False
            self._sounds = []
            self._channel = None
            self._current_sound = None

    def update(self) -> None:
        if not self._started or self._channel is None:
            return

        current_sound = self._channel.get_sound()
        if current_sound is None or current_sound is self._current_sound:
            return

        self._current_sound = current_sound
        self._queue_next_track()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        if self._channel is not None:
            self._channel.set_volume(self._volume)

    @property
    def volume(self) -> float:
        return self._volume

    def _queue_next_track(self) -> None:
        if self._channel is None or not self._sounds or self._current_sound is None:
            return

        try:
            current_index = self._sounds.index(self._current_sound)
        except ValueError:
            return

        next_index = (current_index + 1) % len(self._sounds)
        self._channel.queue(self._sounds[next_index])


@dataclass(frozen=True)
class GameLayout:
    """Scaled coordinates and sizes for the current window."""

    width: float
    height: float

    @property
    def scale_x(self) -> float:
        return self.width / BASE_SCREEN_WIDTH

    @property
    def scale_y(self) -> float:
        return self.height / BASE_SCREEN_HEIGHT

    @property
    def ui_scale(self) -> float:
        return min(self.scale_x, self.scale_y)

    def sx(self, value: float) -> float:
        return value * self.scale_x

    def sy(self, value: float) -> float:
        return value * self.scale_y

    def ss(self, value: float) -> float:
        return value * self.ui_scale

    @property
    def side_bar_x(self) -> float:
        return self.sx(SIDE_BAR_X)

    @property
    def side_bar_y(self) -> float:
        return self.sy(SIDE_BAR_Y)

    @property
    def side_bar_width(self) -> float:
        return self.sx(SIDE_BAR_WIDTH)

    @property
    def side_bar_height(self) -> float:
        return self.sy(SIDE_BAR_HEIGHT)

    @property
    def top_bar_y(self) -> float:
        return self.height - self.sy(33)

    @property
    def top_hud_left(self) -> float:
        return self.sx(TOP_HUD_LEFT)

    @property
    def top_hud_gap(self) -> float:
        return self.sx(TOP_HUD_GAP)

    @property
    def top_clock_right(self) -> float:
        return self.width - self.sx(34)

    @property
    def top_clock_date_y(self) -> float:
        return self.top_bar_y + self.sy(10)

    @property
    def top_clock_time_y(self) -> float:
        return self.top_bar_y - self.sy(12)

    @property
    def home_button_width(self) -> float:
        return self.ss(HOME_BUTTON_WIDTH)

    @property
    def home_button_height(self) -> float:
        return self.ss(HOME_BUTTON_HEIGHT)

    @property
    def home_button_left(self) -> float:
        return self.sx(HOME_BUTTON_LEFT)

    @property
    def home_button_top(self) -> float:
        return self.sy(HOME_BUTTON_TOP)

    @property
    def home_button_gap(self) -> float:
        return self.ss(HOME_BUTTON_GAP)

    @property
    def status_label_font_size(self) -> float:
        return self.ss(STATUS_LABEL_FONT_SIZE)

    @property
    def status_value_font_size(self) -> float:
        return self.ss(STATUS_VALUE_FONT_SIZE)

    @property
    def button_label_font_size(self) -> float:
        return self.ss(BUTTON_LABEL_FONT_SIZE)

    @property
    def window_title_font_size(self) -> float:
        return self.ss(WINDOW_TITLE_FONT_SIZE)

    @property
    def window_close_font_size(self) -> float:
        return self.ss(WINDOW_CLOSE_FONT_SIZE)

    @property
    def window_margin(self) -> float:
        return self.ss(WINDOW_MARGIN)

    @property
    def window_header_height(self) -> float:
        return self.sy(WINDOW_HEADER_HEIGHT)

    @property
    def window_header_top_padding(self) -> float:
        return self.sy(WINDOW_HEADER_TOP_PADDING)

    @property
    def window_title_left_padding(self) -> float:
        return self.sx(WINDOW_TITLE_LEFT_PADDING)

    @property
    def window_close_half_size(self) -> float:
        return self.ss(WINDOW_CLOSE_HALF_SIZE)

    @property
    def window_close_offset_x(self) -> float:
        return self.sx(WINDOW_CLOSE_OFFSET_X)

    @property
    def window_close_offset_y(self) -> float:
        return self.sy(WINDOW_CLOSE_OFFSET_Y)

    @property
    def window_close_text_offset_y(self) -> float:
        return self.sy(WINDOW_CLOSE_TEXT_OFFSET_Y)


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

    layout: GameLayout
    label: str
    value: str
    center_x: float
    center_y: float
    width: float = 132
    height: float = 42
    fill_color: arcade.Color = THEME_PALE_PINK
    border_color: arcade.Color = THEME_LAVENDER
    accent_color: arcade.Color = THEME_DEEP_PURPLE
    label_size: float = STATUS_LABEL_FONT_SIZE
    value_size: float = STATUS_VALUE_FONT_SIZE

    def __post_init__(self) -> None:
        self._build_visuals()

    def _build_visuals(self) -> None:
        self.shadow = DrawableSprite(
            _make_panel(
                self.center_x + self.layout.ss(3),
                self.center_y - self.layout.ss(3),
                self.width,
                self.height,
                THEME_DEEP_PURPLE,
                110,
            )
        )
        self.border = DrawableSprite(
            _make_panel(
                self.center_x,
                self.center_y,
                self.width + self.layout.ss(4),
                self.height + self.layout.ss(4),
                self.border_color,
                255,
            )
        )
        self.panel = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width, self.height, self.fill_color, 220))
        self.accent = DrawableSprite(
            _make_panel(
                self.center_x - self.width * 0.36,
                self.center_y,
                self.layout.ss(4),
                self.height - self.layout.ss(10),
                self.accent_color,
                255,
            )
        )
        if not hasattr(self, "label_text"):
            self.label_text = arcade.Text(
                self.label.upper(),
                self.center_x - self.width * 0.24,
                self.center_y + self.layout.sy(9),
                THEME_TEXT_PURPLE,
                self.label_size,
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            )
            self.value_text = arcade.Text(
                self.value,
                self.center_x - self.width * 0.24,
                self.center_y - self.layout.sy(8),
                THEME_TEXT_PURPLE,
                self.value_size,
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            )
        else:
            self.label_text.x = self.center_x - self.width * 0.24
            self.label_text.y = self.center_y + self.layout.sy(9)
            self.label_text.font_size = self.label_size
            self.value_text.x = self.center_x - self.width * 0.24
            self.value_text.y = self.center_y - self.layout.sy(8)
            self.value_text.font_size = self.value_size

    def update_layout(
        self,
        layout: GameLayout,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        label_size: float,
        value_size: float,
    ) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.label_size = label_size
        self.value_size = value_size
        self._build_visuals()

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
        layout: GameLayout,
        label: str,
        center_x: float,
        center_y: float,
        on_activate: Callable[[], None],
        active: bool = False,
    ) -> None:
        self.layout = layout
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.on_activate = on_activate
        self.press_started_at: Optional[float] = None
        self.pending_activation = False
        self.current_scale = 1.0
        self.is_active = active
        self.normal_sprite = DrawableSprite(self._build_sprite(active=False))
        self.active_sprite = DrawableSprite(self._build_sprite(active=True))
        self.sprite = self.active_sprite if active else self.normal_sprite
        self.show_label = not _path_exists(BUTTON_IMAGE_PATHS[self.label])
        self.text = arcade.Text(
            label.title(),
            center_x,
            center_y,
            THEME_TEXT_PURPLE,
            self.layout.button_label_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.update_layout(layout, center_x, center_y)

    def _build_sprite(self, active: bool) -> arcade.Sprite:
        image_path = BUTTON_ACTIVE_IMAGE_PATHS.get(self.label) if active else BUTTON_IMAGE_PATHS[self.label]
        fallback_color = THEME_LAVENDER if active else THEME_DEEP_PURPLE
        sprite = _make_sprite(
            image_path if image_path is not None else BUTTON_IMAGE_PATHS[self.label],
            self.center_x,
            self.center_y,
            self.layout.home_button_width,
            self.layout.home_button_height,
            fallback_color,
        )
        sprite.alpha = 230
        return sprite

    def update_layout(self, layout: GameLayout, center_x: float, center_y: float) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        for sprite in (self.normal_sprite, self.active_sprite):
            sprite.center_x = center_x
            sprite.center_y = center_y
            sprite.width = layout.home_button_width
            sprite.height = layout.home_button_height
            sprite.scale = self.current_scale
        self.sprite = self.active_sprite if self.is_active else self.normal_sprite
        self.text.x = center_x
        self.text.y = center_y
        self.text.font_size = max(11, int(layout.button_label_font_size * self.current_scale))

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active
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
            self.text.font_size = max(11, int(self.layout.button_label_font_size * self.current_scale))
            self.text.draw()


@dataclass
class ThriftFind:
    """One clickable clothing item in the thrifting mini-game."""

    name: str
    price: int
    style: int
    quality: int
    picked: bool = False

    @property
    def value(self) -> int:
        return self.style + self.quality

    @property
    def is_good_find(self) -> bool:
        return self.value >= self.price


class HomeView(arcade.View):
    """Main dashboard with button sprites and top status boxes."""

    def __init__(self) -> None:
        super().__init__()
        self.music = BackgroundMusicPlaylist(ASSETS_DIR)
        self.layout = GameLayout(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.background_color = THEME_DEEP_PURPLE
        self.background_sprite = DrawableSprite(self._build_background_sprite(self.layout))
        self.theme_overlay = DrawableSprite(_make_panel(self.layout.width / 2, self.layout.height / 2, self.layout.width, self.layout.height, THEME_SOFT_LILAC, THEME_OVERLAY_ALPHA))
        self.top_bar = DrawableSprite(_make_panel(self.layout.width / 2, self.layout.top_bar_y, self.layout.width, self.layout.sy(92), THEME_LAVENDER, 120))
        self.side_bar = DrawableSprite(_make_panel(self.layout.side_bar_x, self.layout.side_bar_y, self.layout.side_bar_width, self.layout.side_bar_height, THEME_LAVENDER, 220))
        self.money_box = StatusBox(self.layout, "Money", "$120", self.layout.top_hud_left, self.layout.top_bar_y, width=self.layout.ss(132), height=self.layout.ss(42), label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.energy_box = StatusBox(self.layout, "Energy", "85%", self.layout.top_hud_left + self.layout.top_hud_gap, self.layout.top_bar_y, width=self.layout.ss(132), height=self.layout.ss(42), label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.level_box = StatusBox(self.layout, "Level", "1", self.layout.top_hud_left + self.layout.top_hud_gap * 2, self.layout.top_bar_y, width=self.layout.ss(108), height=self.layout.ss(42), accent_color=THEME_DEEP_PURPLE, label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.date_text = arcade.Text(
            "",
            self.layout.top_clock_right,
            self.layout.top_clock_date_y,
            THEME_TEXT_PURPLE,
            self.layout.ss(14),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        self.time_text = arcade.Text(
            "",
            self.layout.top_clock_right,
            self.layout.top_clock_time_y,
            THEME_TEXT_PURPLE,
            self.layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        self.buttons: list[HomeButton] = []
        self.active_window: Optional[ComputerWindowOverlay] = None
        self._pending_action: Optional[Callable[[], None]] = None
        self._build_buttons()
        self._sync_clock_text()
        self._apply_layout(self.layout)

    def _build_background_sprite(self, layout: GameLayout) -> arcade.Sprite:
        return _make_sprite(
            BACKGROUND_IMAGE,
            layout.width / 2,
            layout.height / 2,
            layout.width,
            layout.height,
            THEME_DEEP_PURPLE,
        )

    def _sync_clock_text(self) -> None:
        now = datetime.now()
        self.date_text.text = now.strftime("%b %d, %Y")
        self.time_text.text = now.strftime("%I:%M %p").lstrip("0")

    def _build_buttons(self) -> None:
        labels = [
            "settings",
            "social media",
            "closet",
            "clothing store",
            "activity center",
        ]
        for index, label in enumerate(labels):
            center_y = self.layout.home_button_top - index * (self.layout.home_button_height + self.layout.home_button_gap)
            button = HomeButton(
                self.layout,
                label,
                self.layout.home_button_left + self.layout.home_button_width / 2,
                center_y,
                self._make_open_action(label),
            )
            self.buttons.append(button)

    def _apply_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        self.background_sprite.center_x = layout.width / 2
        self.background_sprite.center_y = layout.height / 2
        self.background_sprite.width = layout.width
        self.background_sprite.height = layout.height
        self.theme_overlay.center_x = layout.width / 2
        self.theme_overlay.center_y = layout.height / 2
        self.theme_overlay.width = layout.width
        self.theme_overlay.height = layout.height
        self.top_bar.center_x = layout.width / 2
        self.top_bar.center_y = layout.top_bar_y
        self.top_bar.width = layout.width
        self.top_bar.height = layout.sy(92)
        self.side_bar.center_x = layout.side_bar_x
        self.side_bar.center_y = layout.side_bar_y
        self.side_bar.width = layout.side_bar_width
        self.side_bar.height = layout.side_bar_height
        self.money_box.update_layout(
            layout,
            layout.top_hud_left,
            layout.top_bar_y,
            layout.ss(132),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.energy_box.update_layout(
            layout,
            layout.top_hud_left + layout.top_hud_gap,
            layout.top_bar_y,
            layout.ss(132),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.level_box.update_layout(
            layout,
            layout.top_hud_left + layout.top_hud_gap * 2,
            layout.top_bar_y,
            layout.ss(108),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.date_text.x = layout.top_clock_right
        self.date_text.y = layout.top_clock_date_y
        self.date_text.font_size = layout.ss(14)
        self.time_text.x = layout.top_clock_right
        self.time_text.y = layout.top_clock_time_y
        self.time_text.font_size = layout.ss(18)
        button_left = layout.home_button_left + layout.home_button_width / 2
        for index, button in enumerate(self.buttons):
            center_y = layout.home_button_top - index * (layout.home_button_height + layout.home_button_gap)
            button.update_layout(layout, button_left, center_y)
        if self.active_window is not None:
            self.active_window.update_layout(layout)

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
            self.layout,
            title=label.title(),
            on_close=lambda: self._close_window(label),
            music=self.music,
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
        self.music.start()
        if self.window is not None:
            self._apply_layout(GameLayout(self.window.width, self.window.height))

    def on_draw(self) -> None:
        self.clear()
        self.background_sprite.draw()
        self.theme_overlay.draw()
        self.top_bar.draw()
        self.side_bar.draw()
        self.money_box.draw()
        self.energy_box.draw()
        self.level_box.draw()
        self.date_text.draw()
        self.time_text.draw()
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
        self.music.update()
        self._sync_clock_text()
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

    def on_resize(self, width: float, height: float) -> None:
        self._apply_layout(GameLayout(width, height))


class ComputerWindowOverlay:
    """A draggable computer-style window drawn on top of the home screen."""

    def __init__(
        self,
        layout: GameLayout,
        title: str,
        on_close: Callable[[], None],
        music: Optional[BackgroundMusicPlaylist] = None,
    ) -> None:
        self.layout = layout
        self.title = title
        self.on_close = on_close
        self.music = music
        self.window_width = 0.0
        self.window_height = 0.0
        self.window_x = 0.0
        self.window_y = 0.0
        self.is_dragging = False
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        self.is_adjusting_volume = False
        self.activity_screen = "menu"
        self.thrift_budget = 35
        self.thrift_score = 0
        self.thrift_round = 1
        self.thrift_message = "Find the pieces with the best style and quality."
        self.thrift_finds: list[ThriftFind] = []
        self.title_text = arcade.Text(
            self.title,
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.window_title_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.close_text = arcade.Text(
            "x",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.window_close_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.settings_label_text = arcade.Text(
            "Music Volume",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.ss(SETTINGS_SLIDER_LABEL_SIZE),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.settings_value_text = arcade.Text(
            "",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.ss(SETTINGS_SLIDER_VALUE_SIZE),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        if self.title == "Activity Center":
            self._restock_thrift_rack()
        self.update_layout(layout)

    def _bounds(self) -> tuple[float, float, float, float]:
        left = self.window_x - self.window_width / 2
        right = self.window_x + self.window_width / 2
        bottom = self.window_y - self.window_height / 2
        top = self.window_y + self.window_height / 2
        return left, right, bottom, top

    def _header_bounds(self) -> tuple[float, float, float, float]:
        left, right, _, top = self._bounds()
        return left, right, top - self.layout.window_header_height, top - self.layout.window_header_top_padding

    def _close_bounds(self) -> tuple[float, float, float, float]:
        _, right, _, top = self._bounds()
        center_x = right - self.layout.window_close_offset_x
        center_y = top - self.layout.window_close_offset_y
        return (
            center_x - self.layout.window_close_half_size,
            center_x + self.layout.window_close_half_size,
            center_y - self.layout.window_close_half_size,
            center_y + self.layout.window_close_half_size,
        )

    def _sync_text_positions(self) -> None:
        left, right, _, top = self._bounds()
        _, _, header_bottom, header_top = self._header_bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        self.title_text.x = left + self.layout.window_title_left_padding
        self.title_text.y = (header_bottom + header_top) / 2
        self.close_text.x = (close_left + close_right) / 2
        self.close_text.y = (close_bottom + close_top) / 2 - self.layout.window_close_text_offset_y
        if self.title == "Settings":
            slider_left, slider_right, slider_center_y = self._slider_geometry()
            self.settings_label_text.x = slider_left
            self.settings_label_text.y = slider_center_y + self.layout.sy(30)
            self.settings_value_text.x = slider_right
            self.settings_value_text.y = slider_center_y + self.layout.sy(30)
            if self.music is not None:
                self.settings_value_text.text = f"{int(round(self.music.volume * 100))}%"

    def _slider_geometry(self) -> tuple[float, float, float]:
        left, right, _, top = self._bounds()
        slider_left = left + self.layout.sx(SETTINGS_SLIDER_LEFT_PADDING)
        slider_right = right - self.layout.sx(SETTINGS_SLIDER_RIGHT_PADDING)
        slider_center_y = top - self.layout.sy(SETTINGS_SLIDER_TOP_PADDING)
        return slider_left, slider_right, slider_center_y

    def _slider_bounds(self) -> tuple[float, float, float, float]:
        slider_left, slider_right, slider_center_y = self._slider_geometry()
        half_height = self.layout.sy(SETTINGS_SLIDER_BAR_HEIGHT) / 2
        return slider_left, slider_right, slider_center_y - half_height, slider_center_y + half_height

    def _slider_knob_center_x(self) -> float:
        slider_left, slider_right, _ = self._slider_geometry()
        if self.music is None:
            return slider_left
        return slider_left + (slider_right - slider_left) * self.music.volume

    def _set_music_volume_from_x(self, x: float) -> None:
        if self.music is None:
            return
        slider_left, slider_right, _ = self._slider_geometry()
        if slider_right <= slider_left:
            return
        volume = (x - slider_left) / (slider_right - slider_left)
        self.music.set_volume(volume)
        self.settings_value_text.text = f"{int(round(self.music.volume * 100))}%"

    def _restock_thrift_rack(self) -> None:
        self.thrift_round += 1
        self.thrift_budget = 35
        self.thrift_finds = []
        for name in random.sample(THRIFT_ITEM_NAMES, 4):
            style = random.randint(4, 12)
            quality = random.randint(4, 12)
            price = random.randint(6, 22)
            self.thrift_finds.append(ThriftFind(name, price, style, quality))
        self.thrift_message = "New rack! Click pieces worth more than they cost."

    def _activity_thrifting_button_bounds(self) -> tuple[float, float, float, float]:
        left, right, bottom, top = self._content_bounds()
        button_width = min(self.layout.sx(240), (right - left) * 0.7)
        button_height = min(self.layout.sy(70), (top - bottom) * 0.28)
        center_x = (left + right) / 2
        center_y = (bottom + top) / 2
        return (
            center_x - button_width / 2,
            center_x + button_width / 2,
            center_y - button_height / 2,
            center_y + button_height / 2,
        )

    def _thrift_back_button_bounds(self) -> tuple[float, float, float, float]:
        left, _, bottom, _ = self._content_bounds()
        button_width = self.layout.sx(88)
        button_height = self.layout.sy(30)
        return left, left + button_width, bottom, bottom + button_height

    def _content_bounds(self) -> tuple[float, float, float, float]:
        left, right, bottom, top = self._bounds()
        _, _, header_bottom, _ = self._header_bounds()
        pad = self.layout.ss(22)
        return left + pad, right - pad, bottom + pad, header_bottom - self.layout.sy(14)

    def _thrift_card_bounds(self, index: int) -> tuple[float, float, float, float]:
        left, right, bottom, top = self._content_bounds()
        gap = self.layout.ss(10)
        content_height = max(self.layout.sy(1), top - bottom)
        title_space = min(self.layout.sy(76), content_height * 0.32)
        bottom_space = min(self.layout.sy(42), content_height * 0.18)
        grid_top = top - title_space
        grid_bottom = bottom + bottom_space
        card_width = (right - left - gap) / 2
        card_height = max(self.layout.sy(1), (grid_top - grid_bottom - gap) / 2)
        row = index // 2
        col = index % 2
        card_left = left + col * (card_width + gap)
        card_top = grid_top - row * (card_height + gap)
        return card_left, card_left + card_width, card_top - card_height, card_top

    def _thrift_button_bounds(self) -> tuple[float, float, float, float]:
        left, right, bottom, _ = self._content_bounds()
        button_width = min(self.layout.sx(150), (right - left) * 0.42)
        button_height = self.layout.sy(30)
        button_right = right
        button_bottom = bottom
        return button_right - button_width, button_right, button_bottom, button_bottom + button_height

    def _draw_activity_center(self) -> None:
        left, right, _, top = self._content_bounds()
        title_size = self.layout.ss(22)
        body_size = self.layout.ss(14)
        small_size = self.layout.ss(11)
        self._draw_window_text(
            "Activity Center",
            (left + right) / 2,
            top - self.layout.sy(16),
            THEME_TEXT_PURPLE,
            title_size,
            anchor_x="center",
            anchor_y="top",
        )
        self._draw_window_text(
            "Choose an activity",
            (left + right) / 2,
            top - self.layout.sy(48),
            THEME_TEXT_PURPLE,
            small_size,
            anchor_x="center",
            anchor_y="top",
        )
        button_left, button_right, button_bottom, button_top = self._activity_thrifting_button_bounds()
        arcade.draw_lrbt_rectangle_filled(button_left, button_right, button_bottom, button_top, THEME_SOFT_LILAC)
        arcade.draw_lrbt_rectangle_outline(button_left, button_right, button_bottom, button_top, THEME_DEEP_PURPLE, 3)
        arcade.draw_circle_filled(
            button_left + self.layout.sx(34),
            (button_bottom + button_top) / 2,
            min(self.layout.ss(18), (button_top - button_bottom) * 0.28),
            THEME_LAVENDER,
        )
        self._draw_window_text(
            "Thrifting",
            (button_left + button_right) / 2 + self.layout.sx(14),
            (button_bottom + button_top) / 2,
            THEME_TEXT_PURPLE,
            body_size,
            anchor_x="center",
        )

    def _draw_window_text(
        self,
        text: str,
        x: float,
        y: float,
        color: arcade.Color,
        size: float,
        anchor_x: str = "left",
        anchor_y: str = "center",
    ) -> None:
        arcade.draw_text(
            text,
            x,
            y,
            color,
            max(8, int(size)),
            font_name=UI_FONT_NAME,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
        )

    def _draw_thrift_game(self) -> None:
        left, right, bottom, top = self._content_bounds()
        title_size = self.layout.ss(19)
        body_size = self.layout.ss(12)
        small_size = self.layout.ss(10)
        self._draw_window_text(
            "Thrift Challenge",
            left,
            top - self.layout.sy(10),
            THEME_TEXT_PURPLE,
            title_size,
            anchor_y="top",
        )
        self._draw_window_text(
            f"Budget ${self.thrift_budget}   Score {self.thrift_score}",
            right,
            top - self.layout.sy(10),
            THEME_TEXT_PURPLE,
            body_size,
            anchor_x="right",
            anchor_y="top",
        )
        self._draw_window_text(
            self.thrift_message,
            left,
            top - self.layout.sy(42),
            THEME_TEXT_PURPLE,
            small_size,
            anchor_y="top",
        )

        for index, item in enumerate(self.thrift_finds):
            card_left, card_right, card_bottom, card_top = self._thrift_card_bounds(index)
            fill = THEME_SOFT_LILAC if item.picked else THEME_PALE_PINK
            border = THEME_LAVENDER if item.picked else THEME_DEEP_PURPLE
            arcade.draw_lrbt_rectangle_filled(card_left, card_right, card_bottom, card_top, fill)
            arcade.draw_lrbt_rectangle_outline(card_left, card_right, card_bottom, card_top, border, 2)

            tag_width = min(self.layout.sx(64), (card_right - card_left) * 0.36)
            tag_height = min(self.layout.sy(24), (card_top - card_bottom) * 0.3)
            arcade.draw_lrbt_rectangle_filled(
                card_right - tag_width,
                card_right,
                card_top - tag_height,
                card_top,
                THEME_LAVENDER,
            )
            self._draw_window_text(
                f"${item.price}",
                card_right - tag_width / 2,
                card_top - tag_height / 2,
                THEME_TEXT_PURPLE,
                body_size,
                anchor_x="center",
            )

            card_width = card_right - card_left
            card_height = card_top - card_bottom
            item_width = min(card_width * 0.32, self.layout.sx(52))
            item_height = min(card_height * 0.42, self.layout.sy(44))
            item_center_x = card_left + self.layout.sx(18) + item_width / 2
            item_center_y = card_bottom + card_height * 0.48
            item_left = max(card_left + self.layout.sx(8), item_center_x - item_width / 2)
            item_right = min(card_right - self.layout.sx(8), item_center_x + item_width / 2)
            item_bottom_padding = min(self.layout.sy(28), card_height * 0.32)
            item_top_padding = min(self.layout.sy(30), card_height * 0.36)
            item_bottom = max(card_bottom + item_bottom_padding, item_center_y - item_height / 2)
            item_top = min(card_top - item_top_padding, item_center_y + item_height / 2)
            item_top = max(item_bottom + self.layout.sy(1), item_top)
            arcade.draw_lrbt_rectangle_filled(item_left, item_right, item_bottom, item_top, THEME_LAVENDER)
            arcade.draw_triangle_filled(
                item_left,
                item_top,
                item_right,
                item_top,
                (item_left + item_right) / 2,
                min(card_top - self.layout.sy(10), item_top + self.layout.sy(16)),
                THEME_DEEP_PURPLE,
            )

            name = item.name if len(item.name) <= 16 else item.name[:15] + "."
            self._draw_window_text(
                name,
                card_left + self.layout.sx(10),
                card_top - self.layout.sy(16),
                THEME_TEXT_PURPLE,
                body_size,
            )
            self._draw_window_text(
                f"Style {item.style}",
                card_left + max(self.layout.sx(10), item_width + self.layout.sx(22)),
                card_bottom + self.layout.sy(38),
                THEME_TEXT_PURPLE,
                small_size,
            )
            self._draw_window_text(
                f"Quality {item.quality}",
                card_left + max(self.layout.sx(10), item_width + self.layout.sx(22)),
                card_bottom + self.layout.sy(20),
                THEME_TEXT_PURPLE,
                small_size,
            )
            if item.picked:
                verdict = "closet win" if item.is_good_find else "leftover regret"
                self._draw_window_text(
                    verdict,
                    card_right - self.layout.sx(10),
                    card_bottom + self.layout.sy(20),
                    THEME_TEXT_PURPLE,
                    small_size,
                    anchor_x="right",
                )

        button_left, button_right, button_bottom, button_top = self._thrift_button_bounds()
        arcade.draw_lrbt_rectangle_filled(button_left, button_right, button_bottom, button_top, THEME_LAVENDER)
        arcade.draw_lrbt_rectangle_outline(button_left, button_right, button_bottom, button_top, THEME_DEEP_PURPLE, 2)
        self._draw_window_text(
            "New Rack",
            (button_left + button_right) / 2,
            (button_bottom + button_top) / 2,
            THEME_TEXT_PURPLE,
            body_size,
            anchor_x="center",
        )
        back_left, back_right, back_bottom, back_top = self._thrift_back_button_bounds()
        arcade.draw_lrbt_rectangle_filled(back_left, back_right, back_bottom, back_top, THEME_SOFT_LILAC)
        arcade.draw_lrbt_rectangle_outline(back_left, back_right, back_bottom, back_top, THEME_DEEP_PURPLE, 2)
        self._draw_window_text(
            "Back",
            (back_left + back_right) / 2,
            (back_bottom + back_top) / 2,
            THEME_TEXT_PURPLE,
            body_size,
            anchor_x="center",
        )

    def _hit_test_activity_center(self, x: float, y: float) -> bool:
        if self.title != "Activity Center":
            return False
        if self.activity_screen == "thrifting":
            return self._hit_test_thrift_game(x, y)
        button_left, button_right, button_bottom, button_top = self._activity_thrifting_button_bounds()
        if button_left <= x <= button_right and button_bottom <= y <= button_top:
            self.activity_screen = "thrifting"
            self.thrift_message = "Pick the hidden gems before your budget runs out."
            return True
        return False

    def _hit_test_thrift_game(self, x: float, y: float) -> bool:
        if self.title != "Activity Center" or self.activity_screen != "thrifting":
            return False
        back_left, back_right, back_bottom, back_top = self._thrift_back_button_bounds()
        if back_left <= x <= back_right and back_bottom <= y <= back_top:
            self.activity_screen = "menu"
            return True
        button_left, button_right, button_bottom, button_top = self._thrift_button_bounds()
        if button_left <= x <= button_right and button_bottom <= y <= button_top:
            self._restock_thrift_rack()
            return True
        for index, item in enumerate(self.thrift_finds):
            card_left, card_right, card_bottom, card_top = self._thrift_card_bounds(index)
            if card_left <= x <= card_right and card_bottom <= y <= card_top:
                if item.picked:
                    self.thrift_message = "You already checked that rack tag."
                    return True
                item.picked = True
                if self.thrift_budget < item.price:
                    self.thrift_message = "Not enough budget left for that piece."
                    return True
                self.thrift_budget -= item.price
                if item.is_good_find:
                    self.thrift_score += item.value - item.price + 5
                    self.thrift_message = f"{item.name} is a treasure."
                else:
                    self.thrift_score = max(0, self.thrift_score - 3)
                    self.thrift_message = f"{item.name} was cute, but overpriced."
                return True
        return False

    def update_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        self.window_width = max(layout.ss(240), min(layout.sx(560), layout.width - layout.window_margin * 2))
        self.window_height = max(layout.ss(180), min(layout.sy(390), layout.height - layout.window_margin * 2))
        self._set_center(layout.width / 2, layout.height / 2 - layout.sy(8))
        self.title_text.font_size = layout.window_title_font_size
        self.close_text.font_size = layout.window_close_font_size
        self.settings_label_text.font_size = layout.ss(SETTINGS_SLIDER_LABEL_SIZE)
        self.settings_value_text.font_size = layout.ss(SETTINGS_SLIDER_VALUE_SIZE)

    def _clamp_position(self, center_x: float, center_y: float) -> tuple[float, float]:
        half_width = self.window_width / 2
        half_height = self.window_height / 2
        min_x = half_width + self.layout.window_margin
        max_x = self.layout.width - half_width - self.layout.window_margin
        min_y = half_height + self.layout.window_margin
        max_y = self.layout.height - half_height - self.layout.window_margin
        return (
            max(min_x, min(center_x, max_x)),
            max(min_y, min(center_y, max_y)),
        )

    def _set_center(self, center_x: float, center_y: float) -> None:
        self.window_x, self.window_y = self._clamp_position(center_x, center_y)
        self._sync_text_positions()

    def _close(self) -> None:
        self.on_close()

    def on_draw(self) -> None:
        left, right, bottom, top = self._bounds()
        header_left, header_right, header_bottom, header_top = self._header_bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        shadow_offset = self.layout.ss(5)
        arcade.draw_lrbt_rectangle_filled(
            left + shadow_offset,
            right + shadow_offset,
            bottom - shadow_offset,
            top - shadow_offset,
            THEME_DEEP_PURPLE,
        )
        arcade.draw_lrbt_rectangle_filled(
            left,
            right,
            bottom,
            top,
            THEME_PALE_PINK,
        )
        arcade.draw_lrbt_rectangle_outline(
            left,
            right,
            bottom,
            top,
            THEME_DEEP_PURPLE,
            3,
        )
        arcade.draw_lrbt_rectangle_filled(
            header_left,
            header_right,
            header_bottom,
            header_top,
            THEME_LAVENDER,
        )
        self.title_text.draw()
        arcade.draw_lrbt_rectangle_filled(
            close_left,
            close_right,
            close_bottom,
            close_top,
            THEME_SOFT_LILAC,
        )
        self.close_text.draw()
        if self.title == "Settings":
            slider_left, slider_right, slider_bottom, slider_top = self._slider_bounds()
            knob_x = self._slider_knob_center_x()
            knob_y = (slider_bottom + slider_top) / 2
            arcade.draw_lrbt_rectangle_filled(
                slider_left,
                slider_right,
                slider_bottom,
                slider_top,
                THEME_LAVENDER,
            )
            arcade.draw_lrbt_rectangle_outline(
                slider_left,
                slider_right,
                slider_bottom,
                slider_top,
                THEME_DEEP_PURPLE,
                2,
            )
            arcade.draw_circle_filled(
                knob_x,
                knob_y,
                self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS),
                THEME_DEEP_PURPLE,
            )
            arcade.draw_circle_outline(
                knob_x,
                knob_y,
                self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS),
                THEME_PALE_PINK,
                2,
            )
            self.settings_label_text.draw()
            self.settings_value_text.draw()
        elif self.title == "Activity Center":
            if self.activity_screen == "thrifting":
                self._draw_thrift_game()
            else:
                self._draw_activity_center()

    def draw(self) -> None:
        self.on_draw()

    def _hit_test_slider(self, x: float, y: float) -> bool:
        if self.title != "Settings":
            return False
        left, right, bottom, top = self._slider_bounds()
        if left <= x <= right and bottom <= y <= top:
            return True
        knob_x = self._slider_knob_center_x()
        knob_y = (bottom + top) / 2
        knob_radius = self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS) * 1.3
        return (x - knob_x) ** 2 + (y - knob_y) ** 2 <= knob_radius**2

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
            if self._hit_test_slider(x, y):
                self.is_adjusting_volume = True
                self._set_music_volume_from_x(x)
                return True
            if self._hit_test_activity_center(x, y):
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
        elif self.is_adjusting_volume and buttons & arcade.MOUSE_BUTTON_LEFT:
            self._set_music_volume_from_x(x)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_dragging = False
            self.is_adjusting_volume = False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._close()

    def close(self) -> None:
        self._close()

    def on_resize(self, width: float, height: float) -> None:
        self.update_layout(GameLayout(width, height))




    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Mouse Follow Sprite")

        self.player = None
        self.player_list = None

        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):
        # Create sprite
        self.player = arcade.Sprite("assets/my_sprite.png", scale=0.3)
        self.player.center_x = 400
        self.player.center_y = 300

        # Put sprite in a SpriteList (required for drawing)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, delta_time):
        # Smooth follow toward mouse
        self.player.center_x += (self.mouse_x - self.player.center_x) * 0.1
        self.player.center_y += (self.mouse_y - self.player.center_y) * 0.1

    def on_draw(self):
        self.clear()
        self.player_list.draw()




def main() -> None:
    """Start the game window."""
    display_width, display_height = arcade.get_display_size()
    window = arcade.Window(
        min(DEFAULT_WINDOW_WIDTH, display_width),
        min(DEFAULT_WINDOW_HEIGHT, display_height),
        SCREEN_TITLE,
        resizable=True,
        center_window=True,
    )
    window.show_view(HomeView())
    arcade.run()


if __name__ == "__main__":
    main()
