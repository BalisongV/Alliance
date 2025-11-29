from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
import models

# CRUD операции для Train
class TrainCRUD:
    @staticmethod
    def create_train(db: Session, train_number: str, arrival_time: datetime, departure_time: datetime):
        db_train = models.Train(
            train_number=train_number,
            arrival_time=arrival_time,
            departure_time=departure_time
        )
        db.add(db_train)
        db.commit()
        db.refresh(db_train)
        return db_train

    @staticmethod
    def get_train(db: Session, train_id: int):
        return db.query(models.Train).filter(models.Train.id == train_id).first()

    @staticmethod
    def get_trains_by_number(db: Session, train_number: str):
        return db.query(models.Train).filter(models.Train.train_number == train_number).all()

    @staticmethod
    def get_trains_in_time_range(db: Session, start_time: datetime, end_time: datetime):
        return db.query(models.Train).filter(
            and_(
                models.Train.arrival_time <= end_time,
                models.Train.departure_time >= start_time
            )
        ).all()


# CRUD операции для Uniform
class UniformCRUD:
    @staticmethod
    def create_uniform(db: Session, color: str):
        db_uniform = models.Uniform(color=color)
        db.add(db_uniform)
        db.commit()
        db.refresh(db_uniform)
        return db_uniform

    @staticmethod
    def get_uniform(db: Session, uniform_id: int):
        return db.query(models.Uniform).filter(models.Uniform.id == uniform_id).first()

    @staticmethod
    def get_uniform_by_color(db: Session, color: str):
        return db.query(models.Uniform).filter(models.Uniform.color == color).first()


# CRUD операции для Activity
class ActivityCRUD:
    @staticmethod
    def create_activity(db: Session, name: str, description: str = None):
        db_activity = models.Activity(name=name, description=description)
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    @staticmethod
    def get_activity(db: Session, activity_id: int):
        return db.query(models.Activity).filter(models.Activity.id == activity_id).first()

    @staticmethod
    def get_activity_by_name(db: Session, name: str):
        return db.query(models.Activity).filter(models.Activity.name == name).first()


# CRUD операции для Worker
class WorkerCRUD:
    @staticmethod
    def create_worker(db: Session, train_id: int, uniform_id: int, helmet_on: bool, 
                     appearance_time: datetime, disappearance_time: datetime):
        db_worker = models.Worker(
            train_id=train_id,
            uniform_id=uniform_id,
            helmet_on=helmet_on,
            appearance_time=appearance_time,
            disappearance_time=disappearance_time
        )
        db.add(db_worker)
        db.commit()
        db.refresh(db_worker)
        return db_worker

    @staticmethod
    def get_worker(db: Session, worker_id: int):
        return db.query(models.Worker).filter(models.Worker.id == worker_id).first()

    @staticmethod
    def get_workers_by_train(db: Session, train_id: int):
        return db.query(models.Worker).filter(models.Worker.train_id == train_id).all()

    @staticmethod
    def get_workers_in_time_range(db: Session, start_time: datetime, end_time: datetime):
        return db.query(models.Worker).filter(
            and_(
                models.Worker.appearance_time <= end_time,
                models.Worker.disappearance_time >= start_time
            )
        ).all()


