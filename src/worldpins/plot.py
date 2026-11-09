from PIL.ImageChops import offset
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import shapely.geometry as sgeom

from .compassposition import CompassPosition
from .points import Point
from .style import InsetStyle, Style


GEO = ccrs.PlateCarree()
SQRT2 = np.sqrt(2)


def _fill_for(attrs: dict, style: Style) -> str:
    for key in (attrs.get("ADM0_A3"), attrs.get("NAME")):
        if key in style.countries:
            return style.countries[key]
    return style.continents.get(attrs.get("CONTINENT"), style.land)


def _draw_countries(ax, style: Style, resolution: str, clip=None) -> None:
    shp = shpreader.natural_earth(
        resolution=resolution, category="cultural", name="admin_0_countries"
    )
    for rec in shpreader.Reader(shp).records():
        geom = rec.geometry
        if clip is not None:
            # Trim to the region so the SVG doesn't carry all of Russia, etc.
            geom = geom.intersection(clip)
            if geom.is_empty:
                continue
        ax.add_geometries(
            [geom], crs=GEO,
            facecolor=_fill_for(rec.attributes, style),
            edgecolor=style.border_colour,
            linewidth=style.border_width,
            zorder=1,
        )


def _draw_points(ax, points : list[Point], pin_colour_list : list[str], pin_size : float,
                 label_colour_list: list[str], label_size : float, label_offset_magnitude : float, has_labels : bool) -> None:
    to_data = GEO._as_mpl_transform(ax)
    for p in points:
        try:
            pin_colour = pin_colour_list[p.point_type]
        except IndexError:
            print(f"WARNING: Cannot access pin colour {p.point_type}. Reverting to default")
            pin_colour = pin_colour_list[0]

        try:
            label_colour = label_colour_list[p.point_type]
        except IndexError:
            print(f"WARNING: Cannot access label colour {p.point_type}. Reverting to default")
            label_colour = label_colour_list[0]


        ax.plot(p.lon, p.lat, marker="o", color=pin_colour, markersize=pin_size,
                transform=GEO, zorder=5)
        if has_labels and p.label:
            # Offset in points, so it looks the same at any zoom level
            x_offset = 0
            y_offset = 0
            halign=""
            valign=""

            match p.pos:
                case CompassPosition.NORTH:
                    x_offset = 0
                    y_offset = label_offset_magnitude
                    halign = "center"
                    valign = "bottom"
                case CompassPosition.NORTH_EAST:
                    x_offset = 0*label_offset_magnitude/SQRT2
                    y_offset = 0*label_offset_magnitude/SQRT2
                    halign = "left"
                    valign = "bottom"
                case CompassPosition.EAST:
                    x_offset = label_offset_magnitude
                    y_offset = 0
                    halign = "left"
                    valign = "center"
                case CompassPosition.SOUTH_EAST:
                    x_offset =  0*label_offset_magnitude/SQRT2
                    y_offset = -0*label_offset_magnitude/SQRT2
                    halign = "left"
                    valign = "top"
                case CompassPosition.SOUTH:
                    x_offset = 0
                    y_offset = -label_offset_magnitude
                    halign = "center"
                    valign = "top"
                case CompassPosition.SOUTH_WEST:
                    x_offset = -0*label_offset_magnitude/SQRT2
                    y_offset = -0*label_offset_magnitude/SQRT2
                    halign = "right"
                    valign = "top"
                case CompassPosition.WEST:
                    x_offset = -label_offset_magnitude
                    y_offset = 0
                    halign = "right"
                    valign = "center"
                case CompassPosition.NORTH_WEST:
                    x_offset = -0*label_offset_magnitude/SQRT2
                    y_offset =  0*label_offset_magnitude/SQRT2
                    halign = "right"
                    valign = "bottom"

            ax.annotate(p.label, xy=(p.lon, p.lat), xycoords=to_data,
                        xytext=(x_offset, y_offset), textcoords="offset points",
                        horizontalalignment=halign,verticalalignment=valign,
                        fontsize=label_size, color=label_colour, zorder=6)

def _draw_key(ax, position: tuple[float,float], key: list[str], key_anchor: tuple[float,float], pin_colour_list: list[str], key_colour: tuple[str,str]):
    if len(key) != len(pin_colour_list):
        print("WARNING: pin colour list and key entries must have same length")
        raise ValueError

    halign,valign = CompassPosition.get_anchor_halignment_valignment(key_anchor)
    print(halign,valign)

    handles = []
    for text,col in zip(key,pin_colour_list):
        handles.append(Line2D([],[], marker="o",color=col,label=text,markersize=8, linestyle="None"))

    ax.legend(handles=handles,title="",bbox_to_anchor=position, loc=key_anchor, edgecolor=key_colour[0], facecolor=key_colour[1])
    return


def _inset_crs(inset: InsetStyle):
    lon0, lon1, lat0, lat1 = inset.extent
    clon, clat = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    if inset.projection == "mercator":
        return ccrs.Mercator(central_longitude=clon)
    if inset.projection == "plate_carree":
        return ccrs.PlateCarree(central_longitude=clon)
    span = (lat1 - lat0) / 6
    return ccrs.LambertConformal(
        central_longitude=clon, central_latitude=clat,
        standard_parallels=(lat0 + span, lat1 - span),
    )


def _in_extent(p: Point, extent) -> bool:
    lon0, lon1, lat0, lat1 = extent
    return lon0 <= p.lon <= lon1 and lat0 <= p.lat <= lat1


def make_map(points: list[Point], out_path: str,
             style: Style | None = None, has_labels: bool = True) -> None:
    style = style or Style()
    inset = style.inset

    plt.rcParams["svg.fonttype"] = "none"  # keep SVG text editable
    plt.rcParams["font.family"] = style.font_family

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    ax.set_global()
    ax.patch.set_facecolor(style.sea)
    ax.spines["geo"].set_edgecolor(style.border_colour)
    _draw_countries(ax, style, style.resolution)

    main_points = points
    if inset and not inset.pins_on_main:
        main_points = [p for p in points if not _in_extent(p, inset.extent)]
    _draw_points(ax, main_points, style.pin_colour, style.pin_size,
                 style.label_colour,style.label_size, style.label_offset_magnitude, has_labels)

    if inset:
        lon0, lon1, lat0, lat1 = inset.extent

        if inset.show_box:
            ax.add_geometries(
                [sgeom.box(lon0, lat0, lon1, lat1)], crs=GEO,
                facecolor="none", edgecolor=inset.border_colour,
                linewidth=inset.border_width, zorder=4,
            )

        iax = fig.add_axes(list(inset.position), projection=_inset_crs(inset))
        iax.set_zorder(10)
        iax.set_extent([lon0, lon1, lat0, lat1], crs=GEO)
        iax.patch.set_facecolor(style.sea)
        iax.spines["geo"].set_edgecolor(inset.border_colour)
        iax.spines["geo"].set_linewidth(inset.border_width)

        pad = 5  # degrees, so edges stay filled with the curved projections
        clip = sgeom.box(lon0 - pad, lat0 - pad, lon1 + pad, lat1 + pad)
        _draw_countries(iax, style, inset.resolution, clip=clip)

        _draw_points(iax, [p for p in points if _in_extent(p, inset.extent)],
                     style.pin_colour, inset.pin_size, style.label_colour, inset.label_size,
                     inset.label_offset_magnitude, has_labels)

    _draw_key(ax,style.key_position, style.key, style.key_anchor, style.pin_colour, style.key_colour)

    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
