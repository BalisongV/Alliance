from datetime import datetime, timedelta
from database import get_session, create_tables, get_engine
import models
import crud
import queries

# Глобальные переменные для управления размером таблиц
MAX_RECORDS = 7  # Максимальное количество записей перед очисткой
DELETE_BATCH = 4   # Сколько записей удалять при превышении лимита

def check_and_cleanup_tables(db):
    """Проверяет размер таблиц и удаляет старые записи при необходимости"""
    try:
        # Проверяем количество записей в workers
        workers_count = db.query(models.Worker).count()
        worker_activities_count = db.query(models.WorkerActivity).count()
        
        print(f"Текущее количество записей: workers={workers_count}, worker_activities={worker_activities_count}")
        
        # Если превышен лимит, удаляем самые старые записи
        if workers_count >= MAX_RECORDS or worker_activities_count >= MAX_RECORDS:
            print(f"Превышен лимит {MAX_RECORDS} записей. Удаляем {DELETE_BATCH} самых старых записей...")
            
            # Удаляем из worker_activities (сначала из зависимой таблицы)
            old_activities = db.query(models.WorkerActivity).order_by(models.WorkerActivity.start_time).limit(DELETE_BATCH).all()
            for activity in old_activities:
                db.delete(activity)
            
            # Удаляем из workers
            old_workers = db.query(models.Worker).order_by(models.Worker.appearance_time).limit(DELETE_BATCH).all()
            for worker in old_workers:
                db.delete(worker)
            
            db.commit()
            print(f"Удалено {len(old_workers)} работников и {len(old_activities)} активностей")
            
    except Exception as e:
        db.rollback()
        print(f"Ошибка при очистке таблиц: {e}")