# CRUD операции для WorkerActivity
class WorkerActivityCRUD:
    @staticmethod
    def create_worker_activity(db: Session, worker_id: int, activity_id: int, 
                              start_time: datetime, end_time: datetime):
        db_activity = models.WorkerActivity(
            worker_id=worker_id,
            activity_id=activity_id,
            start_time=start_time,
            end_time=end_time
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    @staticmethod
    def get_worker_activities(db: Session, worker_id: int):
        return db.query(models.WorkerActivity).filter(
            models.WorkerActivity.worker_id == worker_id
        ).all()

    @staticmethod
    def get_activities_in_time_range(db: Session, start_time: datetime, end_time: datetime):
        return db.query(models.WorkerActivity).filter(
            and_(
                models.WorkerActivity.start_time <= end_time,
                models.WorkerActivity.end_time >= start_time
            )
        ).all()

# CRUD операции для MeanWorkingTime
class MeanWorkingTimeCRUD:
    @staticmethod
    def create_or_update_mean_working_time(db: Session, uniform_id: int, uniform_color: str,
                                         mean_seconds: int, worker_count: int, activity_count: int):
        """Создает или обновляет запись о среднем времени работы"""
        existing = db.query(models.MeanWorkingTime).filter(
            models.MeanWorkingTime.uniform_id == uniform_id
        ).first()
        
        if existing:
            existing.mean_seconds = mean_seconds
            existing.worker_count = worker_count
            existing.activity_count = activity_count
            existing.last_updated = datetime.now()
        else:
            db_record = models.MeanWorkingTime(
                uniform_id=uniform_id,
                uniform_color=uniform_color,
                mean_seconds=mean_seconds,
                worker_count=worker_count,
                activity_count=activity_count
            )
            db.add(db_record)
        
        db.commit()
        return existing or db_record

    @staticmethod
    def get_mean_working_time(db: Session, uniform_id: int):
        return db.query(models.MeanWorkingTime).filter(
            models.MeanWorkingTime.uniform_id == uniform_id
        ).first()

    @staticmethod
    def get_all_mean_working_times(db: Session):
        return db.query(models.MeanWorkingTime).order_by(models.MeanWorkingTime.uniform_id).all()

    @staticmethod
    def calculate_and_update_all(db: Session):
        """Вычисляет и обновляет среднее время работы для всех униформ"""
        from sqlalchemy import func
        
        # Запрос для вычисления среднего времени работы (активность ID=1 - "работает")
        results = db.query(
            models.Uniform.id,
            models.Uniform.color,
            func.avg(func.extract('epoch', models.WorkerActivity.end_time - models.WorkerActivity.start_time)).label('mean_seconds'),
            func.count(func.distinct(models.Worker.id)).label('worker_count'),
            func.count(models.WorkerActivity.id).label('activity_count')
        ).join(models.Worker, models.Worker.uniform_id == models.Uniform.id)\
         .join(models.WorkerActivity, models.WorkerActivity.worker_id == models.Worker.id)\
         .filter(models.WorkerActivity.activity_id == 1)\
         .group_by(models.Uniform.id, models.Uniform.color)\
         .all()
        
        updated_records = []
        for uniform_id, color, mean_seconds, worker_count, activity_count in results:
            record = MeanWorkingTimeCRUD.create_or_update_mean_working_time(
                db, uniform_id, color, 
                int(mean_seconds) if mean_seconds else 0,
                worker_count, activity_count
            )
            updated_records.append(record)
        
        return updated_records
    
# CRUD операции для Alert
class AlertCRUD:
    @staticmethod
    def create_alert(db: Session, worker_id: int, alert_type: str, danger_message: str, alert_time: datetime):
        db_alert = models.Alert(
            worker_id=worker_id,
            alert_type=alert_type,
            danger_message=danger_message,
            alert_time=alert_time
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert

    @staticmethod
    def get_alert(db: Session, alert_id: int):
        return db.query(models.Alert).filter(models.Alert.id == alert_id).first()

    @staticmethod
    def get_alerts_by_worker(db: Session, worker_id: int):
        return db.query(models.Alert).filter(models.Alert.worker_id == worker_id).all()

    @staticmethod
    def get_alerts_by_type(db: Session, alert_type: str):
        return db.query(models.Alert).filter(models.Alert.alert_type == alert_type).all()

    @staticmethod
    def get_alerts_in_time_range(db: Session, start_time: datetime, end_time: datetime):
        return db.query(models.Alert).filter(
            and_(
                models.Alert.alert_time >= start_time,
                models.Alert.alert_time <= end_time
            )
        ).order_by(models.Alert.alert_time).all()

