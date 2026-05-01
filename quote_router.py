from fastapi import APIRouter, HTTPException
from size_calculators import get_size_calculator
from pricing import PriceContext, calculate_item_cost

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
    # 1. Size validation and area calculation
    # This uses OOP calculators. Different packing types can have different calculators.
    try:
        size_calculator = get_size_calculator(order.packing_type, order.size)
        size_result = size_calculator.calculate_area()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    # 2. Keep selected add-ons as enum objects for calculation/config matching
    selected_addon_enums = []

    if not order.addons.no_addon:
        if order.addons.zipper:
            selected_addon_enums.append(order.addons.zipper)

        if order.addons.hang_hole:
            selected_addon_enums.append(order.addons.hang_hole)

        if order.addons.other:
            selected_addon_enums.extend(order.addons.other)

    # 3. Convert enum objects to labels only for display
    if order.addons.no_addon:
        selected_addon_labels = ["No add-on (.ai)"]
    elif selected_addon_enums:
        selected_addon_labels = [label(item) for item in selected_addon_enums]
    else:
        selected_addon_labels = ["None"]

    # 4. Pricing configurator demo
    # Pricing uses enum/code, not labels.
    price_context = PriceContext(
        area=size_result.total_area,
        width=order.size.w,
        quantity=order.quantity,
    )

    price_breakdown = []

    base_price_items = [
        ("material", order.material),
        ("printing", order.printing),
        ("lamination", order.lamination),
        ("finishing", order.finishing),
    ]

    for category, item in base_price_items:
        item_cost = calculate_item_cost(category, item, price_context)

        if item_cost:
            item_cost["label"] = label(item)
            price_breakdown.append(item_cost)

    if not order.addons.no_addon:
        addon_price_items = [
            ("zipper", order.addons.zipper),
            ("hang_hole", order.addons.hang_hole),
        ]

        for category, item in addon_price_items:
            item_cost = calculate_item_cost(category, item, price_context)

            if item_cost:
                item_cost["label"] = label(item)
                price_breakdown.append(item_cost)

        for addon in order.addons.other:
            item_cost = calculate_item_cost("other_addons", addon, price_context)

            if item_cost:
                item_cost["label"] = label(addon)
                price_breakdown.append(item_cost)

    unit_price = sum(item["unit_cost"] for item in price_breakdown)
    total_price = unit_price * order.quantity

    formatted_details = [
        f"Quantity: {order.quantity}",
        f"Size: W:{order.size.w}, H:{order.size.h}, G:{order.size.g}",
        f"Front/Back/Bottom Area: {size_result.front_back_bottom_area}",
        f"Two-Side Area: {size_result.two_side_area}",
        f"Total Area: {size_result.total_area}",
        f"Packing Type: {label(order.packing_type)}",
        f"Sustainability: {label(order.sustainability)}",
        f"Material: {label(order.material)}",
        f"Printing: {label(order.printing)}",
        f"Lamination: {label(order.lamination)}",
        f"Finishing: {label(order.finishing)}",
        f"Add-ons: {', '.join(selected_addon_labels)}",
        f"Demo Unit Price: {round(unit_price, 4)}",
        f"Demo Total Price: {round(total_price, 2)}",
    ]

    return {
        "status": "success",
        "message": "Quote options parsed successfully. Pricing is demo/config-driven and should be replaced with final business rules.",
        "formatted_details": formatted_details,

        "size_calculation": {
            "packing_type": {
                "code": order.packing_type.value,
                "label": label(order.packing_type),
            },
            "formula_name": size_result.formula_name,
            "input_size": size_result.input_size,
            "front_back_bottom_area": size_result.front_back_bottom_area,
            "two_side_area": size_result.two_side_area,
            "total_area": size_result.total_area,
        },

        "pricing": {
            "is_demo_pricing": True,
            "unit_price": round(unit_price, 6),
            "quantity": order.quantity,
            "total_price": round(total_price, 2),
            "breakdown": price_breakdown,
        },

        "parsed_data": {
            "quantity": order.quantity,

            "size": {
                "w": order.size.w,
                "h": order.size.h,
                "g": order.size.g,
                "front_back_bottom_area": size_result.front_back_bottom_area,
                "two_side_area": size_result.two_side_area,
                "total_area": size_result.total_area,
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