def initialize_sample_data():
    """Инициализация тестовых данных"""
    session = get_session()

    try:
        # Проверяем и очищаем таблицы перед добавлением новых данных
        check_and_cleanup_tables(session)

        # Создание видов униформы
        uniform_colors = ["униформа отсутствует", "синий", "серый", "белый"]
        uniforms = {}
        for color in uniform_colors:
            uniform = crud.UniformCRUD.create_uniform(session, color)
            uniforms[color] = uniform

        # Создание видов деятельности
        activities_data = [
            ("работает", "ремонтные работы"),
            ("не работает", "сотрудник не работает")
        ]
        activities = {}
        for name, description in activities_data:
            activity = crud.ActivityCRUD.create_activity(session, name, description)
            activities[name] = activity

        # Создание поездов
        train1 = crud.TrainCRUD.create_train(
            session,
            "ЭС1-001",
            datetime.now() - timedelta(hours=3),
            datetime.now() - timedelta(hours=1)
        )
        train2 = crud.TrainCRUD.create_train(
            session,
            "ЭС2-005",
            datetime.now() - timedelta(hours=2),
            datetime.now()
        )
        train3 = crud.TrainCRUD.create_train(
            session,
            "ЭС1-012",
            datetime.now() - timedelta(hours=5),
            None  # departure_time теперь NULL
            #datetime.now() - timedelta(hours=1),
        )

        # Создание работников - ДОБАВЛЕНО БОЛЬШЕ РАБОТНИКОВ
        worker1 = crud.WorkerCRUD.create_worker(
            session,
            train1.id,
            uniforms["синий"].id,
            True,
            datetime.now() - timedelta(hours=3, minutes=10),
            datetime.now() - timedelta(hours=1, minutes=5)
        )
        worker2 = crud.WorkerCRUD.create_worker(
            session,
            train1.id,
            uniforms["белый"].id,
            False,
            datetime.now() - timedelta(hours=2, minutes=45),
            datetime.now() - timedelta(hours=1, minutes=15)
        )
        worker3 = crud.WorkerCRUD.create_worker(
            session,
            train1.id,
            uniforms["серый"].id,
            True,
            datetime.now() - timedelta(hours=3, minutes=30),
            #datetime.now() - timedelta(hours=1, minutes=20)
            None
        )
        worker4 = crud.WorkerCRUD.create_worker(
            session,
            train2.id,
            uniforms["синий"].id,
            True,
            datetime.now() - timedelta(hours=2, minutes=15),
            datetime.now() - timedelta(minutes=30)
        )
        worker5 = crud.WorkerCRUD.create_worker(
            session,
            train2.id,
            uniforms["белый"].id,
            False,
            datetime.now() - timedelta(hours=1, minutes=45),
            datetime.now() - timedelta(minutes=15)
        )
        worker6 = crud.WorkerCRUD.create_worker(
            session,
            train2.id,
            uniforms["серый"].id,
            True,
            datetime.now() - timedelta(hours=2, minutes=30),
            datetime.now() - timedelta(minutes=45)
        )
        worker7 = crud.WorkerCRUD.create_worker(
            session,
            train3.id,
            uniforms["синий"].id,
            False,
            datetime.now() - timedelta(hours=5, minutes=20),
            datetime.now() - timedelta(hours=2, minutes=10)
        )
        worker8 = crud.WorkerCRUD.create_worker(
            session,
            train3.id,
            uniforms["белый"].id,
            True,
            datetime.now() - timedelta(hours=4, minutes=50),
            datetime.now() - timedelta(hours=2, minutes=30)
        )

        # Создание активностей работников - ДОБАВЛЕНО БОЛЬШЕ АКТИВНОСТЕЙ
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker1.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=3, minutes=5),
            datetime.now() - timedelta(hours=2, minutes=30)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker1.id,
            activities["не работает"].id,
            datetime.now() - timedelta(hours=2, minutes=25),
            datetime.now() - timedelta(hours=1, minutes=10)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker2.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=2, minutes=40),
            datetime.now() - timedelta(hours=1, minutes=30)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker3.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=3, minutes=25),
            datetime.now() - timedelta(hours=1, minutes=40)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker4.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=2, minutes=10),
            #datetime.now() - timedelta(minutes=40)
            None
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker5.id,
            activities["не работает"].id,
            datetime.now() - timedelta(hours=1, minutes=40),
            datetime.now() - timedelta(minutes=20)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker6.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=2, minutes=25),
            datetime.now() - timedelta(minutes=50)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker7.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=5, minutes=15),
            datetime.now() - timedelta(hours=3, minutes=30)
        )
        crud.WorkerActivityCRUD.create_worker_activity(
            session,
            worker8.id,
            activities["работает"].id,
            datetime.now() - timedelta(hours=4, minutes=45),
            datetime.now() - timedelta(hours=2, minutes=40)
        )
        
        # Создание тестовых происшествий
        crud.AlertCRUD.create_alert(
            session,
            worker2.id,  # работник без каски
            "падение на рельсы",
            "Сотрудник упал на рельсы при осмотре поезда",
            datetime.now() - timedelta(hours=2, minutes=30)
        )
        
        crud.AlertCRUD.create_alert(
            session,
            worker5.id,  # другой работник без каски
            "отсутствие защитной экипировки", 
            "Сотрудник работает без каски в опасной зоне",
            datetime.now() - timedelta(hours=1, minutes=10)
        )
        
        crud.AlertCRUD.create_alert(
            session,
            worker7.id,
            "нарушение техники безопасности",
            "Сотрудник пересек ограничительную линию без разрешения",
            datetime.now() - timedelta(hours=4, minutes=15)
        )

        session.commit()
        
        # Расчет и сохранение среднего времени работы
        crud.MeanWorkingTimeCRUD.calculate_and_update_all(session)
        
        print("Тестовые данные успешно созданы!")
        
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании тестовых данных: {e}")
    finally:
        session.close()


