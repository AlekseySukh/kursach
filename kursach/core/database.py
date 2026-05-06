import sqlite3
from pathlib import Path
from core.seed import seed_if_empty

DB_PATH = Path("database.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS wood_types (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS properties (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('numeric', 'categorical'))
            );
            CREATE TABLE IF NOT EXISTS categorical_values (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                value       TEXT    NOT NULL,
                UNIQUE(property_id, value)
            );
            CREATE TABLE IF NOT EXISTS wood_properties (
                wood_id     INTEGER NOT NULL REFERENCES wood_types(id) ON DELETE CASCADE,
                property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                PRIMARY KEY (wood_id, property_id)
            );
            CREATE TABLE IF NOT EXISTS property_values (
                wood_id           INTEGER NOT NULL REFERENCES wood_types(id) ON DELETE CASCADE,
                property_id       INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                min_value         REAL,
                max_value         REAL,
                categorical_value TEXT,
                PRIMARY KEY (wood_id, property_id, categorical_value)
            );
            CREATE TABLE IF NOT EXISTS numeric_ranges (
                property_id INTEGER PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
                min_value   REAL NOT NULL,
                max_value   REAL NOT NULL
            );
        """)
        seed_if_empty(connection)


# Виды древесины

def get_wood_types() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT id, name FROM wood_types ORDER BY name").fetchall()
    return [dict(row) for row in rows]

def add_wood_type(name: str) -> int:
    with get_connection() as connection:
        cursor = connection.execute("INSERT INTO wood_types(name) VALUES(?)", (name.strip(),))
        return cursor.lastrowid

def delete_wood_type(wood_id: int):
    with get_connection() as connection:
        connection.execute("DELETE FROM wood_types WHERE id=?", (wood_id,))


# Свойства

def get_properties() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT id, name, type FROM properties ORDER BY name").fetchall()
    return [dict(row) for row in rows]

def add_property(name: str, prop_type: str) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO properties(name, type) VALUES(?,?)", (name.strip(), prop_type)
        )
        return cursor.lastrowid

def delete_property(property_id: int):
    with get_connection() as connection:
        connection.execute("DELETE FROM properties WHERE id=?", (property_id,))


# Возможные значения категориальных свойств

def get_categorical_values(property_id: int) -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT value FROM categorical_values WHERE property_id=? ORDER BY value",
            (property_id,)
        ).fetchall()
    return [row["value"] for row in rows]

def add_categorical_value(property_id: int, value: str):
    with get_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO categorical_values(property_id, value) VALUES(?,?)",
            (property_id, value.strip())
        )

def delete_categorical_value(property_id: int, value: str):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM categorical_values WHERE property_id=? AND value=?",
            (property_id, value)
        )
        # Удаляем это значение из всех видов где оно было задано
        connection.execute(
            "DELETE FROM property_values WHERE property_id=? AND categorical_value=?",
            (property_id, value)
        )


# Описание свойств вида

def get_wood_property_ids(wood_id: int) -> list[int]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT property_id FROM wood_properties WHERE wood_id=?", (wood_id,)
        ).fetchall()
    return [row["property_id"] for row in rows]

def set_wood_properties(wood_id: int, property_ids: list[int]):
    with get_connection() as connection:
        connection.execute("DELETE FROM wood_properties WHERE wood_id=?", (wood_id,))
        connection.executemany(
            "INSERT INTO wood_properties(wood_id, property_id) VALUES(?,?)",
            [(wood_id, property_id) for property_id in property_ids]
        )


# Значения свойств для конкретного вида

def get_property_values(wood_id: int, property_id: int) -> dict:
    with get_connection() as connection:
        prop = connection.execute(
            "SELECT type FROM properties WHERE id=?", (property_id,)
        ).fetchone()
        if not prop:
            return {}
        rows = connection.execute(
            "SELECT min_value, max_value, categorical_value "
            "FROM property_values WHERE wood_id=? AND property_id=?",
            (wood_id, property_id)
        ).fetchall()

        if prop["type"] == "numeric":
            if rows:
                return {"min": rows[0]["min_value"], "max": rows[0]["max_value"]}
            return {}
        else:
            valid_values = [row["value"] for row in connection.execute(
                "SELECT value FROM categorical_values WHERE property_id=?",
                (property_id,)
            ).fetchall()]
            values = [row["categorical_value"] for row in rows if row["categorical_value"] in valid_values]
            return {"values": values}

def set_numeric_value(wood_id: int, property_id: int, min_values: float, max_values: float):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM property_values WHERE wood_id=? AND property_id=?",
            (wood_id, property_id)
        )
        connection.execute(
            "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) "
            "VALUES(?,?,?,?,NULL)",
            (wood_id, property_id, min_values, max_values)
        )

def set_categorical_values(wood_id: int, property_id: int, values: list[str]):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM property_values WHERE wood_id=? AND property_id=?",
            (wood_id, property_id)
        )
        connection.executemany(
            "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) "
            "VALUES(?,?,NULL,NULL,?)",
            [(wood_id, property_id, value) for value in values]
        )


# Проверка полноты

def check_completeness() -> list[str]:
    errors = []
    with get_connection() as connection:
        woods = connection.execute("SELECT id, name FROM wood_types").fetchall()
        for wood in woods:
            property_ids = connection.execute(
                "SELECT property_id FROM wood_properties WHERE wood_id=?", (wood["id"],)
            ).fetchall()
            if not property_ids:
                errors.append(f'"{wood["name"]}": не задано ни одного свойства')
                continue
            for row in property_ids:
                property_id = row["property_id"]
                count = connection.execute(
                    "SELECT COUNT(*) as count FROM property_values WHERE wood_id=? AND property_id=?",
                    (wood["id"], property_id)
                ).fetchone()["count"]
                property_name = connection.execute(
                    "SELECT name FROM properties WHERE id=?", (property_id,)
                ).fetchone()["name"]
                property_type = connection.execute(
                    "SELECT type FROM properties WHERE id=?", (property_id,)
                ).fetchone()["type"]
                if count == 0:
                    errors.append(f'"{wood["name"]}": не заданы значения свойства "{property_name}"')

        # Проверяем что для всех числовых свойств задан общий диапазон
        numeric_properties = connection.execute(
            "SELECT id, name FROM properties WHERE type='numeric'"
        ).fetchall()
        for prop in numeric_properties:
            range_count = connection.execute(
                "SELECT COUNT(*) as count FROM numeric_ranges WHERE property_id=?",
                (prop["id"],)
            ).fetchone()["count"]
            if range_count == 0:
                errors.append(f'Свойство "{prop["name"]}": не задан общий допустимый диапазон')

    return errors



# Функции для работы с диапазонами

def get_numeric_range(property_id: int) -> dict:
    """Возвращает {"min": float, "max": float} или {} если не задан."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT min_value, max_value FROM numeric_ranges WHERE property_id=?",
            (property_id,)
        ).fetchone()
    if row:
        return {"min": row["min_value"], "max": row["max_value"]}
    return {}

def set_numeric_range(property_id: int, min_val: float, max_val: float):
    with get_connection() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO numeric_ranges(property_id, min_value, max_value) VALUES(?,?,?)",
            (property_id, min_val, max_val)
        )

def delete_numeric_range(property_id: int):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM numeric_ranges WHERE property_id=?", (property_id,)
        )