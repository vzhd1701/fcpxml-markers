import logging
import math
from itertools import chain
from typing import Tuple

import av

logger = logging.getLogger(__name__)


def extract_frames(clip_path, frame_numbers, duration=None, fps=None):
    with av.open(str(clip_path)) as clip:
        for frame_number in frame_numbers:
            if duration:
                yield from _iter_seek_frames_raw(clip, frame_number, duration, fps)
            else:
                yield _get_seek_frame_raw(clip, frame_number)


def iter_resized_as_ndarray(frames, height, width):
    (height, width), frames = _extract_proper_frame_size(frames, height, width)

    for frame in frames:
        yield frame.to_ndarray(format="rgb24", height=height, width=width)


def iter_resized_as_image(frames, height, width):
    (height, width), frames = _extract_proper_frame_size(frames, height, width)

    for frame in frames:
        yield frame.to_image(height=height, width=width)


def _extract_proper_frame_size(frames, height, width):
    first_frame = next(frames)

    height, width = _calc_size_keeping_aspect(
        height, width, first_frame.height, first_frame.width
    )

    return (height, width), chain([first_frame], frames)


def _get_seek_frame_raw(clip, frame_number):
    video_stream = clip.streams.video[0]

    target_timestamp = int(
        (frame_number / video_stream.base_rate) / video_stream.time_base
    )

    logger.debug(f"Extracting frame at {target_timestamp}")

    clip.seek(target_timestamp, stream=video_stream)

    for packet in clip.demux(video_stream):
        for frame in packet.decode():
            if frame.pts < target_timestamp:
                continue

            return frame


def _iter_seek_frames_raw(clip, start_frame_number, duration, fps):
    video_stream = clip.streams.video[0]

    start_timestamp = int(
        (start_frame_number / video_stream.base_rate) / video_stream.time_base
    )

    frames_count = int(duration * fps)
    frame_step = math.ceil(video_stream.base_rate / fps) or 3
    cur_frame = 0
    frames_extracted = 0

    logger.debug(
        f"Extracting {frames_count} frames with step {frame_step}"
        f" starting at {start_timestamp}"
    )

    clip.seek(start_timestamp, stream=video_stream)

    for packet in clip.demux(video_stream):
        for frame in packet.decode():
            if frame.pts < start_timestamp:
                continue

            if cur_frame % frame_step == 0:
                frames_extracted += 1
                yield frame

            cur_frame += 1

            if frames_extracted >= frames_count:
                return


def _calc_size_keeping_aspect(
    target_height, target_width, original_height, original_width
) -> Tuple[int, int]:
    if not target_height and not target_width:
        return original_height, original_width

    aspect_ratio = original_width / original_height

    if not target_height:
        target_height = int(target_width / aspect_ratio)

    if not target_width:
        target_width = int(target_height * aspect_ratio)

    return target_height, target_width
