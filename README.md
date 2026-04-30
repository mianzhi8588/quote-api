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