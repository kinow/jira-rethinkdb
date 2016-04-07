
var express = require('express'),
    mustacheExpress = require('mustache-express');
var app = express();

//app.set('view engine', 'mustache');
app.engine('html', mustacheExpress());
app.set('view engine', 'html');
app.set('views', __dirname + '/views');
app.use('/static', express.static(__dirname + '/public'));

var r = require('rethinkdb')

var connection = null;
r.connect( {host: '172.17.0.2', port: 28015}, function(err, conn) {
    if (err) throw err;
    connection = conn;
});

app.get('/', function (req, res) {
    var perMonth = r.db('jira')
        .table('issues')
        .group(
            r.row('created').slice(0, 7)
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
                    data.push({ "Value": entry.reduction, "Month": entry.group });
                }
                res.render('report_1', {'data': JSON.stringify(data) });
            });
        })
    ;
});

app.listen(3000, function () {
    console.log('Example app listening on port 3000!');
});