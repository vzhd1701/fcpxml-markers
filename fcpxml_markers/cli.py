import csv
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, List, Optional

from fcpxml_markers.cli_args import parse_args
from fcpxml_markers.extract_gif import extract_gif_fragments, extract_gif_slideshow
from fcpxml_markers.extract_thumbs import extract_thumbs
from fcpxml_markers.fcpxml_parse import Marker, get_timelines

logger = logging.getLogger(__name__)


def cli(*argv: str) -> None:
    args = parse_args(argv)

    setup_logging(args.verbose, args.log)

    if not args.fcpxml_file.is_file():
        logger.error(f"Input FCPXML file not found '{args.fcpxml_file}'")
        return

    timelines = get_timelines(args.fcpxml_file)

    media_path = args.media_path or args.fcpxml_file.parent

    if not media_path.is_dir():
        logger.error(f"Media files directory not found '{media_path}'")
        return

    # Remove existing CSV, each timeline will append to it.
    if args.mode == "csv":
        args.csv_file.unlink(missing_ok=True)

    for timeline in timelines:
        timeline_video_path = _find_matching_media(timeline.name, media_path)

        logger.info(f"Extracting markers from {timeline_video_path}")

        if timeline_video_path is None:
            logger.warning(f"No video found for timeline {timeline.name}")
            return

        markers = list(timeline.iter_markers())

        if not markers:
            logger.warning(f"No markers found for timeline {timeline.name}")
            return

        if args.mode == "csv":
            logger.info(f"Generating CSV file {args.csv_file}")

            output_csv(
                markers=markers,
                clip_path=timeline_video_path,
                csv_path=args.csv_file,
                resize_height=args.resize_height,
                resize_width=args.resize_width,
                thumb_format=args.image_format,
                jpg_quality=args.image_jpg_quality,
            )

        if args.mode == "gif" and args.type == "slideshow":
            logger.info(f"Generating slideshow GIF file {args.gif_file}")

            frame_numbers = [m.frame for m in markers]

            extract_gif_slideshow(
                gif_path=args.gif_file,
                clip_path=timeline_video_path,
                frame_numbers=frame_numbers,
                resize_height=args.resize_height,
                resize_width=args.resize_width,
                is_optimize=args.optimize,
                duration=args.duration,
            )

        if args.mode == "gif" and args.type == "fragments":
            logger.info(f"Generating fragments GIF file {args.gif_file}")

            frame_numbers = [m.frame for m in markers]

            extract_gif_fragments(
                gif_path=args.gif_file,
                clip_path=timeline_video_path,
                frame_numbers=frame_numbers,
                resize_height=args.resize_height,
                resize_width=args.resize_width,
                is_optimize=args.optimize,
                duration=args.duration,
                fps=args.fps,
            )

        logger.info(f"Done!")


def output_csv(
    markers: List[Marker],
    clip_path: Path,
    csv_path: Path,
    resize_height: int,
    resize_width: int,
    thumb_format: str,
    jpg_quality: int,
) -> None:
    frame_numbers = [m.frame for m in markers]

    thumb_names = [
        f"{clip_path.stem} {m.timecode.replace(':','_')}.{thumb_format}"
        for m in markers
    ]
    thumbs_path = csv_path.parent

    extract_thumbs(
        thumbs_path=thumbs_path,
        clip_path=clip_path,
        thumb_names=thumb_names,
        frame_numbers=frame_numbers,
        resize_height=resize_height,
        resize_width=resize_width,
        thumb_format=thumb_format,
        jpg_quality=jpg_quality,
    )

    markers_out = [
        {
            "Marker Name": marker.name,
            "Marker Type": "",
            "Checked": "true" if marker.is_checked else "false",
            "Notes": "",
            "Asset Name": marker.asset_name,
            "Event Name": marker.event_name,
            "Project Name": marker.project_name,
            "Roles": "",
            "Timecode": marker.timecode,
            "Image Filename": thumb_name,
        }
        for marker, thumb_name in zip(markers, thumb_names)
    ]

    _dicts_to_csv(markers_out, csv_path)


def _dicts_to_csv(out_dicts: List[dict], csv_file: Path):
    with csv_file.open("a+", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(out_dicts[0].keys())
        for out_dict in out_dicts:
            writer.writerow(out_dict.values())


def _find_matching_media(name: str, folder: Path) -> Optional[Path]:
    """Look for media with this name in this folder."""

    if "." in name and (folder / name).is_file():
        return folder / name

    media_exts = (".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mts", ".m2ts", ".mkv")

    for ext in media_exts:
        file_path = folder / (name + ext)
        if file_path.is_file():
            return file_path

    return None


def setup_logging(is_verbose: bool, log_file: Optional[Path]) -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s")

    logging.getLogger("fcpxml_markers").setLevel(
        logging.DEBUG if is_verbose else logging.INFO
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)-8.8s] %(message)s")
        )
        logging.getLogger("fcpxml_markers").addHandler(file_handler)


def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")
    os._exit(1)


def main() -> None:
    signal.signal(signal.SIGINT, abort)

    try:
        cli(*sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(1)
