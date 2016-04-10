
var express = require('express'),
    mustacheExpress = require('mustache-express');
var app = express();

//app.set('view engine', 'mustache');
app.engine('html', mustacheExpress());
app.set('view engine', 'html');
app.set('views', __dirname + '/views');

app.use(express.static('public'));

var r = require('rethinkdb');

var connection = null;
r.connect( {host: '172.17.0.2', port: 28015}, function(err, conn) {
    if (err) throw err;
    connection = conn;
});

app.get('/report_1', function (req, res) {
    var perMonth = r.db('jira')
        .table('issues')
        .group(
            r.row('created').slice(0, 7),
            r.row('type')
        )
        .count()
        .run(connection, function(err, cursor) {
            if (err) throw err;
            cursor.toArray(function(err, result) {
                if (err) throw err;
                //console.log(JSON.stringify(result, null, 2));
                var data = [];
                for (var i = 0; i < result.length; i++) {
                    var entry = result[i];
                    data.push({ "Count": entry.reduction, "Type": entry.group[1], "Month": entry.group[0] });
                }
                res.render('report_1', {'data': JSON.stringify(data) });
            });
        })
    ;
});

app.get('/report_2', function (req, res) {
    var perMonth = r.db('jira')
        .table('issues')
        .group(
            r.row('created').slice(0, 10).do(function(s) {
              return r.ISO8601(s, {defaultTimezone: '+00:00'}).dayOfWeek();
            }),
            r.row('type')
        )
        .count()
        .run(connection, function(err, cursor) {
            if (err) throw err;
            cursor.toArray(function(err, result) {
                if (err) throw err;
                //console.log(JSON.stringify(result, null, 2));
                var data = [];
                for (var i = 0; i < result.length; i++) {
                    var entry = result[i];
                    data.push({ "Count": entry.reduction, "Type": entry.group[1], "DayOfWeek": entry.group[0] });
                }
                for (var j = 1; j <= 7; j++) {
                    var found = false;
                    for (var k = 0; k < data.length; k++) {
                        var entry = data[k];
                        if (entry.DayOfWeek == j) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        data.push({ "Count": 0, "Type": "N/A", "DayOfWeek": j });
                    }
                }
                res.render('report_2', {'data': JSON.stringify(data) });
            });
        })
    ;
});

app.get('/report_3', function (req, res) {
    var perMonth = r.db('jira')
        .table('issues')
        .group(
            r.row('created').slice(0, 10).do(function(s) {
              return r.ISO8601(s, {defaultTimezone: '+00:00'}).month();
            }),
            r.row('created').slice(0, 10).do(function(s) {
              return r.ISO8601(s, {defaultTimezone: '+00:00'}).dayOfWeek();
            }),
            r.row('type')
        )
        .count()
        .run(connection, function(err, cursor) {
            if (err) throw err;
            cursor.toArray(function(err, result) {
                if (err) throw err;
                //console.log(JSON.stringify(result, null, 2));
                var months = {
                    '1': [],
                    '2': [],
                    '3': [],
                    '4': [],
                    '5': [],
                    '6': [],
                    '7': [],
                    '8': [],
                    '9': [],
                    '10': [],
                    '11': [],
                    '12': []
                };
                for (var i = 0; i < result.length; i++) {
                    var entry = result[i];
                    var month = entry.group[0];
                    var month_data = months[month]; // returns an array
                    month_data.push({ "Count": entry.reduction, "Type": entry.group[2], "DayOfWeek": entry.group[1] });
                }
                console.log(months);
                //res.render('report_2', {'data': months });
            });
        })
    ;
});

app.listen(3000, function () {
    console.log('Example app listening on port 3000!');
});
