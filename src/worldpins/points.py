import csv
from dataclasses import dataclass
from pathlib import Path
from .compassposition import CompassPosition

@dataclass(frozen=True)
class Point:
    lat: float
    lon: float
    label: str = ""
    pos: CompassPosition = CompassPosition.NORTH_EAST
    point_type: int = 0


def read_points(path: str | Path) -> list[Point]:
    points = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = {"lat", "lon"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing column(s): {', '.join(sorted(missing))}")

        for line_no, row in enumerate(reader, start=2):
            try:
                lat, lon = float(row["lat"]), float(row["lon"])
            except (TypeError, ValueError):
                if row["lat"].strip()[0] == "#":
                    continue
                raise ValueError(f"Line {line_no}: lat/lon must be numbers") from None

            try:
                pos = CompassPosition.from_abbrev(row["pos"])
            except:
                pos = CompassPosition.NORTH_EAST

            try:
                point_type = int(row["point_type"])
            except:
                point_type = 0

            if point_type < 0:
                raise ValueError("Point type must be a positive integer >= 0")

            if not -90 <= lat <= 90:
                raise ValueError(f"Line {line_no}: lat {lat} out of range")
            if not -180 <= lon <= 180:
                raise ValueError(f"Line {line_no}: lon {lon} out of range")

            points.append(Point(lat, lon, (row.get("label") or "").strip(), pos, point_type))
            print(line_no, row)
    return points
