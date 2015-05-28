Add metric
==========
```
{
    "action": "add_metric",
    "data": {
        "id": <id>,
        "value": <value>,
        "metric_type_id": <metric_type_id>,
        "weather_station_id": <weather_station_id>,
    }
}
```

Add weather station
===================
```
{
    "action": "add_station",
    "data": {
        "id": <id>,
        "name": <name>,
        "latitude": <latitude>,
        "longitude": <longitude>,
        "metric_types": [
            <metric_type_id1>,
            <metric_type_id2>,
        ],
    }
}
```