# Лабораторная работа 2.1. Создание Dockerfile и сборка образа

## Титульный лист

**Дисциплина:** Интеграция и развертывание программного обеспечения с помощью контейнеров
**Тема:** Создание Dockerfile и сборка образа

**Вариант:** 3  

**Выполнила:** Арлинская Александра Викторовна  
**Проверил:** Босенко Тимур Муртазович  
**Курс обучения:** 4  
**Форма обучения:** очная  

**Институт цифрового образования**  
**Департамент информатики, управления и технологий**  
**Московский городской педагогический университет**  
**Москва 2026**

---

## Цель работы

Научиться разрабатывать воспроизводимые аналитические инструменты. Студенту необходимо пройти полный цикл: от написания Node.js-скрипта для обработки бизнес-данных до его упаковки в Docker-образ и запуска в изолированной среде.

---

## Необходимые инструменты и технологии

Для выполнения работы потребуются:

**Платформа.** Виртуальная машина из образа ETL_devops.ova (Ubuntu-based).

**Инструменты:** Docker Compose.

**Репозиторий:** GitHub.

---

## Задачи

1. **Аналитическая часть.** Написать приложение, которое генерирует набор данных (складские остатки товаров для российского рынка) и производит их анализ (расчет метрик, фильтрация, статистика).

2. **Техническая часть.** Создать оптимальный Dockerfile для этого приложения.

3. **Сборка и запуск.** Собрать образ, запустить контейнер и продемонстрировать вывод результатов (через API).

4. **Отчет.** Загрузить код и отчет в репозиторий.

---
## Задание

Разработать Node.js API сервис на Express.js, который генерирует массив JSON-объектов (складские остатки товаров) и имеет эндпоинт `/filter?min=X`, возвращающий записи, где значение метрики (остаток, скорость продаж, срок годности) больше X.

## Источник данных

Данные генерируются синтетически с помощью разработанного файла-генератора generate.js . В основе лежат данные о товарных категориях, характерных для российского рынка:

- Молочные продукты
- Хлебобулочные изделия
- Бакалея
- Крупы
- Мясо и мясная продукция
- Рыба
- Овощи и фрукты
- Напитки
- Яйца
- Масла
- Макаронные изделия

---

## Описание данных

Генератор создает CSV-файл со следующими полями:

- **SKU** — артикул товара (SKU-00001)
- **Наименование** — наименование товара (Молоко 3.2%)
- **Категория** — категория товара (Молочные продукты)
- **Единица** — единица измерения (л)
- **Остаток** — остаток на складе в единицах (156)
- **Скорость_продаж_день** — скорость продаж в единицах в день (23.5)
- **Срок_годности_дней** — срок годности в днях (14)
- **Дней_до_обнуления** — дней до обнуления запаса (6.6)
- **Поставщик** — наименование поставщика (ООО Ромашка)
|

<img width="870" height="483" alt="image" src="https://github.com/user-attachments/assets/a12e67d7-98b7-408b-9855-d465366e3192" />

---

## Структура проекта

<img width="304" height="279" alt="image" src="https://github.com/user-attachments/assets/e6783ee6-3521-4f57-9d5a-7e7b0eb1435d" />



---

## Шаг 1. Разработка генератора данных (app/generate.js)

Создан модуль для генерации тестовых данных о складских остатках.

