from abc import ABC, abstractmethod
from dataclasses import dataclass

from enums import PackingTypeEnum
from schemas import SizeModel


@dataclass
class SizeCalculationResult:
    packing_type: PackingTypeEnum
    total_area: float
    front_back_bottom_area: float
    two_side_area: float
    formula_name: str
    input_size: dict[str, float]


class BaseSizeCalculator(ABC):
    required_fields: tuple[str, ...] = ()

    def __init__(self, size: SizeModel):
        self.size = size

    def validate_required_fields(self):
        missing_fields = []

        for field in self.required_fields:
            value = getattr(self.size, field)
            if value is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                f"Missing required size fields for this packing type: {missing_fields}"
            )

    @abstractmethod
    def calculate_area(self) -> SizeCalculationResult:
        pass


class FlatBottomPouchSizeCalculator(BaseSizeCalculator):
    required_fields = ("w", "h", "g")

    def calculate_area(self) -> SizeCalculationResult:
        self.validate_required_fields()

        w = self.size.w
        h = self.size.h
        g = self.size.g

        # W = bag width
        # H = bag height
        # G = side expansion / gusset
        #
        # Front-back-bottom area:
        # (H * 2 + G + 0.03) * (W + 0.006)
        #
        # Two-side area:
        # (G + 0.006) * 2 * (H + 0.01)
        #
        # Total area:
        # front_back_bottom_area + two_side_area

        front_back_bottom_area = (h * 2 + g + 0.03) * (w + 0.006)
        two_side_area = (g + 0.006) * 2 * (h + 0.01)
        total_area = front_back_bottom_area + two_side_area

        return SizeCalculationResult(
            packing_type=PackingTypeEnum.FLAT_BOTTOM_POUCH,
            total_area=round(total_area, 6),
            front_back_bottom_area=round(front_back_bottom_area, 6),
            two_side_area=round(two_side_area, 6),
            formula_name="flat_bottom_pouch_total_area_formula",
            input_size={
                "w": w,
                "h": h,
                "g": g,
            },
        )


SIZE_CALCULATOR_MAP = {
    PackingTypeEnum.FLAT_BOTTOM_POUCH: FlatBottomPouchSizeCalculator,
}


def get_size_calculator(
    packing_type: PackingTypeEnum,
    size: SizeModel
) -> BaseSizeCalculator:
    calculator_class = SIZE_CALCULATOR_MAP.get(packing_type)

    if calculator_class is None:
        raise ValueError(
            f"No size calculator configured for packing type: {packing_type.value}"
        )

    return calculator_class(size)