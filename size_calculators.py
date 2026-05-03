from abc import ABC, abstractmethod
from dataclasses import dataclass

from enums import PackingTypeEnum
from schemas import SizeModel


@dataclass(frozen=True)
class CalculationResult:
    value: float
    formula_name: str
    input_size: dict[str, float]
    components: dict[str, float]


class BaseProductCalculator(ABC):
    required_fields: tuple[str, ...] = ()

    def __init__(self, size: SizeModel):
        self.size = size

    def validate_required_fields(self) -> None:
        missing_fields: list[str] = []

        for field in self.required_fields:
            value = getattr(self.size, field)
            if value is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                f"Missing required size fields for this product type: {missing_fields}"
            )


class AreaCalculator(ABC):
    @abstractmethod
    def calculate_area(self) -> CalculationResult:
        pass


class WidthCalculator(ABC):
    @abstractmethod
    def calculate_width(self) -> float:
        pass


class FlatBottomPouchCalculator(
    BaseProductCalculator,
    AreaCalculator,
    WidthCalculator,
):
    required_fields = ("w", "h", "g")

    def calculate_area(self) -> CalculationResult:
        self.validate_required_fields()

        w = self.size.w
        h = self.size.h
        g = self.size.g

        front_back_bottom_area = (h * 2 + g + 0.03) * (w + 0.006)
        two_side_area = (g + 0.006) * 2 * (h + 0.01)
        total_area = front_back_bottom_area + two_side_area

        return CalculationResult(
            value=round(total_area, 6),
            formula_name="flat_bottom_pouch_total_area_formula",
            input_size={
                "w": w,
                "h": h,
                "g": g,
            },
            components={
                "front_back_bottom_area": round(front_back_bottom_area, 6),
                "two_side_area": round(two_side_area, 6),
            },
        )

    def calculate_width(self) -> float:
        self.validate_required_fields()
        return self.size.w


PRODUCT_CALCULATOR_MAP: dict[
    PackingTypeEnum,
    type[BaseProductCalculator],
] = {
    PackingTypeEnum.FLAT_BOTTOM_POUCH: FlatBottomPouchCalculator,
}


def get_product_calculator(
    packing_type: PackingTypeEnum,
    size: SizeModel,
) -> BaseProductCalculator:
    calculator_class = PRODUCT_CALCULATOR_MAP.get(packing_type)

    if calculator_class is None:
        raise ValueError(
            f"No calculator configured for packing type: {packing_type.value}"
        )

    return calculator_class(size)