```javascript
const fs = require('fs');
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

const SUPPLIERS = [
  'ООО Ромашка', 'ИП Иванов', 'ЗАО МегаПоставка', 'ООО ТоргСнаб',
  'ПАО Логистика', 'ООО АгроПром', 'ИП Петров', 'ООО СнабЦентр',
  'ЗАО ТехноСнаб', 'ООО РусИмпорт'
];

const PRODUCTS = [
  { name: 'Молоко 3.2%', category: 'Молочные продукты', unit: 'л' },
  { name: 'Хлеб белый', category: 'Хлебобулочные изделия', unit: 'шт' },
  { name: 'Сахар-песок', category: 'Бакалея', unit: 'кг' },
  { name: 'Гречка ядрица', category: 'Крупы', unit: 'кг' },
  { name: 'Масло сливочное 82%', category: 'Молочные продукты', unit: 'кг' },
  { name: 'Яйцо куриное С1', category: 'Яйца', unit: 'дес' },
  { name: 'Мука пшеничная в/с', category: 'Бакалея', unit: 'кг' },
  { name: 'Подсолнечное масло', category: 'Масла', unit: 'л' },
  { name: 'Макароны спагетти', category: 'Макаронные изделия', unit: 'кг' },
  { name: 'Рис длиннозёрный', category: 'Крупы', unit: 'кг' },
  { name: 'Соль поваренная', category: 'Бакалея', unit: 'кг' },
  { name: 'Чай чёрный байховый', category: 'Напитки', unit: 'упак' },
  { name: 'Кофе растворимый', category: 'Напитки', unit: 'упак' },
  { name: 'Сметана 20%', category: 'Молочные продукты', unit: 'кг' },
  { name: 'Творог 9%', category: 'Молочные продукты', unit: 'кг' },
  { name: 'Колбаса докторская', category: 'Колбасные изделия', unit: 'кг' },
  { name: 'Сосиски молочные', category: 'Колбасные изделия', unit: 'кг' },
  { name: 'Курица бройлер', category: 'Мясо птицы', unit: 'кг' },
  { name: 'Фарш говяжий', category: 'Мясо', unit: 'кг' },
  { name: 'Минтай б/г', category: 'Рыба', unit: 'кг' }
];

function rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randFloat(min, max, decimals = 1) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}

function generateExpiryDays(category) {
  const expiryMap = {
    'Молочные продукты': () => rand(3, 30),
    'Хлебобулочные изделия': () => rand(1, 7),
    'Колбасные изделия': () => rand(7, 45),
    'Мясо птицы': () => rand(3, 10),
    'Мясо': () => rand(3, 14),
    'Рыба': () => rand(5, 20),
    'Овощи': () => rand(5, 30),
    'Фрукты': () => rand(7, 21),
    'Крупы': () => rand(180, 730),
    'Бакалея': () => rand(180, 1095),
    'Макаронные изделия': () => rand(365, 730),
    'Масла': () => rand(180, 730),
    'Напитки': () => rand(180, 1095),
    'Яйца': () => rand(14, 25)
  };
  return (expiryMap[category] || (() => rand(30, 365)))();
}

async function generateAndSaveCSV(csvPath, count) {
  const dir = path.dirname(csvPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const items = [];
  
  for (let i = 0; i < count; i++) {
    const product = PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)];
    const stockQty = rand(10, 2000);
    const salesSpeed = randFloat(1, 80);
    const expiryDays = generateExpiryDays(product.category);
    const daysUntilStockout = parseFloat((stockQty / salesSpeed).toFixed(1));

    items.push({
      sku: `SKU-${String(i + 1).padStart(5, '0')}`,
      name: product.name,
      category: product.category,
      unit: product.unit,
      stock_qty: stockQty,
      sales_speed: salesSpeed,
      expiry_days: expiryDays,
      days_until_stockout: daysUntilStockout,
      supplier: SUPPLIERS[Math.floor(Math.random() * SUPPLIERS.length)]
    });
  }

  const csvWriter = createObjectCsvWriter({
    path: csvPath,
    header: [
      { id: 'sku', title: 'SKU' },
      { id: 'name', title: 'Наименование' },
      { id: 'category', title: 'Категория' },
      { id: 'unit', title: 'Единица' },
      { id: 'stock_qty', title: 'Остаток' },
      { id: 'sales_speed', title: 'Скорость_продаж_день' },
      { id: 'expiry_days', title: 'Срок_годности_дней' },
      { id: 'days_until_stockout', title: 'Дней_до_обнуления' },
      { id: 'supplier', title: 'Поставщик' }
    ],
    fieldDelimiter: ';',
    encoding: 'utf8'
  });

  await csvWriter.writeRecords(items);
  console.log(`CSV сгенерирован: ${csvPath} (${items.length} записей)`);
  return items;
}

module.exports = { generateAndSaveCSV };

```
<img width="875" height="636" alt="image" src="https://github.com/user-attachments/assets/0eee8403-4494-4cf4-a4c5-dde2fd6f09d6" />

