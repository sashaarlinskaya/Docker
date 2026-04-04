import os
import random
import datetime
import psycopg2
from psycopg2.extras import execute_values

DB_USER = os.getenv("DB_USER", "hruser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hrpassword")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "hr_db")

FIRST_NAMES = [
    "Александр", "Дмитрий", "Максим", "Сергей", "Андрей",
    "Алексей", "Артём", "Илья", "Кирилл", "Михаил",
    "Никита", "Павел", "Роман", "Тимур", "Евгений",
    "Анна", "Мария", "Наталья", "Екатерина", "Ольга",
    "Юлия", "Елена", "Татьяна", "Ирина", "Светлана",
    "Виктория", "Ксения", "Дарья", "Полина", "Алина",
]

LAST_NAMES = [
    "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев",
    "Петров", "Соколов", "Михайлов", "Новиков", "Фёдоров",
    "Морозов", "Волков", "Алексеев", "Лебедев", "Семёнов",
    "Егоров", "Павлов", "Козлов", "Степанов", "Николаев",
    "Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева",
    "Петрова", "Соколова", "Михайлова", "Новикова", "Фёдорова",
]

PATRONYMICS = [
    "Александрович", "Дмитриевич", "Михайлович", "Сергеевич", "Андреевич",
    "Алексеевич", "Артёмович", "Ильич", "Кириллович", "Павлович",
    "Александровна", "Дмитриевна", "Михайловна", "Сергеевна", "Андреевна",
    "Алексеевна", "Артёмовна", "Ильинична", "Кирилловна", "Павловна",
]

DEPARTMENTS = [
    "Разработка", "Тестирование", "DevOps", "Аналитика",
    "Маркетинг", "Продажи", "HR", "Финансы",
    "Юридический", "Безопасность", "Поддержка", "Управление",
]

POSITIONS_BY_DEPT = {
    "Разработка": ["Junior Developer", "Middle Developer", "Senior Developer", "Lead Developer", "Principal Engineer"],
    "Тестирование": ["QA Engineer", "Senior QA", "QA Lead", "Test Architect"],
    "DevOps": ["DevOps Engineer", "Site Reliability Engineer", "Cloud Architect", "Infrastructure Lead"],
    "Аналитика": ["Data Analyst", "Business Analyst", "Data Scientist", "Analytics Lead"],
    "Маркетинг": ["Marketing Specialist", "Content Manager", "SEO Specialist", "Marketing Lead"],
    "Продажи": ["Sales Manager", "Account Executive", "Sales Representative", "Sales Director"],
    "HR": ["HR Specialist", "HR Manager", "Recruiter", "HR Business Partner"],
    "Финансы": ["Financial Analyst", "Accountant", "Financial Manager", "CFO"],
    "Юридический": ["Legal Counsel", "Senior Legal Counsel", "Legal Manager"],
    "Безопасность": ["Security Engineer", "Security Analyst", "CISO"],
    "Поддержка": ["Support Specialist", "Support Lead", "Technical Support Engineer"],
    "Управление": ["Project Manager", "Product Manager", "Director", "VP"],
}

SALARY_RANGES = {
    "Junior Developer": (60000, 90000),
    "Middle Developer": (100000, 150000),
    "Senior Developer": (160000, 220000),
    "Lead Developer": (220000, 300000),
    "Principal Engineer": (280000, 380000),
    "QA Engineer": (60000, 100000),
    "Senior QA": (100000, 140000),
    "QA Lead": (140000, 200000),
    "Test Architect": (180000, 260000),
    "DevOps Engineer": (120000, 180000),
    "Site Reliability Engineer": (160000, 240000),
    "Cloud Architect": (200000, 300000),
    "Infrastructure Lead": (220000, 320000),
    "Data Analyst": (80000, 140000),
    "Business Analyst": (90000, 150000),
    "Data Scientist": (150000, 250000),
    "Analytics Lead": (200000, 280000),
    "Marketing Specialist": (60000, 100000),
    "Content Manager": (55000, 90000),
    "SEO Specialist": (65000, 110000),
    "Marketing Lead": (130000, 200000),
    "Sales Manager": (80000, 160000),
    "Account Executive": (90000, 170000),
    "Sales Representative": (60000, 100000),
    "Sales Director": (200000, 350000),
    "HR Specialist": (60000, 90000),
    "HR Manager": (100000, 160000),
    "Recruiter": (65000, 110000),
    "HR Business Partner": (130000, 200000),
    "Financial Analyst": (90000, 140000),
    "Accountant": (70000, 110000),
    "Financial Manager": (150000, 250000),
    "CFO": (350000, 600000),
    "Legal Counsel": (110000, 180000),
    "Senior Legal Counsel": (160000, 250000),
    "Legal Manager": (200000, 320000),
    "Security Engineer": (130000, 200000),
    "Security Analyst": (100000, 160000),
    "CISO": (300000, 500000),
    "Support Specialist": (50000, 80000),
    "Support Lead": (90000, 140000),
    "Technical Support Engineer": (70000, 110000),
    "Project Manager": (130000, 200000),
    "Product Manager": (150000, 250000),
    "Director": (280000, 450000),
    "VP": (400000, 700000),
}


def generate_full_name():
    last = random.choice(LAST_NAMES)
    first = random.choice(FIRST_NAMES)
    patronymic = random.choice(PATRONYMICS)
    return f"{last} {first} {patronymic}"


def generate_hire_date():
    start = datetime.date(2010, 1, 1)
    end = datetime.date(2025, 12, 31)
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))


def seed():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM employees")
    count = cur.fetchone()[0]
    if count >= 10000:
        print(f"Already have {count} employees, skipping seed.")
        cur.close()
        conn.close()
        return

    print("Seeding 10000 employees...")
    records = []
    for _ in range(10000):
        dept = random.choice(DEPARTMENTS)
        position = random.choice(POSITIONS_BY_DEPT[dept])
        salary_range = SALARY_RANGES.get(position, (60000, 150000))
        salary = round(random.uniform(*salary_range), 2)
        records.append((
            generate_full_name(),
            position,
            dept,
            salary,
            generate_hire_date(),
        ))

    execute_values(
        cur,
        "INSERT INTO employees (full_name, position, department, salary, hire_date) VALUES %s",
        records,
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    seed()
