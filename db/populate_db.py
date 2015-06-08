from create_db import session
from models import MetricType
import uuid

def initialize_metric_types():
    metric_types = [None] * 2

    metric_types[0] = MetricType()
    metric_types[0].id = '00000000-0000-0000-0000-000000000001'
    metric_types[0].name = 'Temperature'
    metric_types[0].min_value = -50.0
    metric_types[0].max_value = 50.0
    metric_types[0].unit = 'C'

    metric_types[1] = MetricType()
    metric_types[1].id = '00000000-0000-0000-0000-000000000002'
    metric_types[1].name = 'Humidity'
    metric_types[1].min_value = 0.0
    metric_types[1].max_value = 100.0
    metric_types[1].unit = '%'

    session.add_all(metric_types)

    session.commit()

initialize_metric_types()
