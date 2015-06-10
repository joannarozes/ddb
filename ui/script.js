var map;
var stations = {};
var metrics = {};
var serverIP = null;

function formatTimestamp(unixTimestamp) {
    var dt = new Date(unixTimestamp * 1000);

    var hours = dt.getHours();
    var minutes = dt.getMinutes();
    var seconds = dt.getSeconds();

    if (hours < 10)
     hours = '0' + hours;

    if (minutes < 10)
     minutes = '0' + minutes;

    if (seconds < 10)
     seconds = '0' + seconds;

    return hours + ":" + minutes + ":" + seconds;
}

function addStation(station) {
    var marker = new google.maps.Marker({
        position: station.position,
        title: station.name
    });

    content = '<h1>' + station.name + '</h1>'
    for (var i = 0; i < station.metric_types.length; ++i) {
        metric_type = station.metric_types[i];

        content += '<strong>' + metric_type.name + ' (' + metric_type.unit + '): </strong><br />';
        content += '<canvas id="' + station.id + metric_type.id + '" width="500" height="200"></canvas><br />';
    }

    var infowindow = new google.maps.InfoWindow({
        content: content
    });

    marker.setMap(window.map);

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(window.map, marker);
    });
    google.maps.event.addListener(marker, 'click', function() {
        drawCharts(station.id);
    });
}

function drawCharts(id) {
    station = window.stations[id]

    for (var i = 0; i < station.metric_types.length; ++i) {
        metric_type = station.metric_types[i];

        canvas = document.getElementById(station.id + metric_type.id);
        if (canvas) { // If not, then infowindow is probably closed...
            ctxt = canvas.getContext('2d');

            var reversed = metric_type.last.slice()
            reversed.reverse();
            var data = {
                labels: reversed.map(function(metric) {
                            return formatTimestamp(metric.timestamp);
                        }),
                datasets: [
                    {
                        label: "My First dataset",
                        fillColor: "rgba(220,220,220,0.2)",
                        strokeColor: "rgba(220,220,220,1)",
                        pointColor: "rgba(220,220,220,1)",
                        pointStrokeColor: "#fff",
                        pointHighlightFill: "#fff",
                        pointHighlightStroke: "rgba(220,220,220,1)",
                        data: reversed.map(function(metric) {
                            return metric.value;
                        })
                    },
                ]
            };

            var myLineChart = new Chart(ctxt).Line(data, {'animation': false});
        }

    }
}

function updateStation(station) {
    if (!(station.id in stations)) {
        addStation(station);
    }

    window.stations[station.id] = station

    drawCharts(station.id);
}

function update() {
    jQuery.get("http://" + serverIP + ":8081/stations",
        function(response) {
            stations = response.stations

            for (var i = 0; i < stations.length; ++i) {
                updateStation(stations[i]);
            }
        },
        "jsonp"
    );
}

function initialize() {
    window.serverIP = prompt("Enter server IP:", "127.0.0.1");

    var mapOptions = {
        center: {lat: 52.187405, lng: 19.401855},
        zoom: 6
    };

    window.map = new google.maps.Map(document.getElementById('map-canvas'),
        mapOptions);

    setInterval(update, 5000);

    update();
}

google.maps.event.addDomListener(window, 'load', initialize);