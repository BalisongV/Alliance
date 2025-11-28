from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import List, Tuple
from datetime import datetime, timedelta
import models

class AnalysisQueries:
    """Класс для выполнения аналитических запросов из описания"""
    
    @staticmethod
    def find_workers_repairing_train(db: Session, train_number: str, 
                                   start_time: datetime, end_time: datetime):
        """
        Запрос 1: Найти всех работников, которые чинили поезд №XXX с 14:00 до 15:00
        """
        return db.query(models.Worker).join(models.Train).join(models.WorkerActivity).join(models.Activity).filter(
            and_(
                models.Train.train_number == train_number,
                models.Activity.name.ilike('%чинит%'),
                models.WorkerActivity.start_time <= end_time,
                models.WorkerActivity.end_time >= start_time
            )
        ).all()

    @staticmethod
    def calculate_activity_time_by_uniform(db: Session, activity_name: str):
        """
        Запрос 2: Посчитать общее время, затраченное каждым сотрудником 
        (по цвету униформы) на конкретный вид деятельности
        """
        return db.query(
            models.Uniform.color,
            func.sum(
                func.extract('epoch', models.WorkerActivity.end_time - models.WorkerActivity.start_time)
            ).label('total_seconds')
        ).join(models.Worker).join(models.WorkerActivity).join(models.Activity).filter(
            models.Activity.name == activity_name
        ).group_by(models.Uniform.color).all()

    @staticmethod
    def get_workers_presence_timeline(db: Session, train_id: int, hours: int = 24):
        """
        Запрос 3: Построить график присутствия сотрудников в кадре вокруг поезда
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return db.query(
            models.Worker.appearance_time,
            models.Worker.disappearance_time,
            models.Uniform.color,
            models.Worker.helmet_on
        ).join(models.Uniform).filter(
            and_(
                models.Worker.train_id == train_id,
                models.Worker.appearance_time <= end_time,
                models.Worker.disappearance_time >= start_time
            )
        ).order_by(models.Worker.appearance_time).all()

    @staticmethod
    def calculate_helmet_usage_percentage(db: Session):
        """
        Запрос 4: Определить процент работников, которые в течение смены надевали каску
        """
        total_workers = db.query(func.count(models.Worker.id)).scalar()
        workers_with_helmet = db.query(func.count(models.Worker.id)).filter(
            models.Worker.helmet_on == True
        ).scalar()
        
        if total_workers > 0:
            return (workers_with_helmet / total_workers) * 100
        return 0

    @staticmethod
    def find_peak_work_periods(db: Session, min_workers: int = 5, days: int = 1):
        """
        Запрос 5: Найти "периоды пиковой нагрузки" - когда в кадре одновременно находилось больше N работников
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        return db.query(models.FrameStatistics).filter(
            and_(
                models.FrameStatistics.timestamp >= start_time,
                models.FrameStatistics.timestamp <= end_time,
                models.FrameStatistics.workers_count >= min_workers
            )
        ).order_by(models.FrameStatistics.workers_count.desc()).all()

    @staticmethod
    def get_worker_activity_timeline(db: Session, worker_id: int):
        """
        Получить полную временную линию активности для конкретного работника
        """
        return db.query(
            models.WorkerActivity.start_time,
            models.WorkerActivity.end_time,
            models.Activity.name,
            models.Activity.description
        ).join(models.Activity).filter(
            models.WorkerActivity.worker_id == worker_id
        ).order_by(models.WorkerActivity.start_time).all()

    @staticmethod
    def get_busiest_trains(db: Session, limit: int = 10):
        """
        Найти поезда с наибольшим количеством работников
        """
        return db.query(
            models.Train.train_number,
            func.count(models.Worker.id).label('workers_count')
        ).join(models.Worker).group_by(
            models.Train.id, models.Train.train_number
        ).order_by(func.count(models.Worker.id).desc()).limit(limit).all()