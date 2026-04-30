from enum import Enum


class PackingTypeEnum(str, Enum):
    FLAT_BOTTOM_POUCH = "flat_bottom_pouch"


class SustainabilityEnum(str, Enum):
    CLASSIC = "classic"
    RECYCLABLE = "recyclable"
    COMPOSTABLE = "compostable"


class MaterialEnum(str, Enum):
    GENERAL = "general"
    FRESH_KEEP = "fresh_keep"
    MAX_PROTECTION = "max_protection"


class PrintingEnum(str, Enum):
    OUTSIDE = "outside"
    DOUBLE_SIDE = "double_side"
    THREE_SIDE = "three_side"
    FIVE_SIDE = "five_side"


class LaminationEnum(str, Enum):
    MATTE = "matte"
    GLOSS = "gloss"
    SOFT_TOUCH = "soft_touch"


class FinishingEnum(str, Enum):
    NO_FINISHING = "no_finishing"
    SPOT_UV = "spot_uv"
    HOT_FOIL_STAMPING = "hot_foil_stamping"
    EMBOSS = "emboss"
    WINDOW = "window"


class ZipperEnum(str, Enum):
    ZIPPER = "zipper"
    CHILD_RESISTANT = "child_resistant"
    EASY_TEAR = "easy_tear"


class HangHoleEnum(str, Enum):
    ROUND_HOLE = "round_hole"
    EURO_HOLE = "euro_hole"


class OtherAddonEnum(str, Enum):
    TEAR_NOTCH = "tear_notch"
    TEAR_LINE = "tear_line"
    VALVE = "valve"
    SPOUT = "spout"