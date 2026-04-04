import streamlit as st
import requests
import pandas as pd
import os
import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="HR Portal", page_icon="👥", layout="wide")
st.title("👥 HR Portal — База сотрудников")


def get_departments():
    try:
        res = requests.get(f"{BACKEND_URL}/departments", timeout=5)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []


def get_employees(skip=0, limit=50, department=None, search=None):
    try:
        params = {"skip": skip, "limit": limit}
        if department:
            params["department"] = department
        if search:
            params["search"] = search
        res = requests.get(f"{BACKEND_URL}/employees", params=params, timeout=5)
        return res.json() if res.status_code == 200 else {"total": 0, "items": []}
    except Exception as e:
        st.error(f"Ошибка подключения к бэкенду: {e}")
        return {"total": 0, "items": []}


tab_list, tab_add, tab_edit, tab_stats = st.tabs(
    ["📋 Список сотрудников", "➕ Добавить", "✏️ Редактировать / Удалить", "📊 Статистика"]
)

with tab_list:
    st.subheader("Список сотрудников")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_query = st.text_input("🔍 Поиск по ФИО", "")
    with col2:
        departments = ["Все"] + get_departments()
        selected_dept = st.selectbox("Отдел", departments)
    with col3:
        page_size = st.selectbox("Записей на странице", [25, 50, 100], index=1)

    dept_filter = None if selected_dept == "Все" else selected_dept

    if "list_page" not in st.session_state:
        st.session_state.list_page = 0

    data = get_employees(
        skip=st.session_state.list_page * page_size,
        limit=page_size,
        department=dept_filter,
        search=search_query if search_query else None,
    )

    total = data.get("total", 0)
    items = data.get("items", [])

    st.caption(f"Найдено сотрудников: **{total}**")

    if items:
        df = pd.DataFrame(items)
        df = df.rename(columns={
            "id": "ID",
            "full_name": "ФИО",
            "position": "Должность",
            "department": "Отдел",
            "salary": "Зарплата (₽)",
            "hire_date": "Дата найма",
        })
        df["Зарплата (₽)"] = df["Зарплата (₽)"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
        st.dataframe(df[["ID", "ФИО", "Должность", "Отдел", "Зарплата (₽)", "Дата найма"]], use_container_width=True)

        total_pages = (total - 1) // page_size
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("← Назад") and st.session_state.list_page > 0:
                st.session_state.list_page -= 1
                st.rerun()
        with col_info:
            st.write(f"Страница {st.session_state.list_page + 1} из {total_pages + 1}")
        with col_next:
            if st.button("Вперёд →") and st.session_state.list_page < total_pages:
                st.session_state.list_page += 1
                st.rerun()
    else:
        st.info("Нет данных")


with tab_add:
    st.subheader("Добавить нового сотрудника")

    with st.form("add_form", clear_on_submit=True):
        full_name = st.text_input("ФИО *")
        position = st.text_input("Должность *")
        department = st.text_input("Отдел *")
        salary = st.number_input("Зарплата (₽)", min_value=0.0, step=1000.0, value=80000.0)
        hire_date = st.date_input("Дата найма", value=datetime.date.today())
        submitted = st.form_submit_button("Добавить")

        if submitted:
            if not full_name or not position or not department:
                st.warning("Заполните все обязательные поля (*).")
            else:
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/employees",
                        json={
                            "full_name": full_name,
                            "position": position,
                            "department": department,
                            "salary": salary,
                            "hire_date": hire_date.isoformat(),
                        },
                        timeout=5,
                    )
                    if res.status_code == 200:
                        st.success("✅ Сотрудник добавлен!")
                    else:
                        st.error(f"Ошибка: {res.text}")
                except Exception as e:
                    st.error(f"Ошибка подключения: {e}")


with tab_edit:
    st.subheader("Редактировать или удалить сотрудника")

    emp_id_input = st.number_input("ID сотрудника", min_value=1, step=1, value=1)

    col_load, col_delete = st.columns([2, 1])

    with col_load:
        if st.button("Загрузить данные"):
            try:
                res = requests.get(f"{BACKEND_URL}/employees/{int(emp_id_input)}", timeout=5)
                if res.status_code == 200:
                    st.session_state.edit_data = res.json()
                else:
                    st.error("Сотрудник не найден.")
                    st.session_state.pop("edit_data", None)
            except Exception as e:
                st.error(f"Ошибка: {e}")

    with col_delete:
        if st.button("🗑️ Удалить", type="secondary"):
            try:
                res = requests.delete(f"{BACKEND_URL}/employees/{int(emp_id_input)}", timeout=5)
                if res.status_code == 200:
                    st.success("Сотрудник удалён.")
                    st.session_state.pop("edit_data", None)
                else:
                    st.error("Не удалось удалить.")
            except Exception as e:
                st.error(f"Ошибка: {e}")

    if "edit_data" in st.session_state:
        ed = st.session_state.edit_data
        with st.form("edit_form"):
            new_name = st.text_input("ФИО", value=ed.get("full_name", ""))
            new_position = st.text_input("Должность", value=ed.get("position", ""))
            new_department = st.text_input("Отдел", value=ed.get("department", ""))
            new_salary = st.number_input("Зарплата (₽)", value=float(ed.get("salary", 0)), step=1000.0)
            new_hire_date = st.date_input(
                "Дата найма",
                value=datetime.date.fromisoformat(ed["hire_date"]) if ed.get("hire_date") else datetime.date.today(),
            )
            save = st.form_submit_button("💾 Сохранить изменения")

            if save:
                try:
                    res = requests.put(
                        f"{BACKEND_URL}/employees/{ed['id']}",
                        json={
                            "full_name": new_name,
                            "position": new_position,
                            "department": new_department,
                            "salary": new_salary,
                            "hire_date": new_hire_date.isoformat(),
                        },
                        timeout=5,
                    )
                    if res.status_code == 200:
                        st.success("✅ Данные обновлены!")
                        st.session_state.edit_data = res.json()
                    else:
                        st.error(f"Ошибка: {res.text}")
                except Exception as e:
                    st.error(f"Ошибка: {e}")


with tab_stats:
    st.subheader("Статистика по сотрудникам")

    if st.button("Загрузить статистику"):
        try:
            r1 = requests.get(f"{BACKEND_URL}/stats/by-department", timeout=5)
            r2 = requests.get(f"{BACKEND_URL}/stats/salary-distribution", timeout=5)

            if r1.status_code == 200:
                dept_data = r1.json()
                df_dept = pd.DataFrame(dept_data)
                df_dept.columns = ["Отдел", "Кол-во сотрудников", "Средняя зарплата (₽)"]
                df_dept = df_dept.sort_values("Кол-во сотрудников", ascending=False)

                st.markdown("### Сотрудники по отделам")
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df_dept, use_container_width=True)
                with col2:
                    st.bar_chart(df_dept.set_index("Отдел")["Кол-во сотрудников"])

            if r2.status_code == 200:
                sal_data = r2.json()
                df_sal = pd.DataFrame(sal_data)
                df_sal.columns = ["Должность", "Средняя зарплата (₽)"]

                st.markdown("### Средняя зарплата по должностям (топ-15)")
                st.bar_chart(df_sal.set_index("Должность"))

        except Exception as e:
            st.error(f"Ошибка: {e}")
