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


def _archive_name(target: str) -> str:
    return f"{_bundle_name(target)}.zip"


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


def _bundle_path(target: str) -> Path:
    bundle_name = _bundle_name(target)
    if target == "mac":
        return DIST_DIR / f"{bundle_name}.app"
    if target == "windows":
        return DIST_DIR / f"{bundle_name}.exe"
    return DIST_DIR / bundle_name


def _make_zip(target: str) -> Path:
    bundle_path = _bundle_path(target)
    if not bundle_path.exists():
        raise SystemExit(f"Expected build output at {bundle_path}, but it was not found.")

    archive_path = DIST_DIR / _archive_name(target)
    if archive_path.exists():
        archive_path.unlink()

    shutil.make_archive(
        str(archive_path.with_suffix("")),
        "zip",
        root_dir=bundle_path.parent,
        base_dir=bundle_path.name,
    )

    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a release bundle for Sustainable Fashion Influencer Life."
    )
    parser.add_argument(
        "target",
        choices=("mac", "windows"),
        help="The release bundle name to create.",
    )
    args = parser.parse_args()

    if args.target == "mac" and not sys.platform.startswith("darwin"):
        raise SystemExit("The mac bundle can only be built on macOS.")
    if args.target == "windows" and not sys.platform.startswith("win"):
        raise SystemExit("The Windows bundle can only be built on Windows.")

    _run_pyinstaller(args.target)
    archive_path = _make_zip(args.target)
    print(f"Created {archive_path}")


if __name__ == "__main__":
    main()
