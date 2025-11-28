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


# CRUD операции для FrameStatistics
class FrameStatisticsCRUD:
    @staticmethod
    def create_frame_statistics(db: Session, timestamp: datetime, workers_count: int, train_id: int):
        db_stats = models.FrameStatistics(
            timestamp=timestamp,
            workers_count=workers_count,
            train_id=train_id
        )
        db.add(db_stats)
        db.commit()
        db.refresh(db_stats)
        return db_stats

    @staticmethod
    def get_statistics_by_train(db: Session, train_id: int):
        return db.query(models.FrameStatistics).filter(
            models.FrameStatistics.train_id == train_id
        ).order_by(models.FrameStatistics.timestamp).all()

    @staticmethod
    def get_statistics_in_time_range(db: Session, start_time: datetime, end_time: datetime):
        return db.query(models.FrameStatistics).filter(
            and_(
                models.FrameStatistics.timestamp >= start_time,
                models.FrameStatistics.timestamp <= end_time
            )
        ).order_by(models.FrameStatistics.timestamp).all()