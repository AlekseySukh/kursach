import sqlite3


def seed_if_empty(connection: sqlite3.Connection):
    if connection.execute("SELECT COUNT(*) FROM wood_types").fetchone()[0] > 0:
        return

    _insert_wood_types(connection)
    _insert_properties(connection)
    _insert_property_values(connection)


def _insert_wood_types(connection):
    names = [
        "Лиственница", "Сосна обыкновенная", "Ель", "Кедр", "Пихта сибирская",
        "Граб", "Акация белая", "Груша", "Дуб", "Клён",
        "Ясень обыкновенный", "Бук", "Вяз", "Берёза", "Орех",
        "Ольха", "Осина", "Липа", "Ива",
    ]
    for name in names:
        connection.execute("INSERT INTO wood_types(name) VALUES(?)", (name,))


def _insert_properties(connection):
    connection.execute("INSERT INTO properties(name, type) VALUES('Плотность', 'numeric')")
    connection.execute("INSERT INTO properties(name, type) VALUES('Твёрдость', 'numeric')")
    connection.execute("INSERT INTO properties(name, type) VALUES('Стабильность', 'numeric')")
    connection.execute("INSERT INTO properties(name, type) VALUES('Цвет', 'categorical')")

    connection.execute("INSERT INTO numeric_ranges(property_id, min_value, max_value) SELECT id, 0, 1000 FROM properties WHERE name='Плотность'")
    connection.execute("INSERT INTO numeric_ranges(property_id, min_value, max_value) SELECT id, 0, 10 FROM properties WHERE name='Твёрдость'")
    connection.execute("INSERT INTO numeric_ranges(property_id, min_value, max_value) SELECT id, 1, 5 FROM properties WHERE name='Стабильность'")

    color_property_id = connection.execute("SELECT id FROM properties WHERE name='Цвет'").fetchone()[0]
    colors = ["Коричневый", "Жёлтый", "Серый", "Красный", "Белый", "Зелёный", "Оранжевый"]
    for color in colors:
        connection.execute(
            "INSERT INTO categorical_values(property_id, value) VALUES(?,?)",
            (color_property_id, color)
        )

    all_woods = connection.execute("SELECT id FROM wood_types").fetchall()
    all_props = connection.execute("SELECT id FROM properties").fetchall()
    for wood in all_woods:
        for prop in all_props:
            connection.execute(
                "INSERT INTO wood_properties(wood_id, property_id) VALUES(?,?)",
                (wood["id"], prop["id"])
            )


def _insert_property_values(connection):
    density_id = connection.execute("SELECT id FROM properties WHERE name='Плотность'").fetchone()[0]
    hardness_id = connection.execute("SELECT id FROM properties WHERE name='Твёрдость'").fetchone()[0]
    stability_id = connection.execute("SELECT id FROM properties WHERE name='Стабильность'").fetchone()[0]
    color_id = connection.execute("SELECT id FROM properties WHERE name='Цвет'").fetchone()[0]

    numeric_data = [ ("Лиственница", 550, 620, 3.0, 3.5, 3.0, 4.0),
                    ("Сосна обыкновенная", 450, 520, 2.5, 3.0, 3.0, 4.0),
                    ("Ель", 430, 480, 2.0, 2.5, 3.0, 4.0),
                    ("Кедр", 390, 450, 1.5, 2.0, 2.0, 3.0),
                    ("Пихта сибирская", 370, 430, 1.5, 2.0, 2.0, 3.0),
                    ("Граб", 750, 850, 6.5, 7.5, 3.0, 4.0),
                    ("Акация белая", 730, 800, 5.5, 6.5, 3.0, 4.0),
                    ("Груша",  650, 730, 5.0, 6.0, 4.0, 5.0),
                    ("Дуб", 650, 720, 3.5, 4.5, 3.0, 4.0),
                    ("Клён", 600, 700, 4.0, 5.0, 3.0, 4.0),
                    ("Ясень обыкновенный", 650, 720, 4.5, 5.5, 3.0, 4.0),
                    ("Бук", 620, 700, 4.0, 5.0, 2.0, 3.0),
                    ("Вяз", 550, 640, 3.5, 4.5, 2.0, 3.0),
                    ("Берёза",600, 670, 3.0, 3.5, 2.0, 3.0),
                    ("Орех",  580, 680, 3.5, 4.5, 3.0, 4.0),
                    ("Ольха", 430, 530, 2.0, 2.5, 3.0, 4.0),
                    ("Осина", 430, 500, 1.5, 2.0, 3.0, 4.0),
                    ("Липа", 390, 490, 1.5, 2.0, 3.0, 4.0),
                    ("Ива", 420, 500, 2.0, 2.5, 2.0, 3.0), ]

    for name, density_min, density_max, hardness_min, hardness_max, stability_min, stability_max in numeric_data:
        wood_id = connection.execute("SELECT id FROM wood_types WHERE name=?", (name,)).fetchone()[0]
        connection.execute(
            "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) VALUES(?,?,?,?,NULL)",
            (wood_id, density_id, density_min, density_max)
        )
        connection.execute(
            "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) VALUES(?,?,?,?,NULL)",
            (wood_id, hardness_id, hardness_min, hardness_max)
        )
        connection.execute(
            "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) VALUES(?,?,?,?,NULL)",
            (wood_id, stability_id, stability_min, stability_max)
        )

    color_data = { "Лиственница":  ["Коричневый", "Жёлтый"],
                  "Сосна обыкновенная": ["Жёлтый", "Оранжевый"],
                "Ель":  ["Белый", "Жёлтый"],
                "Кедр":  ["Жёлтый", "Коричневый"],
                "Пихта сибирская":  ["Белый", "Жёлтый"],
                "Граб":  ["Белый", "Серый"],
                "Акация белая":  ["Жёлтый", "Зелёный"],
                "Груша": ["Коричневый", "Красный"],
                "Дуб":   ["Коричневый"],
                "Клён":  ["Белый", "Жёлтый"],
                "Ясень обыкновенный": ["Коричневый", "Жёлтый"],
                "Бук":  ["Коричневый", "Оранжевый"],
                "Вяз":  ["Коричневый", "Серый"],
                "Берёза":["Белый", "Жёлтый"],
                "Орех":  ["Коричневый", "Серый"],
                "Ольха":  ["Коричневый", "Оранжевый"],
                "Осина":  ["Белый", "Зелёный"],
                "Липа":  ["Белый", "Жёлтый"],
                "Ива": ["Белый", "Серый"],
                }

    for wood_name, colors in color_data.items():
        wood_id = connection.execute("SELECT id FROM wood_types WHERE name=?", (wood_name,)).fetchone()[0]
        for color in colors:
            connection.execute(
                "INSERT INTO property_values(wood_id, property_id, min_value, max_value, categorical_value) VALUES(?,?,NULL,NULL,?)",
                (wood_id, color_id, color)
            )