from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
# Базовый класс для моделей
Base = declarative_base()

# Настройка подключения к PostgreSQL
DATABASE_URL = "postgresql://depot_user:depotpassword@localhost:5432/depot_analysis"

def get_engine(database_url: str = None):
    """Создание движка БД"""
    url = database_url or DATABASE_URL
    return create_engine(
        url,
        pool_pre_ping=True,
        echo=False,  # Установите True для отладки SQL запросов
        future=True
    )

def get_session(engine=None):
    """Создание сессии БД"""
    if engine is None:
        engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def create_tables(engine=None):
    if engine is None:
        engine = get_engine()
    
    Base.metadata.create_all(bind=engine)
    
    # Создаем нулевой поезд если его нет
    session = get_session(engine)
    try:
        from models import Train
        zero_train = session.query(Train).filter(Train.id == 0).first()
        if not zero_train:
            session.execute(text(
                "INSERT INTO trains (id, train_number, arrival_time, departure_time) VALUES (0, '000-000', '0001-01-01 00:00:00', '0001-01-01 00:00:00')"
            ))
            session.commit()
            print("Создан нулевой поезд: ID=0, Номер=000-000")
    except Exception as e:
        print(f"Ошибка при создании нулевого поезда: {e}")
    finally:
        session.close()


def drop_tables(engine=None):
    """Удаление всех таблиц из базы данных"""
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    print("Все таблицы удалены из базы данных")

def clear_all_data(engine=None):
    """Очистка всех данных из таблиц (без удаления самих таблиц)"""
    if engine is None:
        engine = get_engine()
    
    session = get_session(engine)
    try:
        # Очистка в правильном порядке из-за foreign key constraints
        session.execute(text("DELETE FROM worker_activities"))
        session.execute(text("DELETE FROM frame_statistics"))
        session.execute(text("DELETE FROM workers"))
        session.execute(text("DELETE FROM trains"))
        session.execute(text("DELETE FROM activities"))
        session.execute(text("DELETE FROM uniforms"))
        
        # Сброс последовательностей для auto-increment полей
        session.execute(text("ALTER SEQUENCE worker_activities_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE frame_statistics_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE workers_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE trains_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE activities_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE uniforms_id_seq RESTART WITH 1"))
        
        session.commit()
        print("Все данные очищены из таблиц, последовательности сброшены")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при очистке данных: {e}")
    finally:
        session.close()