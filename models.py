from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Train(Base):
    """Модель поездов"""
    __tablename__ = "trains"

    id = Column(BigInteger, primary_key=True, index=True)
    train_number = Column(String(20), nullable=False, index=True)
    arrival_time = Column(DateTime, nullable=False)
    departure_time = Column(DateTime, nullable=True)  # Изменено на nullable=True
    
    # Связи
    workers = relationship("Worker", back_populates="train", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Train(id={self.id}, number='{self.train_number}')>"


class Uniform(Base):
    """Модель униформы"""
    __tablename__ = "uniforms"

    id = Column(Integer, primary_key=True, index=True)
    color = Column(String(50), nullable=False, unique=True, index=True)
    
    # Связи
    workers = relationship("Worker", back_populates="uniform")

    def __repr__(self):
        return f"<Uniform(id={self.id}, color='{self.color}')>"


class Activity(Base):
    """Модель видов деятельности"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Связи
    worker_activities = relationship("WorkerActivity", back_populates="activity")

    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.name}')>"


class Worker(Base):
    """Модель работников"""
    __tablename__ = "workers"

    id = Column(BigInteger, primary_key=True, index=True)
    train_id = Column(BigInteger, ForeignKey("trains.id", ondelete="CASCADE"), nullable=False)
    uniform_id = Column(Integer, ForeignKey("uniforms.id"), nullable=False)
    helmet_on = Column(Boolean, nullable=False, default=False)
    appearance_time = Column(DateTime, nullable=False)
    disappearance_time = Column(DateTime, nullable=True)  # Изменено на nullable=True
    
    # Связи
    train = relationship("Train", back_populates="workers")
    uniform = relationship("Uniform", back_populates="workers")
    activities = relationship("WorkerActivity", back_populates="worker", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Worker(id={self.id}, train_id={self.train_id}, uniform_id={self.uniform_id})>"


class WorkerActivity(Base):
    """Модель активностей работников"""
    __tablename__ = "worker_activities"

    id = Column(BigInteger, primary_key=True, index=True)
    worker_id = Column(BigInteger, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)  # Изменено на nullable=True

    # Связи
    worker = relationship("Worker", back_populates="activities")
    activity = relationship("Activity", back_populates="worker_activities")

    def __repr__(self):
        return f"<WorkerActivity(id={self.id}, worker_id={self.worker_id}, activity_id={self.activity_id})>"
    

class MeanWorkingTime(Base):
    """Модель среднего времени работы по униформам"""
    __tablename__ = "mean_working_time"

    id = Column(Integer, primary_key=True, index=True)
    uniform_id = Column(Integer, ForeignKey("uniforms.id"), nullable=False, unique=True)
    # uniform_color УДАЛЕН - используем связь с таблицей uniforms
    mean_seconds = Column(Integer, nullable=False)  # Среднее время в секундах
    worker_count = Column(Integer, nullable=False)  # Количество работников
    activity_count = Column(Integer, nullable=False)  # Количество активностей
    last_updated = Column(DateTime, default=datetime.now, nullable=False)
    
    # Связи
    uniform = relationship("Uniform")

    def __repr__(self):
        return f"<MeanWorkingTime(uniform_id={self.uniform_id}, mean_seconds={self.mean_seconds})>"
    
class Alert(Base):
    """Модель происшествий и предупреждений"""
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    worker_id = Column(BigInteger, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(100), nullable=False, index=True)  # тип происшествия
    danger_message = Column(Text, nullable=False)  # сообщение об опасности
    alert_time = Column(DateTime, nullable=False, index=True)  # время происшествия
    
    # Связи
    worker = relationship("Worker")

    def __repr__(self):
        return f"<Alert(id={self.id}, worker_id={self.worker_id}, type='{self.alert_type}')>"