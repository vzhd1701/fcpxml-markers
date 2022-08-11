import argparse
from pathlib import Path
from typing import Sequence

from fcpxml_markers.version import __version__


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fcpxml-markers",
        description="Extract markers from FCPXML",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    common_args = {
        "--log": {
            "metavar": "FILE",
            "type": Path,
            "help": "file to store program log",
        },
        "--verbose": {
            "action": "store_true",
            "help": "output debug information",
        },
        "--media-path": {
            "metavar": "DIR",
            "type": Path,
            "help": (
                "path to look for media files,"
                " by default uses the same directory as the FCPXML file"
            ),
        },
        "--resize-height": {
            "metavar": "H",
            "type": int,
            "help": "resize to height H keeping aspect ration",
        },
        "--resize-width": {
            "metavar": "W",
            "type": int,
            "help": "resize to width W keeping aspect ration",
        },
    }

    subparsers = parser.add_subparsers(help="mode", dest="mode", required=True)
    parser_csv = subparsers.add_parser(
        "csv",
        help="Convert FCPXML markers to CSV",
        usage="%(prog)s [-h] [OPTION]... FCPXML CSV",
    )
    parser_gif = subparsers.add_parser(
        "gif",
        help="Convert FCPXML markers to GIF",
        usage="%(prog)s [-h] [OPTION]... FCPXML GIF",
    )

    csv_args = {
        **common_args,
        "--image-format": {
            "choices": ["png", "jpg"],
            "default": "jpg",
            "help": "thumbnail image file format (default: %(default)s)",
        },
        "--image-jpg-quality": {
            "metavar": "PERCENT",
            "type": int,
            "default": 80,
            "help": "thumbnail image quality for jpg format (default: %(default)s)",
        },
        "fcpxml_file": {
            "metavar": "FCPXML",
            "type": Path,
            "help": "input FCPXML file",
        },
        "csv_file": {
            "metavar": "CSV",
            "type": Path,
            "help": "output CSV file",
        },
    }

    gif_args = {
        **common_args,
        "--resize-height": {
            "metavar": "H",
            "type": int,
            "default": 480,
            "help": (
                "resize to height H keeping aspect ration,"
                " set 0 to disable and use original size (default: %(default)s)"
            ),
        },
        "--type": {
            "choices": ["slideshow", "fragments"],
            "default": "slideshow",
            "help": (
                "slideshows for still frames, fragments for video fragments"
                " (default: %(default)s)"
            ),
        },
        "--duration": {
            "metavar": "SECONDS",
            "type": int,
            "default": 1,
            "help": (
                "slideshow frame / video fragment duration in seconds"
                " (default: %(default)s)"
            ),
        },
        "--fps": {
            "metavar": "SECONDS",
            "type": int,
            "default": 10,
            "help": "video fragments FPS (default: %(default)s)",
        },
        "--optimize": {
            "action": "store_true",
            "help": "optimize final GIF to reduce size",
        },
        "fcpxml_file": {
            "metavar": "FCPXML",
            "type": Path,
            "help": "input FCPXML file",
        },
        "gif_file": {
            "metavar": "GIF",
            "type": Path,
            "help": "output GIF file",
        },
    }

    _apply_args(csv_args, parser_csv)
    _apply_args(gif_args, parser_gif)

    return parser.parse_args(argv)


def _apply_args(args: dict, parser: argparse.ArgumentParser):
    for cmd, cmd_params in args.items():
        if isinstance(cmd, str):
            cmd = [cmd]
        parser.add_argument(*cmd, **cmd_params)
