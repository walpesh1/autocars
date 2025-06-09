from datetime import datetime
import sqlite3
import pandas as pd

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    brand_id INTEGER,
    license_plate TEXT NOT NULL UNIQUE,
    FOREIGN KEY (category_id) REFERENCES Categories(id),
    FOREIGN KEY (brand_id) REFERENCES Brands(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CarStatuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER,
    status TEXT NOT NULL,
    return_date DATE,
    FOREIGN KEY (car_id) REFERENCES Cars(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Mileage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER,
    mileage REAL NOT NULL,
    FOREIGN KEY (car_id) REFERENCES Cars(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Администратор', 'Пользователь')),
    is_blocked BOOLEAN DEFAULT 0,
    last_login DATETIME,
    must_change_password BOOLEAN DEFAULT 1
);
""")

# Импорт данных из Автопарк.xlsx
df = pd.read_excel("Автопарк.xlsx", sheet_name="Лист_1")
df.columns = ['category', 'brand', 'license_plate']

# Добавляем категории и бренды
categories = df['category'].unique()
brands = df['brand'].unique()

for cat in categories:
    cursor.execute("INSERT OR IGNORE INTO Categories (name) VALUES (?)", (cat,))

for brand in brands:
    cursor.execute("INSERT OR IGNORE INTO Brands (name) VALUES (?)", (brand,))

# Добавляем автомобили
for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO Cars (category_id, brand_id, license_plate)
        SELECT 
            (SELECT id FROM Categories WHERE name = ?),
            (SELECT id FROM Brands WHERE name = ?),
            ?
    """, (row['category'], row['brand'], row['license_plate']))

analysis_date = "2025-03-01"
analysis_datetime = datetime.strptime(analysis_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")

# Запрос для расчета загрузки по каждому автомобилю
query = """
WITH CarUsage AS (
    SELECT 
        c.id AS car_id,
        c.license_plate,
        CASE 
            WHEN cs.status = 'Занят' AND cs.return_date IS NULL THEN julianday('now') - julianday(?)
            WHEN cs.status = 'Занят' AND cs.return_date > ? THEN julianday(cs.return_date) - julianday(?)
            WHEN cs.status = 'Занят' AND cs.return_date <= ? THEN julianday(cs.return_date) - julianday(?)
            ELSE 0
        END * 24 AS occupied_hours
    FROM Cars c
    LEFT JOIN CarStatuses cs ON c.id = cs.car_id
),
TotalHours AS (
    SELECT 
        car_id,
        license_plate,
        SUM(occupied_hours) AS total_occupied_hours
    FROM CarUsage
    GROUP BY car_id, license_plate
)
SELECT 
    license_plate,
    ROUND((total_occupied_hours / 24.0) * 100, 2) AS load_percentage
FROM TotalHours;
"""

cursor.execute(query, (analysis_date, analysis_date, analysis_date, analysis_date, analysis_date))

# Вывод результата
print("Процент загрузки автомобилей:")
for row in cursor.fetchall():
    print(f"Номерной знак: {row[0]}, Загрузка: {row[1]}%")

# Сохраняем изменения
conn.commit()
conn.close()
