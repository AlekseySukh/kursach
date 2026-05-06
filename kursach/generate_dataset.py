import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import init_db, get_wood_types, get_properties, get_wood_property_ids, get_property_values, get_categorical_values

SAMPLES_PER_WOOD = 200
OUTPUT_FILE = Path(__file__).parent / "dataset.csv"


def generate():
    init_db()

    wood_types = get_wood_types()
    properties = get_properties()

    rows = []

    for wood in wood_types:
        wood_id = wood["id"]
        assigned_property_ids = set(get_wood_property_ids(wood_id))

        for _ in range(SAMPLES_PER_WOOD):
            row = {}

            for prop in properties:
                if prop["id"] not in assigned_property_ids:
                    continue

                stored_values = get_property_values(wood_id, prop["id"])

                if prop["type"] == "numeric":
                    range_min = stored_values.get("min", 0)
                    range_max = stored_values.get("max", 0)
                    row[prop["name"]] = round(random.uniform(range_min, range_max), 2)

                else:
                    options = stored_values.get("values", [])
                    row[prop["name"]] = random.choice(options) if options else ""

            row["Вид"] = wood["name"]
            rows.append(row)

    if not rows:
        print("Нет данных в БД.")
        return

    columns = [prop["name"] for prop in properties] + ["Вид"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Датасет сохранён: {OUTPUT_FILE}")
    print(f"Строк: {len(rows)}, видов: {len(wood_types)}, свойств: {len(properties)}")


if __name__ == "__main__":
    generate()