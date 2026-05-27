from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Final


PROJECT_ROOT: Final = Path(__file__).resolve().parent
GAME_FILE: Final = PROJECT_ROOT / "game.py"
ASSETS_DIR: Final = PROJECT_ROOT / "assets"
DIST_DIR: Final = PROJECT_ROOT / "dist"
BUILD_DIR: Final = PROJECT_ROOT / "build"


def _data_separator() -> str:
    return ";" if sys.platform.startswith("win") else ":"


def _bundle_name(target: str) -> str:
    return f"SustainableFashionInfluencerLife-{target}"


def _run_pyinstaller(target: str) -> None:
    if shutil.which("pyinstaller") is None:
        raise SystemExit(
            "PyInstaller is not installed. Install it with `pip install pyinstaller` "
            "and try again."
        )

    bundle_name = _bundle_name(target)
    subprocess.run(
        [
            "pyinstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--windowed",
            "--name",
            bundle_name,
            "--add-data",
            f"{ASSETS_DIR}{_data_separator()}assets",
            str(GAME_FILE),
        ],
        check=True,
        cwd=PROJECT_ROOT,
    )


def _create_dmg(app_path: Path, dmg_path: Path) -> None:
    if shutil.which("hdiutil") is None:
        raise SystemExit("hdiutil is not available. This build must run on macOS.")

    if dmg_path.exists():
        dmg_path.unlink()

    subprocess.run(
        [
            "hdiutil",
            "create",
            "-volname",
            app_path.stem,
            "-srcfolder",
            str(app_path),
            "-ov",
            "-format",
            "UDZO",
            str(dmg_path),
        ],
        check=True,
        cwd=PROJECT_ROOT,
    )


def _bundle_path(target: str) -> Path:
    if target == "mac":
        return DIST_DIR / f"{_bundle_name(target)}.app"
    if target == "mac-dmg":
        return DIST_DIR / f"{_bundle_name('mac')}.dmg"
    if target == "windows":
        return DIST_DIR / f"{_bundle_name(target)}.exe"
    return DIST_DIR / _bundle_name(target)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a release bundle for Sustainable Fashion Influencer Life."
    )
    parser.add_argument(
        "target",
        choices=("mac", "mac-dmg", "windows"),
        help="The release bundle name to create.",
    )
    args = parser.parse_args()

    if args.target in {"mac", "mac-dmg"} and not sys.platform.startswith("darwin"):
        raise SystemExit("The mac bundle can only be built on macOS.")
    if args.target == "windows" and not sys.platform.startswith("win"):
        raise SystemExit("The Windows bundle can only be built on Windows.")

    if args.target == "mac-dmg":
        _run_pyinstaller("mac")
        app_path = _bundle_path("mac")
        bundle_path = _bundle_path("mac-dmg")
        if not app_path.exists():
            raise SystemExit(f"Expected build output at {app_path}, but it was not found.")
        _create_dmg(app_path, bundle_path)
    else:
        _run_pyinstaller(args.target)
        bundle_path = _bundle_path(args.target)
    if not bundle_path.exists():
        raise SystemExit(f"Expected build output at {bundle_path}, but it was not found.")
    print(f"Created {bundle_path}")


if __name__ == "__main__":
    main()
