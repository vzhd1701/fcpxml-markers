import datetime
import os
import sys
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import List

import opentimelineio as otio


class FCPXMLError(Exception):
    pass


@dataclass
class Marker(object):
    name: str
    # type: str
    is_checked: bool
    # notes: str
    asset_name: str
    event_name: str
    project_name: str
    # roles: str
    timecode: str
    frame: int


class Timeline(object):
    def __init__(self, event_name, timeline):
        self.event_name = event_name
        self.timeline = timeline

    @property
    def name(self):
        return self.timeline.name

    def iter_markers(self):
        for clip in self.timeline.each_clip():
            for marker in clip.markers:
                marker_frame = int(
                    clip.range_in_parent().start_time.value
                    + marker.marked_range.start_time.value
                )

                marker_timecode = _get_marker_timecode(
                    marker_frame,
                    marker.marked_range.start_time.rate,
                )

                yield Marker(
                    name=marker.name,
                    is_checked=marker.color == "GREEN",
                    asset_name=clip.name,
                    event_name=self.event_name,
                    project_name=self.timeline.name,
                    timecode=marker_timecode,
                    frame=marker_frame,
                )


def _get_marker_timecode(start_frame: int, rate: int) -> str:
    seconds, spare_frames = divmod(start_frame, rate)

    time = str(datetime.timedelta(seconds=seconds))
    if time.startswith("0:"):
        time = f"00{time[1:]}"

    return f"{time}:{spare_frames:05.2f}"


def get_timelines(file) -> List[Timeline]:
    if getattr(sys, "frozen", False):
        custom_fpcxml_adapter_root = Path(sys._MEIPASS) / "custom_fpcxml_adapter"
    else:
        custom_fpcxml_adapter_root = Path(
            find_spec("fcpxml_markers.custom_fpcxml_adapter").origin
        ).parent

    os.environ["OTIO_PLUGIN_MANIFEST_PATH"] = str(
        custom_fpcxml_adapter_root / "manifest.json"
    )

    collection = otio.adapters.read_from_file(file, adapter_name="fcpx_xml_custom")

    if isinstance(collection, otio.schema.Timeline):
        return [Timeline(event_name=collection.name, timeline=collection)]

    if not list(collection):
        raise FCPXMLError(f"No timelines found in '{file}'")

    if not isinstance(collection[0], otio.schema.Timeline):
        raise FCPXMLError(f"First item in '{file}' is not a timeline")

    return [Timeline(event_name=collection.name, timeline=t) for t in collection]
