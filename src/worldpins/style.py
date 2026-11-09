import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class InsetStyle:
    extent: tuple[float, float, float, float]  # lon_min, lon_max, lat_min, lat_max
    position: tuple[float, float, float, float] = (0.02, 0.05, 0.25, 0.43)
    projection: str = "mercator"
    resolution: str = "50m"
    pin_size: float = 6
    label_size: float = 8
    border_colour: str = "#444444"
    border_width: float = 1.0
    show_box: bool = True
    pins_on_main: bool = True
    label_offset_magnitude: float = 2

    def __post_init__(self):
        if len(self.extent) != 4:
            raise ValueError("inset.extent needs 4 values: lon_min, lon_max, lat_min, lat_max")
        if len(self.position) != 4:
            raise ValueError("inset.position needs 4 values: left, bottom, width, height")
        lon0, lon1, lat0, lat1 = self.extent
        if not (-180 <= lon0 < lon1 <= 180 and -90 <= lat0 < lat1 <= 90):
            raise ValueError("inset.extent must satisfy lon_min < lon_max and lat_min < lat_max")
        if self.projection not in {"mercator", "plate_carree", "lambert"}:
            raise ValueError(f"Unknown inset projection: {self.projection!r}")


@dataclass
class Style:
    sea: str = "#cfe8f3"
    land: str = "#e8e8e8"
    font_family: str = "sans-serif"
    border_colour: str = "#ffffff"
    border_width: float = 0.4
    pin_colour: list[str] = field(default_factory=list)
    label_colour: list[str] = field(default_factory=list)
    key: list[str] = field(default_factory=list)
    key_position: tuple[float,float] = (0,0)
    key_anchor: str = "upper left"
    key_colour: tuple[str,str] = ("#000000", "#FFFFFF")
    pin_size: float = 5
    label_size: float = 7
    resolution: str = "110m"
    continents: dict[str, str] = field(default_factory=dict)
    countries: dict[str, str] = field(default_factory=dict)
    inset: InsetStyle | None = None
    label_offset_magnitude: float = 4


def load_style(path: str | Path | None) -> Style:
    if path is None:
        return Style()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    unknown = set(data) - set(Style.__dataclass_fields__)
    if unknown:
        raise ValueError(f"Unknown style key(s): {', '.join(sorted(unknown))}")
    if "inset" in data:
        try:
            data["inset"] = InsetStyle(**data["inset"])
        except TypeError as e:
            raise ValueError(f"Bad [inset] table: {e}") from None
    return Style(**data)
