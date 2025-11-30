import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from streamlit_autorefresh import st_autorefresh
from matplotlib.ticker import MaxNLocator

def custom_info(message, background_color="#fdf0b6", text_color="#000000", border_color="#ffd200"):
    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: {background_color};
            color: {text_color};
            border-left: 4px solid {border_color};
            margin-bottom: 1rem;
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

# Настройка страницы 
st.set_page_config(layout="wide")
st.title("Депо №1")

# Автообновление каждые секунду
#st_autorefresh(interval=1000, limit=None, key="dashboard_refresh")

# Параметры подключения к PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "depot_analysis"
DB_USER = "depot_user"
DB_PASS = "depotpassword"

# Загрузка данных
@st.cache_data(ttl=0)
def load_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )

        # Загрузка ВСЕХ данных о работниках и активностях
        workers_raw = pd.read_sql_query(
            """
            SELECT 
                w.id,
                u.color AS uniform_color,
                w.appearance_time
            FROM workers w
            LEFT JOIN uniforms u ON w.uniform_id = u.id
            """,
            conn,
            parse_dates=["appearance_time"]
        )

        activities_raw = pd.read_sql_query(
            """
            SELECT 
                wa.worker_id,
                a.name AS activity_name,
                wa.start_time
            FROM worker_activities wa
            JOIN activities a ON wa.activity_id = a.id
            """,
            conn,
            parse_dates=["appearance_time"]
        )

        # Преобразуем временные метки в datetime (на случай, если parse_dates не сработало)
        workers_raw['appearance_time'] = pd.to_datetime(workers_raw['appearance_time'])
        activities_raw['start_time'] = pd.to_datetime(activities_raw['start_time'])

        # Найти последнее время появления
        latest_time = max(
            workers_raw['appearance_time'].max(),
            activities_raw['start_time'].max()
        )

        # Отфильтровать только записи с этим временем
        workers_df = workers_raw[workers_raw['appearance_time'] == latest_time].copy()
        activities_df = activities_raw[activities_raw['start_time'] == latest_time].copy()

        # Форматирование времени для отображения (если нужно где-то показывать)
        workers_df['appearance_time'] = workers_df['appearance_time'].dt.strftime("%Y-%m-%d %H:%M:%S")
        activities_df['start_time'] = activities_df['start_time'].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Загрузка исторических данных о среднем времени активности
        mean_time_df = pd.read_sql_query(
            """
            SELECT last_updated, mean_seconds
            FROM mean_working_time
            ORDER BY last_updated
            """,
            conn,
            parse_dates=["last_updated"]
        )
        mean_time_df['last_updated'] = pd.to_datetime(mean_time_df['last_updated'])

        # Загрузка предупреждений
        alerts_df = pd.read_sql_query(
            """
            SELECT 
                alert_type,
                danger_message,
                alert_time
            FROM alerts
            WHERE alert_type = 'человек на путях' AND alert_time >= NOW() - INTERVAL '1 minutes'
            ORDER BY alert_time DESC
            """,
            conn,
            parse_dates=["alert_time"]
        )

        conn.close()
        return workers_df, activities_df, mean_time_df, alerts_df

    except Exception as e:
        st.error(f"Ошибка при загрузке базы данных: {e}")
        st.stop()

workers_df, activities_df, mean_time_df, alerts_df = load_data()

if not alerts_df.empty:
    latest_alert = alerts_df.iloc[0]
    alert_msg = 'На путях находится человек!'
    st.error(f"⚠️ {alert_msg}")

# Три колонки: занятость, униформа, график активности
col1, col2, col3 = st.columns([1, 1, 1])

# Колонка 1: Занятость (по активностям на latest_time)
with col1:
    st.subheader("Занятость сотрудников")
    if not activities_df.empty:
        total_workers = len(activities_df)
        activity_counts = activities_df['activity_name'].value_counts()
        labels = activity_counts.index.tolist()
        sizes = activity_counts.values.tolist()
        colors = ['#fcaf17', '#6b6b6b'] 

        fig, ax = plt.subplots(figsize=(4, 4))
        wedges, _ = ax.pie(
            sizes,
            labels=None,
            colors=colors[:len(sizes)],
            startangle=90,
            wedgeprops=dict(width=0.5)
        )
        ax.text(
            0, 0,
            str(total_workers),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=20,
            fontweight='bold',
            color='black'
        )
        ax.axis('equal')
        ax.legend(
            wedges, labels,
            title="Активность",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        plt.tight_layout()
        st.pyplot(fig)
    else:
        custom_info("Нет данных об активности сотрудников")

# Колонка 2: Униформа (по workers_df на latest_time)
with col2:
    st.subheader("Униформа")
    if not workers_df.empty:
        uniform_counts = workers_df['uniform_color'].value_counts().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(4, 4))
        colors = ['#c20937' if cat == "Нет униформы" else '#ffd200' for cat in uniform_counts.index]
        bars = ax.bar(uniform_counts.index, uniform_counts.values, width=0.6, color=colors)
        ax.set_xlabel("Цвет униформы")
        ax.set_ylabel("Количество сотрудников")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True)) # делаем шкалу количества целочисленной
        ax.set_xlim(-0.8, len(uniform_counts.index) - 0.2)
        ax.grid(True, alpha=0.5)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        custom_info("Нет данных о сотрудниках")

# Колонка 3: Среднее время активности
with col3:
    st.subheader("Среднее время активности сотрудников")
    if not mean_time_df.empty:
        mean_time_df = mean_time_df.sort_values('last_updated')
        mean_time_df['mean_minutes'] = mean_time_df['mean_seconds'] / 60.0

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(
            mean_time_df['last_updated'],
            mean_time_df['mean_minutes'],
            color='#f99d1c',
            marker='o',
            linewidth=2,
            markersize=4
        )
        ax.set_xlabel("Время")
        ax.set_ylabel("Среднее время активности (минуты)")
        ax.set_title("Среднее время активности сотрудников во времени")
        ax.grid(True, alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Нет данных о среднем времени активности.")