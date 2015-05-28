from models import Base, engine, MetricType
from sqlalchemy.orm import Session
import uuid
import os

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

session = Session(engine)

def initialize_metric_types():
    metric_types = [None] * 2

    metric_types[0] = MetricType()
    metric_types[0].id = str(uuid.uuid4())
    metric_types[0].name = 'Temperature'
    metric_types[0].min_value = -50.0
    metric_types[0].max_value = 50.0
    metric_types[0].unit = 'C'

    metric_types[1] = MetricType()
    metric_types[1].id = str(uuid.uuid4())
    metric_types[1].name = 'Humidity'
    metric_types[1].min_value = 0.0
    metric_types[1].max_value = 100.0
    metric_types[1].unit = '%'

    session.add_all(metric_types)

    session.commit()

try:
    os.remove('station_db.db')
except Exception as ex:
    pass

initialize_metric_types()
