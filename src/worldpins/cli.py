import argparse
import sys
from pathlib import Path

from .plot import make_map
from .points import read_points
from .style import load_style

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="worldpins",
        description="Plot pins from a CSV onto a world map (SVG or PDF).",
    )
    parser.add_argument("input", type=Path, help="CSV with lat,lon[,label]")
    parser.add_argument("-o", "--output", type=Path, default=Path("map.svg"),
                        help="output file, .svg or .pdf (default: map.svg)")
    parser.add_argument("--no-labels", action="store_true",
                        help="don't draw labels next to pins")
    parser.add_argument("-s", "--style", type=Path, default=None,
                    help="TOML style file (colours, borders, resolution)")
    args = parser.parse_args(argv)

    if args.output.suffix.lower() not in {".svg", ".pdf"}:
        parser.error("output must end in .svg or .pdf")

    try:
        points = read_points(args.input)
        style = load_style(args.style)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    make_map(points, str(args.output), style=style, has_labels=not args.no_labels)
    print(f"Wrote {len(points)} pin(s) to {args.output}")
    return 0
