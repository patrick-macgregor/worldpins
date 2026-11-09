# worldpins

(NOTE: a lot of the heavy lifting was done by an AI, so proceed with caution. That includes this README)

Plot pins from a CSV file onto a styled world map and export it as **SVG** or **PDF**.

- Robinson-projection world map built from Natural Earth data (via Cartopy)
- Per-pin labels, with a choice of compass position for each label
- Multiple pin "types", each with its own pin colour, label colour and legend entry
- Colour countries individually, or by continent, using a TOML style file
- Optional zoomed **inset map** for a crowded region (e.g. Europe), with its own projection and resolution
- SVG output keeps text as real, editable text (handy for Inkscape / Illustrator)

---

## Requirements

- Python **3.11 or newer** (uses `match` statements and `tomllib`)
- [Cartopy](https://scitools.org.uk/cartopy/), Matplotlib, NumPy, Shapely
- An internet connection the first time you run it, so Cartopy can download the Natural Earth shapefiles (they are cached afterwards)

## Installation

The code is a Python package called `worldpins`. Put the source files in a folder with that name so that the relative imports work:

```
your-project/
└── worldpins/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── compassposition.py
    ├── plot.py
    ├── points.py
    └── style.py
```

Then, from `your-project/`:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install the dependencies
pip install cartopy matplotlib numpy shapely
```

> **Tip:** Cartopy depends on the GEOS and PROJ libraries. On most platforms the pip wheels include them. If `pip install cartopy` fails, install it with conda instead: `conda install -c conda-forge cartopy`.

Check that it works:

```bash
python -m worldpins --help
```

## Quick start

1. Create a CSV of your points (`points.csv`):

   ```csv
   lat,lon,label,pos,point_type
   51.5074,-0.1278,London,NE,0
   40.7128,-74.0060,New York,W,0
   -33.8688,151.2093,Sydney,E,1
   35.6762,139.6503,Tokyo,S,1
   ```

2. Create a minimal style file (`style.toml`). At least `pin_colour` and `label_colour` are needed, one entry per `point_type`:

   ```toml
   pin_colour   = ["#d62728", "#1f77b4"]
   label_colour = ["#000000", "#000000"]
   key          = ["Visited", "Planned"]
   ```

3. Generate the map:

   ```bash
   python -m worldpins points.csv -s style.toml -o map.svg
   ```

## Command-line usage

```
python -m worldpins [-h] [-o OUTPUT] [--no-labels] [-s STYLE] input
```

| Argument | Description |
|---|---|
| `input` | CSV file of points (see below) |
| `-o`, `--output` | Output file, must end in `.svg` or `.pdf` (default: `map.svg`) |
| `--no-labels` | Don't draw labels next to the pins |
| `-s`, `--style` | TOML style file (colours, borders, resolution, inset, legend) |

## Input CSV format

The file must have a header row. `lat` and `lon` are required; the other columns are optional.

| Column | Required | Description |
|---|---|---|
| `lat` | yes | Latitude in decimal degrees, -90 to 90 |
| `lon` | yes | Longitude in decimal degrees, -180 to 180 |
| `label` | no | Text drawn next to the pin |
| `pos` | no | Label position relative to the pin: `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`. Defaults to `NE` (an unrecognised value also falls back to `NE` with a warning) |
| `point_type` | no | Integer ≥ 0, selecting which entry of `pin_colour` / `label_colour` / `key` to use. Defaults to `0` |

Rows whose `lat` value starts with `#` are treated as comments and skipped.

## Style file

Styles are written in [TOML](https://toml.io). Every key is optional except where noted; unknown keys cause an error.

### Top-level keys

| Key | Default | Description |
|---|---|---|
| `sea` | `"#cfe8f3"` | Ocean / background colour |
| `land` | `"#e8e8e8"` | Default land colour |
| `border_colour` | `"#ffffff"` | Country border colour (also the map frame) |
| `border_width` | `0.4` | Country border width |
| `pin_colour` | `[]` | **Needed.** List of pin colours, indexed by `point_type` |
| `label_colour` | `[]` | **Needed.** List of label colours, indexed by `point_type` |
| `pin_size` | `5` | Pin marker size (points) |
| `label_size` | `7` | Label font size |
| `label_offset_magnitude` | `4` | Distance (points) between pin and label |
| `resolution` | `"110m"` | Natural Earth resolution: `110m`, `50m` or `10m` |
| `continents` | `{}` | Table mapping continent name to fill colour |
| `countries` | `{}` | Table mapping country (ISO A3 code or name) to fill colour. Takes priority over `continents` |
| `key` | `[]` | Legend entries, one per colour in `pin_colour` (must be the same length) |
| `key_position` | `[0, 0]` | Legend anchor position in axes coordinates |
| `key_anchor` | `"upper left"` | Matplotlib legend `loc` for the legend box |
| `key_colour` | `["#000000", "#FFFFFF"]` | Legend `[edge colour, background colour]` |

### Inset map (`[inset]` table)

Add an `[inset]` table to draw a zoomed map of a region. Only `extent` is required.

| Key | Default | Description |
|---|---|---|
| `extent` | *(required)* | `[lon_min, lon_max, lat_min, lat_max]` |
| `position` | `[0.02, 0.05, 0.25, 0.43]` | Inset placement on the figure: `[left, bottom, width, height]` (0–1) |
| `projection` | `"mercator"` | `mercator`, `plate_carree` or `lambert` |
| `resolution` | `"50m"` | Natural Earth resolution for the inset |
| `pin_size` | `6` | Pin size inside the inset |
| `label_size` | `8` | Label font size inside the inset |
| `label_offset_magnitude` | `2` | Pin-to-label distance inside the inset |
| `border_colour` | `"#444444"` | Inset frame and extent-box colour |
| `border_width` | `1.0` | Inset frame and extent-box width |
| `show_box` | `true` | Draw a box on the main map marking the inset region |
| `pins_on_main` | `true` | Also draw pins that fall inside the inset on the main map. If `false`, they only appear in the inset |

### Full example

```toml
sea           = "#cfe8f3"
land          = "#e8e8e8"
border_colour = "#ffffff"
border_width  = 0.4
resolution    = "50m"

pin_colour   = ["#d62728", "#1f77b4", "#2ca02c"]
label_colour = ["#222222", "#222222", "#222222"]
pin_size     = 5
label_size   = 7

key          = ["Offices", "Partners", "Events"]
key_position = [0.01, 0.30]
key_anchor   = "lower left"
key_colour   = ["#999999", "#ffffff"]

[continents]
Europe        = "#f2e6d0"
Asia          = "#e3efd9"
"North America" = "#e8dcef"

[countries]
GBR = "#f4c7c3"
FRA = "#c3d9f4"

[inset]
extent         = [-12, 30, 35, 62]
position       = [0.02, 0.05, 0.25, 0.43]
projection     = "lambert"
resolution     = "50m"
pins_on_main   = false
```

## Using it from Python

```python
from worldpins import read_points, make_map
from worldpins.style import load_style

points = read_points("points.csv")
style = load_style("style.toml")
make_map(points, "map.pdf", style=style, has_labels=True)
```

SVG output is written with `svg.fonttype = "none"`, so text stays as live text and the viewer's installed fonts are used when opening the file.

## Troubleshooting

- **`ModuleNotFoundError` / relative import errors**: run it as a package from the folder *containing* `worldpins/` (`python -m worldpins ...`), not by running `cli.py` directly.
- **`IndexError` about colours**: your style file needs `pin_colour` and `label_colour` with at least one entry each.
- **`ValueError` from the legend**: `key` must have the same number of entries as `pin_colour`.
- **Shapefile download fails**: Cartopy needs internet access on first use to fetch Natural Earth data.
- **`error: CSV is missing column(s)`**: check your header row contains `lat` and `lon`.

## Data

Map geometry comes from [Natural Earth](https://www.naturalearthdata.com/), which is in the public domain, downloaded via Cartopy.


## Example
See examples directory, generated using
```python
python -m worldpins -o facilities_map.pdf -s example_style.toml example.csv
```