def display_all_tables():
    """Вывод содержимого всех таблиц"""
    session = get_session()
    
    try:
        print("\n" + "="*80)
        print("СОДЕРЖИМОЕ ВСЕХ ТАБЛИЦ БАЗЫ ДАННЫХ")
        print("="*80)
        
        # 1. Таблица uniforms
        print("\n--- ТАБЛИЦА: uniforms ---")
        uniforms = session.query(models.Uniform).all()
        if uniforms:
            print(f"{'ID':<5} {'Цвет':<15}")
            print("-" * 25)
            for uniform in uniforms:
                print(f"{uniform.id:<5} {uniform.color:<15}")
        else:
            print("Таблица пуста")
        
        # 2. Таблица activities
        print("\n--- ТАБЛИЦА: activities ---")
        activities = session.query(models.Activity).all()
        if activities:
            print(f"{'ID':<5} {'Название':<20} {'Описание':<30}")
            print("-" * 60)
            for activity in activities:
                desc = activity.description[:27] + "..." if activity.description and len(activity.description) > 30 else activity.description
                print(f"{activity.id:<5} {activity.name:<20} {desc or '':<30}")
        else:
            print("Таблица пуста")
        
        # 3. Таблица trains
        print("\n--- ТАБЛИЦА: trains ---")
        trains = session.query(models.Train).all()
        if trains:
            print(f"{'ID':<5} {'Номер поезда':<15} {'Прибытие':<20} {'Отправление':<20}")
            print("-" * 70)
            for train in trains:
                arrival = train.arrival_time.strftime("%Y-%m-%d %H:%M:%S")
                departure = train.departure_time.strftime("%Y-%m-%d %H:%M:%S") if train.departure_time else "NULL"
                print(f"{train.id:<5} {train.train_number:<15} {arrival:<20} {departure:<20}")
        else:
            print("Таблица пуста")
            
        # 4. Таблица workers
        print("\n--- ТАБЛИЦА: workers ---")
        workers = session.query(models.Worker).all()
        if workers:
            print(f"{'ID':<5} {'ID поезда':<10} {'ID униформы':<12} {'Каска':<8} {'Появление':<20} {'Исчезновение':<20}")
            print("-" * 90)
            for worker in workers:
                appearance = worker.appearance_time.strftime("%Y-%m-%d %H:%M:%S")
                disappearance = worker.disappearance_time.strftime("%Y-%m-%d %H:%M:%S") if worker.disappearance_time else "NULL"
                helmet = "Да" if worker.helmet_on else "Нет"
                print(f"{worker.id:<5} {worker.train_id:<10} {worker.uniform_id:<12} {helmet:<8} {appearance:<20} {disappearance:<20}")
        else:
            print("Таблица пуста")
            
        # 5. Таблица worker_activities
        print("\n--- ТАБЛИЦА: worker_activities ---")
        worker_activities = session.query(models.WorkerActivity).all()
        if worker_activities:
            print(f"{'ID':<5} {'ID работника':<13} {'ID активности':<14} {'Начало':<20} {'Конец':<20}")
            print("-" * 80)
            for wa in worker_activities:
                start = wa.start_time.strftime("%Y-%m-%d %H:%M:%S")
                end = wa.end_time.strftime("%Y-%m-%d %H:%M:%S") if wa.end_time else "NULL"
                print(f"{wa.id:<5} {wa.worker_id:<13} {wa.activity_id:<14} {start:<20} {end:<20}")
        else:
            print("Таблица пуста")

        # 6. Таблица mean_working_time
        print("\n--- ТАБЛИЦА: mean_working_time ---")
        mean_times = session.query(models.MeanWorkingTime).all()
        if mean_times:
            print(f"{'ID':<5} {'ID униформы':<12} {'Цвет':<15} {'Ср. время (сек)':<15} {'Работники':<10} {'Активности':<12} {'Обновлено':<20}")
            print("-" * 100)
            for mt in mean_times:
                updated = mt.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{mt.id:<5} {mt.uniform_id:<12} {mt.uniform_color:<15} {mt.mean_seconds:<15} {mt.worker_count:<10} {mt.activity_count:<12} {updated:<20}")
        else:
            print("Таблица пуста")

        # 7. Таблица alerts
        print("\n--- ТАБЛИЦА: alerts ---")
        alerts = session.query(models.Alert).all()
        if alerts:
            print(f"{'ID':<5} {'ID работника':<12} {'Тип':<20} {'Сообщение':<30} {'Время':<20}")
            print("-" * 90)
            for alert in alerts:
                alert_time = alert.alert_time.strftime("%Y-%m-%d %H:%M:%S")
                message = alert.danger_message[:27] + "..." if len(alert.danger_message) > 30 else alert.danger_message
                print(f"{alert.id:<5} {alert.worker_id:<12} {alert.alert_type:<20} {message:<30} {alert_time:<20}")
        else:
            print("Таблица пуста")
        
    except Exception as e:
        print(f"Ошибка при выводе таблиц: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Создание таблиц
    engine = get_engine()
    create_tables(engine)
    
    # Инициализация тестовых данных
    initialize_sample_data()
    
    # Вывод всех таблиц
    display_all_tables()