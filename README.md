```markdown
# Quote Option Reader API

This is a FastAPI project for reading and validating packaging quote options.

## Features

- Read quantity and size
- Validate fixed option fields using Enum
- Validate add-ons logic
- Return standardized formatted details
- No price calculation in this version

## Run

```bash
python -m uvicorn main:app --reload

## Current Update

This version adds:

- OOP-based size calculation for Flat Bottom Pouch
- Required W/H/G validation
- Area calculation:
  - front_back_bottom_area = (H * 2 + G + 0.03) * (W + 0.006)
  - two_side_area = (G + 0.006) * 2 * (H + 0.01)
  - total_area = front_back_bottom_area + two_side_area
- Demo pricing configurator with per_area, per_width, per_piece, and fixed strategies

Note: pricing values are demo placeholders and should be replaced with final business rules later.