## Шаг 2. Разработка сервиса (app/index.js)

Создан Express-сервер с эндпоинтами для работы с данными.

```javascript
require('dotenv').config();
const express = require('express');
const fs = require('fs');
const csv = require('csv-parser');
const { generateAndSaveCSV } = require('./generate');

const app = express();
const PORT = process.env.PORT || 3000;
const CSV_PATH = process.env.CSV_PATH || './data/inventory.csv';
const ITEMS_COUNT = parseInt(process.env.ITEMS_COUNT || '50', 10);

let inventoryCache = [];

async function loadCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv({ separator: ';' }))
      .on('data', (row) => {
        rows.push({
          sku: row['SKU'],
          name: row['Наименование'],
          category: row['Категория'],
          unit: row['Единица'],
          stock_qty: parseFloat(row['Остаток']),
          sales_speed: parseFloat(row['Скорость_продаж_день']),
          expiry_days: parseInt(row['Срок_годности_дней'], 10),
          days_until_stockout: parseFloat(row['Дней_до_обнуления']),
          supplier: row['Поставщик']
        });
      })
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}

async function init() {
  const csvExists = fs.existsSync(CSV_PATH);

  if (!csvExists) {
    console.log('CSV не найден, генерируем данные...');
    inventoryCache = await generateAndSaveCSV(CSV_PATH, ITEMS_COUNT);
  } else {
    console.log('CSV найден, загружаем данные...');
    inventoryCache = await loadCSV(CSV_PATH);
    console.log(`Загружено записей: ${inventoryCache.length}`);
  }
}

app.get('/inventory', (req, res) => {
  res.json({
    total: inventoryCache.length,
    items: inventoryCache
  });
});

app.get('/filter', (req, res) => {
  const min = parseFloat(req.query.min);
  const metric = req.query.metric || 'stock_qty';

  const allowedMetrics = ['stock_qty', 'sales_speed', 'expiry_days', 'days_until_stockout'];

  if (isNaN(min)) {
    return res.status(400).json({
      error: 'Параметр min обязателен и должен быть числом',
      example: '/filter?min=100'
    });
  }

  if (!allowedMetrics.includes(metric)) {
    return res.status(400).json({
      error: `Недопустимая метрика. Доступные: ${allowedMetrics.join(', ')}`
    });
  }

  const filtered = inventoryCache.filter((item) => item[metric] > min);

  res.json({
    metric,
    min,
    total: filtered.length,
    items: filtered
  });
});

app.get('/stats', (req, res) => {
  if (inventoryCache.length === 0) {
    return res.json({ message: 'Данных нет' });
  }

  const totalStock = inventoryCache.reduce((s, i) => s + i.stock_qty, 0);
  const avgSalesSpeed = inventoryCache.reduce((s, i) => s + i.sales_speed, 0) / inventoryCache.length;
  const avgExpiry = inventoryCache.reduce((s, i) => s + i.expiry_days, 0) / inventoryCache.length;
  const criticalItems = inventoryCache.filter((i) => i.days_until_stockout < 7).length;

  const byCategory = inventoryCache.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {});

  const bySupplier = inventoryCache.reduce((acc, item) => {
    acc[item.supplier] = (acc[item.supplier] || 0) + 1;
    return acc;
  }, {});

  res.json({
    total_items: inventoryCache.length,
    total_stock_units: totalStock,
    avg_sales_speed_per_day: parseFloat(avgSalesSpeed.toFixed(2)),
    avg_expiry_days: parseFloat(avgExpiry.toFixed(1)),
    critical_stockout_items: criticalItems,
    by_category: byCategory,
    by_supplier: bySupplier
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', items_loaded: inventoryCache.length });
});

init()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Сервер запущен на порту ${PORT}`);
      console.log(`GET /inventory          — все товары`);
      console.log(`GET /filter?min=X       — фильтр по остатку > X`);
      console.log(`GET /filter?min=X&metric=sales_speed — фильтр по любой метрике`);
      console.log(`GET /stats              — агрегированная статистика`);
      console.log(`GET /health             — healthcheck`);
    });
  })
  .catch((err) => {
    console.error('Ошибка инициализации:', err);
    process.exit(1);
  });

  ```
  <img width="770" height="609" alt="image" src="https://github.com/user-attachments/assets/0e540d2f-dff1-4a04-80c1-cabf93dd7a32" />

 ## Шаг 3. Создание файла .env

Файл .env:

```env
PORT=3000
CSV_PATH=./data/inventory.csv
ITEMS_COUNT=2000
```
<img width="553" height="169" alt="image" src="https://github.com/user-attachments/assets/d4f14d1d-cb97-4289-9d1c-f541dd55bd93" />

## Шаг 4. Создание Dockerfile

Файл Dockerfile:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Копируем зависимости отдельно для кэширования слоев
COPY package*.json ./

# Устанавливаем только production зависимости
RUN npm ci --only=production

# Копируем код
COPY . .

# Создаем директорию для данных
RUN mkdir -p data

# Создаем непривилегированного пользователя для безопасности
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

# Переключаемся на непривилегированного пользователя
USER nodejs

EXPOSE 3000

CMD ["node", "app/index.js"]
```
## Шаг 5. Создание docker-compose.yml

