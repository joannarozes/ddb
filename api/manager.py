import json

from bottle import run, get, request, abort, response

from db.db import session
from db.models import Metric, WeatherStation
from api.errors import error404, error400, error500


def jsonp(rq, dictionary):
    if rq.query.callback:
        return "%s(%s)" % (rq.query.callback, json.dumps(dictionary))
    return dictionary


@get('/stations')
def get_stations():
    stations = session.query(WeatherStation).all()

    stations_list = []
    for station in stations:
        station_dict = {
            'id': station.id,
            'name': station.name,
            'position': {
                'lat': station.latitude,
                'lng': station.longitude,
            },
            'metric_types': [],
        }

        for metric_type in station.metric_types:
            type_dict = {
                'id': metric_type.id,
                'name': metric_type.name,
                'unit': metric_type.unit,
                'last': []
            }

            metrics = (
                session.query(Metric).
                filter_by(weather_station=station, metric_type=metric_type).
                order_by(Metric.timestamp.desc()).
                limit(20)
            )

            for metric in metrics:
                metric_dict = {
                    'value': metric.value,
                    'timestamp': metric.timestamp.strftime('%s'),
                }

                type_dict['last'].append(metric_dict)

            station_dict['metric_types'].append(type_dict)

        stations_list.append(station_dict)

    return jsonp(request, {'stations': stations_list})


def main():
    run(host='0.0.0.0', port=8081)


if __name__ == '__main__':
    main()
