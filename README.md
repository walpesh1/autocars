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
