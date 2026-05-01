from dataclasses import dataclass
from typing import Optional, Dict, Any

from enums import (
    MaterialEnum,
    PrintingEnum,
    LaminationEnum,
    FinishingEnum,
    ZipperEnum,
    HangHoleEnum,
    OtherAddonEnum,
)


@dataclass
class PriceContext:
    area: float
    width: float
    quantity: int


# Demo pricing configuration.
# These numbers are placeholders and should be replaced by real business rules later.
PRICING_CONFIG = {
    "material": {
        MaterialEnum.GENERAL: {
            "strategy": "per_area",
            "unit_price": 0.50,
        },
        MaterialEnum.FRESH_KEEP: {
            "strategy": "per_area",
            "unit_price": 0.80,
        },
        MaterialEnum.MAX_PROTECTION: {
            "strategy": "per_area",
            "unit_price": 1.20,
        },
    },
    "printing": {
        PrintingEnum.OUTSIDE: {
            "strategy": "per_area",
            "unit_price": 0.10,
        },
        PrintingEnum.DOUBLE_SIDE: {
            "strategy": "per_area",
            "unit_price": 0.18,
        },
        PrintingEnum.THREE_SIDE: {
            "strategy": "per_area",
            "unit_price": 0.22,
        },
        PrintingEnum.FIVE_SIDE: {
            "strategy": "per_area",
            "unit_price": 0.30,
        },
    },
    "lamination": {
        LaminationEnum.MATTE: {
            "strategy": "per_area",
            "unit_price": 0.05,
        },
        LaminationEnum.GLOSS: {
            "strategy": "per_area",
            "unit_price": 0.05,
        },
        LaminationEnum.SOFT_TOUCH: {
            "strategy": "per_area",
            "unit_price": 0.12,
        },
    },
    "finishing": {
        FinishingEnum.NO_FINISHING: {
            "strategy": "fixed",
            "unit_price": 0.00,
        },
        FinishingEnum.SPOT_UV: {
            "strategy": "per_area",
            "unit_price": 0.08,
        },
        FinishingEnum.HOT_FOIL_STAMPING: {
            "strategy": "per_area",
            "unit_price": 0.15,
        },
        FinishingEnum.EMBOSS: {
            "strategy": "per_area",
            "unit_price": 0.10,
        },
        FinishingEnum.WINDOW: {
            "strategy": "per_piece",
            "unit_price": 0.03,
        },
    },
    "zipper": {
        ZipperEnum.ZIPPER: {
            "strategy": "per_width",
            "unit_price": 0.15,
        },
        ZipperEnum.CHILD_RESISTANT: {
            "strategy": "per_width",
            "unit_price": 0.30,
        },
        ZipperEnum.EASY_TEAR: {
            "strategy": "per_width",
            "unit_price": 0.10,
        },
    },
    "hang_hole": {
        HangHoleEnum.ROUND_HOLE: {
            "strategy": "per_piece",
            "unit_price": 0.01,
        },
        HangHoleEnum.EURO_HOLE: {
            "strategy": "per_piece",
            "unit_price": 0.02,
        },
    },
    "other_addons": {
        OtherAddonEnum.TEAR_NOTCH: {
            "strategy": "per_piece",
            "unit_price": 0.02,
        },
        OtherAddonEnum.TEAR_LINE: {
            "strategy": "per_piece",
            "unit_price": 0.03,
        },
        OtherAddonEnum.VALVE: {
            "strategy": "per_piece",
            "unit_price": 0.10,
        },
        OtherAddonEnum.SPOUT: {
            "strategy": "per_piece",
            "unit_price": 0.15,
        },
    },
}


def apply_pricing_strategy(
    strategy: str,
    unit_price: float,
    context: PriceContext
) -> float:
    if strategy == "per_area":
        return unit_price * context.area

    if strategy == "per_width":
        return unit_price * context.width

    if strategy == "per_piece":
        return unit_price

    if strategy == "fixed":
        return unit_price

    raise ValueError(f"Unsupported pricing strategy: {strategy}")


def calculate_item_cost(
    category: str,
    item_enum,
    context: PriceContext
) -> Optional[Dict[str, Any]]:
    if item_enum is None:
        return None

    config = PRICING_CONFIG.get(category, {}).get(item_enum)

    if config is None:
        return {
            "category": category,
            "code": item_enum.value,
            "strategy": "not_configured",
            "unit_price": 0.0,
            "unit_cost": 0.0,
            "configured": False,
        }

    strategy = config["strategy"]
    unit_price = config["unit_price"]
    unit_cost = apply_pricing_strategy(strategy, unit_price, context)

    return {
        "category": category,
        "code": item_enum.value,
        "strategy": strategy,
        "unit_price": unit_price,
        "unit_cost": round(unit_cost, 6),
        "configured": True,
    }