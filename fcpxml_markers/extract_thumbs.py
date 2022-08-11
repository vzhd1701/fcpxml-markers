from pathlib import Path
from typing import List

from fcpxml_markers.extract_frames import extract_frames, iter_resized_as_image


def extract_thumbs(
    thumbs_path: Path,
    clip_path: Path,
    thumb_names: List[str],
    frame_numbers: List[int],
    resize_height: int,
    resize_width: int,
    thumb_format: str,
    jpg_quality: int,
):
    thumbs = zip(
        thumb_names,
        iter_resized_as_image(
            extract_frames(clip_path, frame_numbers),
            resize_height,
            resize_width,
        ),
    )

    kwargs = {}
    if thumb_format == "jpg":
        kwargs["quality"] = jpg_quality
    if thumb_format == "png":
        kwargs["optimize"] = True

    for thumb_name, thumb_image in thumbs:
        thumb_file_path = thumbs_path / f"{thumb_name}"
        thumb_image.save(thumb_file_path, **kwargs)
