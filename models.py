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
    departure_time = Column(DateTime, nullable=False)
    
    # Связи
    workers = relationship("Worker", back_populates="train", cascade="all, delete-orphan")
    frame_statistics = relationship("FrameStatistics", back_populates="train")

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
    disappearance_time = Column(DateTime, nullable=False)
    
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
    end_time = Column(DateTime, nullable=False)
    
    # Связи
    worker = relationship("Worker", back_populates="activities")
    activity = relationship("Activity", back_populates="worker_activities")

    def __repr__(self):
        return f"<WorkerActivity(id={self.id}, worker_id={self.worker_id}, activity_id={self.activity_id})>"


class FrameStatistics(Base):
    """Модель статистики по кадрам"""
    __tablename__ = "frame_statistics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    workers_count = Column(Integer, nullable=False)
    train_id = Column(BigInteger, ForeignKey("trains.id"), nullable=False)
    
    # Связи
    train = relationship("Train", back_populates="frame_statistics")

    def __repr__(self):
        return f"<FrameStatistics(id={self.id}, timestamp={self.timestamp}, workers={self.workers_count})>"