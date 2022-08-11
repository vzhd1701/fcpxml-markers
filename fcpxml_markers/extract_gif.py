import logging
import subprocess
from pathlib import Path
from typing import List, Optional

import imageio

from fcpxml_markers.extract_frames import extract_frames, iter_resized_as_ndarray

logger = logging.getLogger(__name__)


def extract_gif_slideshow(
    gif_path: Path,
    clip_path: Path,
    frame_numbers: List[int],
    resize_height: int,
    resize_width: int,
    is_optimize: bool,
    duration: int,
):
    frames = iter_resized_as_ndarray(
        extract_frames(clip_path, frame_numbers),
        resize_height,
        resize_width,
    )

    with imageio.get_writer(gif_path, mode="I", duration=duration) as writer:
        for frame in frames:
            writer.append_data(frame)

    if is_optimize:
        logger.info("Optimizing GIF")
        _gifsicle(gif_path)


def extract_gif_fragments(
    gif_path: Path,
    clip_path: Path,
    frame_numbers: List[int],
    resize_height: int,
    resize_width: int,
    is_optimize: bool,
    duration: int,
    fps: int,
):
    frames = iter_resized_as_ndarray(
        extract_frames(clip_path, frame_numbers, duration, fps),
        resize_height,
        resize_width,
    )

    with imageio.get_writer(gif_path, mode="I") as writer:
        for frame in frames:
            writer.append_data(frame)

    if is_optimize:
        logger.info("Optimizing GIF")
        _gifsicle(gif_path)


def _gifsicle(
    gif_file: Path,
    colors: int = 256,
    optimize: bool = True,
    options: Optional[List[str]] = None,
) -> None:
    options = [] if options is None else options

    if optimize and "--optimize" not in options:
        options.append("--optimize")

    try:
        subprocess.call(
            [
                "gifsicle",
                *options,
                str(gif_file),
                "--colors",
                str(colors),
                "--output",
                str(gif_file),
            ]
        )
    except FileNotFoundError:
        raise FileNotFoundError("The gifsicle binary was not found on your system.")
