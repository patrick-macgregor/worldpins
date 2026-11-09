
from enum import Enum
class CompassPosition(Enum):
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7

    @classmethod
    def from_abbrev(cls, abbrev: str):
        match abbrev:
            case "N":
                return CompassPosition.NORTH
            case "NE":
                return CompassPosition.NORTH_EAST
            case "E":
                return CompassPosition.EAST
            case "SE":
                return CompassPosition.SOUTH_EAST
            case "S":
                return CompassPosition.SOUTH
            case "SW":
                return CompassPosition.SOUTH_WEST
            case "W":
                return CompassPosition.WEST
            case "NW":
                return CompassPosition.NORTH_WEST
            case _:
                print(f"WARNING: Cannot parse {abbrev}. Setting to NORTH_EAST...")
                return CompassPosition.NORTH_EAST

    @classmethod
    def get_anchor_halignment_valignment(cls, cp: CompassPosition) -> tuple[str,str]:
        halign=""
        valign=""
        match cp:
            case CompassPosition.NORTH:
                halign = "center"
                valign = "bottom"
            case CompassPosition.NORTH_EAST:
                halign = "left"
                valign = "bottom"
            case CompassPosition.EAST:
                halign = "left"
                valign = "center"
            case CompassPosition.SOUTH_EAST:
                halign = "left"
                valign = "top"
            case CompassPosition.SOUTH:
                halign = "center"
                valign = "top"
            case CompassPosition.SOUTH_WEST:
                halign = "right"
                valign = "top"
            case CompassPosition.WEST:
                halign = "right"
                valign = "center"
            case CompassPosition.NORTH_WEST:
                halign = "right"
                valign = "bottom"

        return (halign,valign)

