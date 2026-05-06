from core import database as db


def classify(input_values) -> dict:
    wood_types = db.get_wood_types()
    properties_by_id = {prop["id"]: prop for prop in db.get_properties()}

    found = []
    skipped = []

    for wood in wood_types:
        wood_id = wood["id"]
        skip_reason = None

        assigned_properties = db.get_wood_property_ids(wood_id)

        if not assigned_properties:
            skip_reason = "не задано ни одного свойства"
            skipped.append({"id": wood_id, "name": wood["name"], "reason": skip_reason})
            continue

        for property_id in properties_by_id:
            prop = properties_by_id[property_id]
            if prop["name"] in input_values and property_id not in assigned_properties:
                skip_reason = f'"{prop["name"]}": свойство не задано для этого вида'
                break

        if skip_reason:
            skipped.append({"id": wood_id, "name": wood["name"], "reason": skip_reason})
            continue

        for property_id in assigned_properties:
            prop = properties_by_id[property_id]
            property_name = prop["name"]
            property_type = prop["type"]

            if property_name not in input_values:
                continue

            user_value = input_values[property_name]
            stored = db.get_property_values(wood_id, property_id)

            if property_type == "numeric":
                general_range = db.get_numeric_range(property_id)
                if not general_range:
                    skip_reason = f'"{property_name}": общий диапазон не задан в базе знаний'
                    break
                if not stored:
                    skip_reason = f'"{property_name}": значения не заданы в базе знаний'
                    break
                range_min = stored["min"]
                range_max = stored["max"]
                if not (range_min <= float(user_value) <= range_max):
                    skip_reason = f'"{property_name}" = {user_value} не входит в [{range_min}; {range_max}]'
                    break

            else:
                allowed = stored.get("values", [])
                if not allowed:
                    skip_reason = f'"{property_name}": значения не заданы в базе знаний'
                    break
                if str(user_value) not in allowed:
                    skip_reason = f'"{property_name}" = "{user_value}" не совпадает с {_format_list(allowed)}'
                    break

        if skip_reason:
            skipped.append({"id": wood_id, "name": wood["name"], "reason": skip_reason})
        else:
            found.append({"id": wood_id, "name": wood["name"]})

    return {"found": found, "skipped": skipped}


def _format_list(values: list[str]) -> str:
    return "{" + ", ".join(f'"{value}"' for value in values) + "}"