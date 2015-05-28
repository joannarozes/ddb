from sqlalchemy import Column, ForeignKey, Table, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


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


class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    id = Column(String(36), primary_key=True)
    name = Column(String(250), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    metric_types = relationship("MetricType", secondary=type_station_table,
                                backref="weather_stations")


class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(String(36), primary_key=True)
    value = Column(Float, nullable=False)
    metric_type_id = Column(String(36), ForeignKey('metric_types.id'))
    metric_type = relationship(MetricType)
    weather_station_id = Column(String(36), ForeignKey('weather_stations.id'))
    weather_station = relationship(WeatherStation)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///station_db.db')
