from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

from enums import (
    PackingTypeEnum,
    SustainabilityEnum,
    MaterialEnum,
    PrintingEnum,
    LaminationEnum,
    FinishingEnum,
    ZipperEnum,
    HangHoleEnum,
    OtherAddonEnum,
)


class SizeModel(BaseModel):
    w: float = Field(..., gt=0, description="Width")
    h: float = Field(..., gt=0, description="Height")
    g: float = Field(..., gt=0, description="Gusset")


class AddonsModel(BaseModel):
    no_addon: bool = False

    # Zipper 组：只能选一个
    zipper: Optional[ZipperEnum] = None

    # Hang Hole 组：只能选一个
    hang_hole: Optional[HangHoleEnum] = None

    # Other 组：可以多选
    other: List[OtherAddonEnum] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_addons(self):
        if self.no_addon:
            if self.zipper is not None or self.hang_hole is not None or len(self.other) > 0:
                raise ValueError(
                    "If no_addon is true, zipper, hang_hole, and other add-ons must be empty."
                )
        return self


class QuoteRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    size: SizeModel

    packing_type: PackingTypeEnum
    sustainability: SustainabilityEnum
    material: MaterialEnum
    printing: PrintingEnum
    lamination: LaminationEnum
    finishing: FinishingEnum
    addons: AddonsModel