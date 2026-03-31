#!/usr/bin/env python3
import pymysql
import os
import sys
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('ru_RU')

def get_db_connection():
    """Подключение к MySQL"""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'mysql-service'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root123'),
        database=os.getenv('DB_NAME', 'internet_shop'),
        charset='utf8mb4'
    )

def init_database():
    """Инициализация базы данных: создание таблиц и наполнение тестовыми данными"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("📦 Создание таблиц...")
        
        # Таблица товаров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                price DECIMAL(10,2),
                stock_quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица клиентов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200),
                email VARCHAR(200),
                city VARCHAR(100),
                registered_at DATE
            )
        """)
        
        # Таблица заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10,2),
                status VARCHAR(50) DEFAULT 'completed',
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Таблица позиций заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                product_id INT,
                quantity INT,
                price_per_unit DECIMAL(10,2),
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        print("📊 Заполнение тестовыми данными...")
        
        # Очистка существующих данных (опционально)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE order_items")
        cursor.execute("TRUNCATE TABLE orders")
        cursor.execute("TRUNCATE TABLE customers")
        cursor.execute("TRUNCATE TABLE products")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Добавление товаров
        products = [
            ("Ноутбук Lenovo IdeaPad", "Электроника", 45000.00, 25),
            ("Смартфон Xiaomi Note", "Электроника", 25000.00, 50),
            ("Наушники Sony WH-1000", "Аксессуары", 15000.00, 30),
            ("Клавиатура Logitech MX", "Аксессуары", 12000.00, 20),
            ("Монитор Samsung 24\"", "Электроника", 18000.00, 15),
            ("Мышь Logitech Master", "Аксессуары", 8000.00, 40),
            ("Внешний SSD 1TB", "Хранение", 10000.00, 12),
            ("Кофеварка De'Longhi", "Бытовая техника", 35000.00, 8),
        ]
        
        for product in products:
            cursor.execute(
                "INSERT INTO products (name, category, price, stock_quantity) VALUES (%s, %s, %s, %s)",
                product
            )
        
        # Добавление клиентов
        customers = []
        for _ in range(20):
            customer = (
                fake.name(),
                fake.email(),
                fake.city(),
                fake.date_between(start_date='-1y', end_date='today')
            )
            customers.append(customer)
            cursor.execute(
                "INSERT INTO customers (name, email, city, registered_at) VALUES (%s, %s, %s, %s)",
                customer
            )
        
        # Получаем ID товаров и клиентов
        cursor.execute("SELECT id, price FROM products")
        products_data = cursor.fetchall()
        
        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        # Генерация заказов
        for _ in range(100):
            customer_id = random.choice(customer_ids)
            order_date = fake.date_time_between(start_date='-6m', end_date='now')
            order_items_count = random.randint(1, 5)
            
            cursor.execute(
                "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (%s, %s, %s, %s)",
                (customer_id, order_date, 0, random.choice(['completed', 'pending', 'shipped']))
            )
            order_id = cursor.lastrowid
            
            total = 0
            for _ in range(order_items_count):
                product_id, price = random.choice(products_data)
                quantity = random.randint(1, 3)
                total += price * quantity
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price_per_unit) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, price)
                )
            
            # Обновляем сумму заказа
            cursor.execute("UPDATE orders SET total_amount = %s WHERE id = %s", (total, order_id))
        
        conn.commit()
        conn.close()
        
        print("✅ База данных успешно инициализирована!")
        print("   Таблицы: products, customers, orders, order_items")
        print("   Записей: товаров - 8, клиентов - 20, заказов - 100")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Запуск инициализации базы данных интернет-магазина")
    init_database()
