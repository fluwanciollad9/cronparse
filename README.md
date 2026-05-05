# cronparse

A Python library for parsing and humanizing cron expressions with conflict detection.

## Installation

```bash
pip install cronparse
```

## Usage

```python
from cronparse import CronExpression

# Parse a cron expression
cron = CronExpression("0 9 * * 1-5")

# Get a human-readable description
print(cron.humanize())
# Output: "At 09:00 AM, Monday through Friday"

# Validate the expression
print(cron.is_valid())
# Output: True

# Detect conflicts between two expressions
cron2 = CronExpression("0 9 * * 3")
conflicts = cron.conflicts_with(cron2)
print(conflicts)
# Output: True  (both fire at 09:00 on Wednesdays)

# Inspect individual fields
print(cron.minute)   # 0
print(cron.hour)     # 9
print(cron.weekday)  # 1-5
```

## Features

- Parse and validate standard 5-field cron expressions
- Generate human-readable descriptions in plain English
- Detect scheduling conflicts between two or more expressions
- Support for special strings (`@daily`, `@hourly`, `@reboot`, etc.)

## License

This project is licensed under the [MIT License](LICENSE).