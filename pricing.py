from enum import Enum
from typing import Optional, TypedDict, TypeAlias, Union

from enums import (
    MaterialEnum,
    PrintingEnum,
    LaminationEnum,
    FinishingEnum,
    ZipperEnum,
    HangHoleEnum,
    OtherAddonEnum,
)

from size_calculators import (
    BaseProductCalculator,
    AreaCalculator,
    WidthCalculator,
)


class PricingStrategyEnum(str, Enum):
    PER_AREA = "per_area"
    PER_WIDTH = "per_width"
    PER_PIECE = "per_piece"
    FIXED = "fixed"
    NOT_CONFIGURED = "not_configured"


PriceableItem: TypeAlias = Union[
    MaterialEnum,
    PrintingEnum,
    LaminationEnum,
    FinishingEnum,
    ZipperEnum,
    HangHoleEnum,
    OtherAddonEnum,
]


class PricingRule(TypedDict):
    strategy: PricingStrategyEnum
    unit_price: float


class PriceBreakdownItem(TypedDict, total=False):
    category: str
    code: str
    label: str
    strategy: str
    unit_price: float
    unit_cost: float
    configured: bool


PRICING_CONFIG: dict[str, dict[PriceableItem, PricingRule]] = {
    "material": {
        MaterialEnum.GENERAL: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.50,
        },
        MaterialEnum.FRESH_KEEP: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.80,
        },
        MaterialEnum.MAX_PROTECTION: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 1.20,
        },
    },
    "printing": {
        PrintingEnum.OUTSIDE: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.10,
        },
        PrintingEnum.DOUBLE_SIDE: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.18,
        },
        PrintingEnum.THREE_SIDE: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.22,
        },
        PrintingEnum.FIVE_SIDE: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.30,
        },
    },
    "lamination": {
        LaminationEnum.MATTE: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.05,
        },
        LaminationEnum.GLOSS: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.05,
        },
        LaminationEnum.SOFT_TOUCH: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.12,
        },
    },
    "finishing": {
        FinishingEnum.NO_FINISHING: {
            "strategy": PricingStrategyEnum.FIXED,
            "unit_price": 0.00,
        },
        FinishingEnum.SPOT_UV: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.08,
        },
        FinishingEnum.HOT_FOIL_STAMPING: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.15,
        },
        FinishingEnum.EMBOSS: {
            "strategy": PricingStrategyEnum.PER_AREA,
            "unit_price": 0.10,
        },
        FinishingEnum.WINDOW: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.03,
        },
    },
    "zipper": {
        ZipperEnum.ZIPPER: {
            "strategy": PricingStrategyEnum.PER_WIDTH,
            "unit_price": 0.15,
        },
        ZipperEnum.CHILD_RESISTANT: {
            "strategy": PricingStrategyEnum.PER_WIDTH,
            "unit_price": 0.30,
        },
        ZipperEnum.EASY_TEAR: {
            "strategy": PricingStrategyEnum.PER_WIDTH,
            "unit_price": 0.10,
        },
    },
    "hang_hole": {
        HangHoleEnum.ROUND_HOLE: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.01,
        },
        HangHoleEnum.EURO_HOLE: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.02,
        },
    },
    "other_addons": {
        OtherAddonEnum.TEAR_NOTCH: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.02,
        },
        OtherAddonEnum.TEAR_LINE: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.03,
        },
        OtherAddonEnum.VALVE: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.10,
        },
        OtherAddonEnum.SPOUT: {
            "strategy": PricingStrategyEnum.PER_PIECE,
            "unit_price": 0.15,
        },
    },
}


def get_metric_for_strategy(
    strategy: PricingStrategyEnum,
    calculator: BaseProductCalculator,
) -> float:
    if strategy == PricingStrategyEnum.PER_AREA:
        if not isinstance(calculator, AreaCalculator):
            raise ValueError(
                "This product calculator does not support area-based pricing."
            )

        return calculator.calculate_area().value

    if strategy == PricingStrategyEnum.PER_WIDTH:
        if not isinstance(calculator, WidthCalculator):
            raise ValueError(
                "This product calculator does not support width-based pricing."
            )

        return calculator.calculate_width()

    if strategy == PricingStrategyEnum.PER_PIECE:
        return 1.0

    if strategy == PricingStrategyEnum.FIXED:
        return 1.0

    raise ValueError(f"Unsupported pricing strategy: {strategy.value}")


def calculate_item_cost(
    category: str,
    item_enum: Optional[PriceableItem],
    calculator: BaseProductCalculator,
) -> Optional[PriceBreakdownItem]:
    if item_enum is None:
        return None

    config = PRICING_CONFIG.get(category, {}).get(item_enum)

    if config is None:
        return {
            "category": category,
            "code": item_enum.value,
            "strategy": PricingStrategyEnum.NOT_CONFIGURED.value,
            "unit_price": 0.0,
            "unit_cost": 0.0,
            "configured": False,
        }

    strategy = config["strategy"]
    unit_price = config["unit_price"]
    metric = get_metric_for_strategy(strategy, calculator)
    unit_cost = unit_price * metric

    return {
        "category": category,
        "code": item_enum.value,
        "strategy": strategy.value,
        "unit_price": unit_price,
        "unit_cost": round(unit_cost, 6),
        "configured": True,
    }