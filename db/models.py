from sqlalchemy import Column, ForeignKey, Table, String, Float, Integer, \
    DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os


Base = declarative_base()


type_station_table = Table('metric_type_station', Base.metadata,
                           Column('type_id', String(36),
                                  ForeignKey('metric_types.id')),
                           Column('station_id', String(36),
                                  ForeignKey('weather_stations.id')))


class MetricType(Base):
    __tablename__ = 'metric_types'
    id = Column(String(36), primary_key=True)
    name = Column(String(250), nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    unit = Column(String(250))

    def __init__(self, id=None, name=None, min_value=None, max_value=None,
                 unit=None):
        self.id = id
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.unit = unit


class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    id = Column(String(36), primary_key=True)
    name = Column(String(250), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    deleted = Column(Integer, default=0)
    is_sent = Column(Integer, default=0)
    metric_types = relationship("MetricType", secondary=type_station_table,
                                backref="weather_stations")

    def __init__(self, id=None, name=None, latitude=None, longitude=None,
                 metric_types=[]):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.metric_types = metric_types


class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(String(36), primary_key=True)
    value = Column(Float, nullable=False)
    is_sent = Column(Integer, default=0)
    metric_type_id = Column(String(36), ForeignKey('metric_types.id'))
    metric_type = relationship(MetricType)
    weather_station_id = Column(String(36), ForeignKey('weather_stations.id'))
    weather_station = relationship(WeatherStation)
    timestamp = Column(DateTime, nullable=False, default=False)

    def __init__(self, id=None, value=None, metric_type=None,
                 weather_station=None):
        self.id = id
        self.value = value
        self.metric_type = metric_type
        self.weather_station = weather_station


# Create an engine that stores data in the local directory's
db_name = 'station.db'
dir_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(dir_path, db_name)
engine = create_engine('sqlite:///%s' % db_path)
