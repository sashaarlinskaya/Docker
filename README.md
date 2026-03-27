```
#!/usr/bin/env python3
"""
Генератор синтетических данных: Складской учёт / Inventory.
Вариант: Склад / Управление запасами / Анализ остатков и скорости продаж.

Запуск: python generate_data.py
Результат: data/inventory.csv
"""

import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
NUM_ROWS = 2_000
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "inventory.csv")

# --- Параметры генерации ---

# Категории товаров (новые)
CATEGORIES = [
    "Комплектующие для ПК", "Смарт-устройства", "Аксессуары для гаджетов", "Сетевое оборудование",
    "Периферия", "Аудиотехника", "Видеотехника", "Оргтехника",
    "Расходные материалы", "Защитные покрытия", "Кабельная продукция", "Системы хранения данных"
]

# Поставщики (новые)
SUPPLIERS = [
    "ООО 'ТехноЛогистик'", "АО 'Цифровые Решения'", "ИП Коваленко Д.А.", "Группа 'ИТ-Снаб'",
    "Компания 'ЭлектронТрейд'", "ООО 'ГаджетОпт'", "АО 'СмартТехно'", "ТД 'Компьютерный Мир'",
    "ООО 'НейроИмпульс'", "ИП Власова Е.М.", "ЗАО 'КиберСклад'", "Торговый дом 'ТехноПарк'"
]

# Весовое распределение для скорости продаж (units per day)
# Большинство товаров продаются медленно, некоторые - быстро
SALES_SPEED_WEIGHTS = {
    0.1: 30,   # очень медленно
    0.5: 25,   # медленно
    1.0: 20,   # средне
    2.0: 15,   # быстро
    5.0: 8,    # очень быстро
    10.0: 2    # супер-быстро
}

random.seed(SEED)

def weighted_sales_speed() -> float:
    """Выбор скорости продаж с учётом весов."""
    speeds = list(SALES_SPEED_WEIGHTS.keys())
    weights = list(SALES_SPEED_WEIGHTS.values())
    return random.choices(speeds, weights=weights, k=1)[0]

def generate_expiry_date() -> str:
    """Генерация срока годности (для продуктов - короткий срок, для других - длинный)."""
    category = random.choice(CATEGORIES)
    
    # Для некоторых категорий - короткий срок годности
    if category in ["Расходные материалы", "Защитные покрытия"]:
        # Для расходников - от 30 до 365 дней
        days = random.randint(30, 365)
    elif category in ["Кабельная продукция", "Системы хранения данных"]:
        # Для кабелей и систем хранения - от 1 до 3 лет
        days = random.randint(365, 1095)
    else:
        # Для остальных товаров - от 2 до 5 лет или бессрочно (NULL)
        if random.random() < 0.3:  # 30% товаров бессрочные
            return "NULL"
        else:
            days = random.randint(730, 1825)
    
    expiry_date = datetime.now() + timedelta(days=days)
    return expiry_date.strftime("%Y-%m-%d")

def generate_sku(index: int) -> str:
    """Генерация уникального SKU."""
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    numbers = str(index).zfill(6)
    return f"{letters}-{numbers}"

def generate() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "sku",
        "product_name",
        "category",
        "supplier",
        "stock_quantity",
        "sales_speed_per_day",
        "expiry_date",
        "warehouse_location",
        "price_rub",
        "reorder_point"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, NUM_ROWS + 1):
            sku = generate_sku(i)
            category = random.choice(CATEGORIES)
            supplier = random.choice(SUPPLIERS)
            
            # Генерация остатка на складе (от 0 до 1000)
            stock_quantity = random.randint(0, 1000)
            
            # Скорость продаж в единицах в день
            sales_speed = weighted_sales_speed()
            
            # Срок годности
            expiry_date = generate_expiry_date()
            
            # Локация на складе
            warehouse_location = f"Сектор {random.randint(1, 15)}-Ряд {random.randint(1, 25)}-Ячейка {random.randint(1, 40)}"
            
            # Цена в рублях
            price_rub = round(random.uniform(150, 120000), 2)
            
            # Точка заказа (reorder point) - когда нужно заказывать новый товар
            reorder_point = int(sales_speed * random.randint(7, 30))  # от 7 до 30 дней продаж
            
            # Название товара (новые)
            product_names = {
                "Комплектующие для ПК": ["Процессор Intel Core i9", "Видеокарта RTX 4080", "Материнская плата B760", "Оперативная память DDR5", "SSD NVMe 1TB"],
                "Смарт-устройства": ["Умная колонка", "Фитнес-браслет", "Умные часы Pro", "Wi-Fi розетка", "Датчик движения"],
                "Аксессуары для гаджетов": ["Защитное стекло", "Чехол-книжка", "Магнитный держатель", "Беспроводная зарядка", "Портативный аккумулятор"],
                "Сетевое оборудование": ["Маршрутизатор WiFi 6", "Управляемый коммутатор", "Точка доступа", "Сетевой адаптер", "Mesh-система"],
                "Периферия": ["Игровая клавиатура", "Беспроводная мышь", "Игровая гарнитура", "Web-камера 4K", "Геймпад"],
                "Аудиотехника": ["Наушники TWS", "Портативная колонка", "Студийные мониторы", "Звуковая карта", "Микрофон конденсаторный"],
                "Видеотехника": ["4K монитор", "Проектор", "Видеорегистратор", "Экшн-камера", "Домашний кинотеатр"],
                "Оргтехника": ["МФУ лазерное", "Сканер документов", "Ламинатор", "Уничтожитель бумаг", "Переплетчик"],
                "Расходные материалы": ["Тонер-картридж", "Бумага для печати", "Чернила для принтера", "Фотобарабан", "Термоэтикетки"],
                "Защитные покрытия": ["Антивандальная пленка", "Защитная пленка для экрана", "Силиконовый бампер", "Бронированное стекло", "Гидрофобное покрытие"],
                "Кабельная продукция": ["Кабель HDMI 2.1", "Оптический кабель", "USB-C кабель", "Удлинитель", "Переходник DisplayPort"],
                "Системы хранения данных": ["Внешний HDD 4TB", "NAS сервер", "Сетевой накопитель", "Флеш-накопитель 128GB", "Карта памяти microSD"]
            }
            
            product_name = f"{random.choice(product_names[category])} {random.choice(['Ultra', 'Pro Max', 'Elite', 'Black Edition', 'Gaming', 'Studio', 'Premium'])}-{random.randint(2024, 2026)}"

            writer.writerow(
                {
                    "sku": sku,
                    "product_name": product_name,
                    "category": category,
                    "supplier": supplier,
                    "stock_quantity": stock_quantity,
                    "sales_speed_per_day": round(sales_speed, 2),
                    "expiry_date": expiry_date,
                    "warehouse_location": warehouse_location,
                    "price_rub": price_rub,
                    "reorder_point": reorder_point
                }
            )

    print(f"Сгенерировано {NUM_ROWS} записей → {OUTPUT_FILE}")

```


if __name__ == "__main__":
    generate()
