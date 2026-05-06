from core import database as db
from core.seed import seed_if_empty


def reset_to_defaults():
    clear_db()
    with db.get_connection() as connection:
        seed_if_empty(connection)


def clear_db():
    with db.get_connection() as connection:
        connection.executescript("""
            DELETE FROM property_values;
            DELETE FROM wood_properties;
            DELETE FROM categorical_values;
            DELETE FROM properties;
            DELETE FROM wood_types;
        """)


def fill_defaults():
    with db.get_connection() as connection:
        seed_if_empty(connection)