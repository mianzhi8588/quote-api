from fastapi import APIRouter, HTTPException

from size_calculators import (
    get_product_calculator,
    AreaCalculator,
    WidthCalculator,
)

from pricing import calculate_item_cost

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
from quote_storage import save_quote_price, get_quote_price

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
    try:
        calculator = get_product_calculator(order.packing_type, order.size)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    area_result = None
    width_value = None

    if isinstance(calculator, AreaCalculator):
        area_result = calculator.calculate_area()

    if isinstance(calculator, WidthCalculator):
        width_value = calculator.calculate_width()

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

    price_breakdown = []

    base_price_items = [
        ("material", order.material),
        ("printing", order.printing),
        ("lamination", order.lamination),
        ("finishing", order.finishing),
    ]

    try:
        for category, item in base_price_items:
            item_cost = calculate_item_cost(category, item, calculator)

            if item_cost:
                item_cost["label"] = label(item)
                price_breakdown.append(item_cost)

        if not order.addons.no_addon:
            addon_price_items = [
                ("zipper", order.addons.zipper),
                ("hang_hole", order.addons.hang_hole),
            ]

            for category, item in addon_price_items:
                item_cost = calculate_item_cost(category, item, calculator)

                if item_cost:
                    item_cost["label"] = label(item)
                    price_breakdown.append(item_cost)

            for addon in order.addons.other:
                item_cost = calculate_item_cost("other_addons", addon, calculator)

                if item_cost:
                    item_cost["label"] = label(addon)
                    price_breakdown.append(item_cost)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    unit_price = sum(item["unit_cost"] for item in price_breakdown)
    total_price = unit_price * order.quantity

    quote_record = save_quote_price(
          unit_price=unit_price,
          total_price=total_price,
          quantity=order.quantity,
          currency="USD",
)

    formatted_details = [
        f"Quantity: {order.quantity}",
        f"Size: W:{order.size.w}, H:{order.size.h}, G:{order.size.g}",
        f"Area: {area_result.value if area_result else None}",
        f"Area Components: {area_result.components if area_result else None}",
        f"Width: {width_value}",
        f"Packing Type: {label(order.packing_type)}",
        f"Sustainability: {label(order.sustainability)}",
        f"Material: {label(order.material)}",
        f"Printing: {label(order.printing)}",
        f"Lamination: {label(order.lamination)}",
        f"Finishing: {label(order.finishing)}",
        f"Add-ons: {', '.join(selected_addon_labels)}",
        f"Estimated Unit Price: {round(unit_price, 4)}",
        f"Estimated Total Price: {round(total_price, 2)}",
    ]

    return {
        "status": "success",
        "message": "Quote options parsed successfully.",
         "quote_id": quote_record.quote_id,
         "price": quote_record.to_price_response(),
        "formatted_details": formatted_details,

        "size_calculation": {
            "packing_type": {
                "code": order.packing_type.value,
                "label": label(order.packing_type),
            },
            "area": None if area_result is None else {
                "value": area_result.value,
                "formula_name": area_result.formula_name,
                "input_size": area_result.input_size,
                "components": area_result.components,
            },
            "width": width_value,
        },

        "pricing": {
            "pricing_method": "config_based",
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
                "area": area_result.value if area_result else None,
                "area_components": area_result.components if area_result else None,
                "width": width_value,
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

@router.get("/{quote_id}")
def get_quote_by_id(quote_id: str):
    quote_record = get_quote_price(quote_id)

    if quote_record is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found or expired."
        )

    return {
        "status": "success",
        "quote_id": quote_record.quote_id,
        "price": quote_record.to_price_response(),
    }