from fastapi import APIRouter

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
from schemas import QuoteRequest


router = APIRouter(
    prefix="/quote",
    tags=["Quote"]
)


LABELS = {
    PackingTypeEnum.FLAT_BOTTOM_POUCH: "Flat Bottom Pouch",

    SustainabilityEnum.CLASSIC: "Classic",
    SustainabilityEnum.RECYCLABLE: "Recyclable",
    SustainabilityEnum.COMPOSTABLE: "Compostable",

    MaterialEnum.GENERAL: "General",
    MaterialEnum.FRESH_KEEP: "Fresh Keep",
    MaterialEnum.MAX_PROTECTION: "Max Protection",

    PrintingEnum.OUTSIDE: "Outside",
    PrintingEnum.DOUBLE_SIDE: "Double Side",
    PrintingEnum.THREE_SIDE: "3 side(.com)",
    PrintingEnum.FIVE_SIDE: "5 side(.com)",

    LaminationEnum.MATTE: "Matte",
    LaminationEnum.GLOSS: "Gloss",
    LaminationEnum.SOFT_TOUCH: "Soft Touch",

    FinishingEnum.NO_FINISHING: "No Finishing(.ai)",
    FinishingEnum.SPOT_UV: "Spot UV",
    FinishingEnum.HOT_FOIL_STAMPING: "Hot Foil Stamping",
    FinishingEnum.EMBOSS: "Emboss",
    FinishingEnum.WINDOW: "Window(.ai)",

    ZipperEnum.ZIPPER: "Zipper",
    ZipperEnum.CHILD_RESISTANT: "Child Resistant (.ai)",
    ZipperEnum.EASY_TEAR: "Easy Tear (.ai)",

    HangHoleEnum.ROUND_HOLE: "Round Hole",
    HangHoleEnum.EURO_HOLE: "Euro Hole",

    OtherAddonEnum.TEAR_NOTCH: "Tear Notch",
    OtherAddonEnum.TEAR_LINE: "Tear Line (.ai)",
    OtherAddonEnum.VALVE: "Valve",
    OtherAddonEnum.SPOUT: "Spout (.ai)",
}


def label(value):
    return LABELS.get(value, str(value))


@router.post("/read")
def read_quote_options(order: QuoteRequest):
    selected_addon_enums = []

    if not order.addons.no_addon:
        if order.addons.zipper:
            selected_addon_enums.append(order.addons.zipper)

        if order.addons.hang_hole:
            selected_addon_enums.append(order.addons.hang_hole)

        if order.addons.other:
            selected_addon_enums.extend(order.addons.other)

    if order.addons.no_addon:
        selected_addon_labels = ["No add-on (.ai)"]
    elif selected_addon_enums:
        selected_addon_labels = [label(item) for item in selected_addon_enums]
    else:
        selected_addon_labels = ["None"]

    formatted_details = [
        f"Quantity: {order.quantity}",
        f"Size: W:{order.size.w}, H:{order.size.h}, G:{order.size.g}",
        f"Packing Type: {label(order.packing_type)}",
        f"Sustainability: {label(order.sustainability)}",
        f"Material: {label(order.material)}",
        f"Printing: {label(order.printing)}",
        f"Lamination: {label(order.lamination)}",
        f"Finishing: {label(order.finishing)}",
        f"Add-ons: {', '.join(selected_addon_labels)}",
    ]

    return {
        "status": "success",
        "message": "Quote options parsed successfully. Price calculation is not included in this version.",
        "formatted_details": formatted_details,
        "parsed_data": {
            "quantity": order.quantity,
            "size": {
                "w": order.size.w,
                "h": order.size.h,
                "g": order.size.g,
            },
            "packing_type": {
                "code": order.packing_type.value,
                "label": label(order.packing_type),
            },
            "sustainability": {
                "code": order.sustainability.value,
                "label": label(order.sustainability),
            },
            "material": {
                "code": order.material.value,
                "label": label(order.material),
            },
            "printing": {
                "code": order.printing.value,
                "label": label(order.printing),
            },
            "lamination": {
                "code": order.lamination.value,
                "label": label(order.lamination),
            },
            "finishing": {
                "code": order.finishing.value,
                "label": label(order.finishing),
            },
            "addons": {
                "no_addon": order.addons.no_addon,
                "codes": [item.value for item in selected_addon_enums],
                "labels": selected_addon_labels,
            },
        },
    }