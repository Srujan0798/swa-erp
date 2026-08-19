import io
import json
from decimal import Decimal, InvalidOperation

import openpyxl  # type: ignore[import-untyped]

REQUIRED_COLUMNS = {"description", "unit", "quantity", "rate"}
OPTIONAL_COLUMNS = {"category", "specification"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


class BOQParseError(Exception):
    pass


def _cell_to_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if not cleaned:
            return Decimal("0")
        try:
            return Decimal(cleaned)
        except InvalidOperation as e:
            raise BOQParseError(f"Invalid decimal value: {value}") from e
    raise BOQParseError(f"Cannot convert {type(value).__name__} to Decimal")


def _normalize_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_").replace("-", "_")


def _validate_columns(headers: list[str]) -> dict[str, int]:
    normalized = [_normalize_header(h) for h in headers]
    mapping: dict[str, int] = {}
    for i, h in enumerate(normalized):
        if h in ALL_COLUMNS:
            mapping[h] = i

    missing = REQUIRED_COLUMNS - set(mapping.keys())
    if missing:
        raise BOQParseError(f"Missing required columns: {', '.join(sorted(missing))}")

    return mapping


def _build_row(line_number: int, row: list, col_map: dict[str, int]) -> dict:
    description = str(row[col_map["description"]] or "").strip()
    if not description:
        return {}

    unit = str(row[col_map["unit"]] or "").strip()
    if not unit:
        return {}

    quantity = _cell_to_decimal(row[col_map["quantity"]])
    rate = _cell_to_decimal(row[col_map["rate"]])
    amount = quantity * rate

    category = None
    if "category" in col_map:
        raw_cat = row[col_map["category"]]
        if raw_cat is not None:
            category = str(raw_cat).strip() or None

    specification = None
    if "specification" in col_map:
        raw_spec = row[col_map["specification"]]
        if raw_spec is not None:
            specification = str(raw_spec).strip() or None

    return {
        "line_number": line_number,
        "category": category,
        "description": description,
        "specification": specification,
        "unit": unit,
        "quantity": quantity,
        "rate": rate,
        "amount": amount,
    }


def parse_excel(file_bytes: bytes) -> list[dict]:
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    except Exception as e:
        raise BOQParseError(f"Cannot read Excel file: {e}") from e

    ws = wb.active
    if ws is None:
        raise BOQParseError("Excel file has no sheets")

    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 2:
        raise BOQParseError("Excel file must have a header row and at least one data row")

    headers = [str(c) if c is not None else "" for c in rows[0]]
    col_map = _validate_columns(headers)

    items: list[dict] = []
    line = 1
    for row in rows[1:]:
        if all(c is None or str(c).strip() == "" for c in row):
            continue
        item = _build_row(line, list(row), col_map)
        if item:
            items.append(item)
            line += 1

    return items


def parse_json(file_bytes: bytes) -> list[dict]:
    try:
        data = json.loads(file_bytes)
    except json.JSONDecodeError as e:
        raise BOQParseError(f"Invalid JSON: {e}") from e

    if not isinstance(data, list):
        raise BOQParseError("JSON must contain an array of BOQ items")

    items: list[dict] = []
    for idx, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            continue

        description = str(row.get("description", "")).strip()
        if not description:
            continue

        unit = str(row.get("unit", "")).strip()
        if not unit:
            continue

        quantity = _cell_to_decimal(row.get("quantity", 0))
        rate = _cell_to_decimal(row.get("rate", 0))
        amount = quantity * rate

        category_raw = row.get("category")
        specification_raw = row.get("specification")

        items.append(
            {
                "line_number": idx,
                "category": str(category_raw).strip() if category_raw else None,
                "description": description,
                "specification": str(specification_raw).strip() if specification_raw else None,
                "unit": unit,
                "quantity": quantity,
                "rate": rate,
                "amount": amount,
            }
        )

    return items