Файл docker-compose.yml:

```yaml
services:
  api:
    build: .
    container_name: inventory-api
    ports:
      - "${PORT:-3000}:3000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

## Шаг 6. Создание .dockerignore

Файл .dockerignore:

```dockerignore
node_modules
npm-debug.log
.env
.git
.gitignore
README.md
data/*.csv
!data/.gitkeep
*.log
```

## Шаг 7. Запуск контейнера

Для запуска контейнера используем Docker Compose. Эта команда собирает образ (если он еще не собран) и запускает контейнер в фоновом режиме.

```bash
docker compose up --build
```
<img width="700" height="452" alt="image" src="https://github.com/user-attachments/assets/f69532ef-42d8-4b8c-8027-049a02d0bc67" />

<img width="672" height="249" alt="image" src="https://github.com/user-attachments/assets/62837ea0-f8f3-445a-bb79-93e9d4843e07" />

## Шаг 8. Тестирование API через curl

После запуска контейнера необходимо проверить работоспособность всех эндпоинтов с помощью утилиты curl.

### 8.1. Получение всех товаров
```
curl http://localhost:3000/inventory
```
<img width="681" height="735" alt="image" src="https://github.com/user-attachments/assets/a67f2b50-75cc-48ca-b66a-5b481d820064" />

### 8.2. Фильтрация по остатку > 500

```
curl "http://localhost:3000/filter?min=500"
```
<img width="889" height="782" alt="image" src="https://github.com/user-attachments/assets/25573af6-b4f6-4cf8-a2cd-362a1423467b" />

## Вывод

В ходе лабораторной работы разработан Node.js API сервис на Express.js, который генерирует массив JSON-объектов (складские остатки товаров) и реализует эндпоинт `/filter?min=X` для фильтрации записей по различным метрикам. Приложение упаковано в Docker-контейнер с использованием оптимального Dockerfile, запущено через Docker Compose, работоспособность подтверждена curl-запросами.

---

## Ссылка на архив проекта

Проект доступен для скачивания по ссылке:

[https://github.com/sashaarlinskaya/Docker/blob/main/lab_02.zip](https://github.com/sashaarlinskaya/Docker/blob/main/lab_02.zip)
