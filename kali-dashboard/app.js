
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes');
var io = require('socket.io');

var metrics = require("./metrics").Metrics;
var moment = require('moment');

var app = module.exports = express.createServer();

// Configuration

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(express.static(__dirname + '/public'));
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function(){
  app.use(express.errorHandler());
});

// Routes

app.get('/', routes.index);
app.get('/search', routes.search);
app.get('/quick', routes.quick);
app.get('/metrics/names', routes.all);
app.get('/dashboard/:id', routes.show);
app.get('/dashboard/save', routes.save);

app.get('/metrics', routes.metrics);

app.listen(3000);

var sio = io.listen(app);

var client_count = 0;
var client_

sio.sockets.on('connection', function (socket) {
  // search for metrics
  socket.on('subscribe', function (data) {
    var mapping = { '10s' : 10, '1 min' : 60, '10 mins' : 600};
    var period = 10;
    var timestamp = moment().unix();
    var metric_type = 'n';
    var start = moment().unix();
    
    socket.set('client_id', "on", function () {});

    if(data.p) period = mapping[data.p];
    if(data.t) timestamp = data.t;
    if(data.metric_type) metric_type = data.metric_type;
    if(data.start) start = data.start;
    
    var interval_id = null;
    
    var timed_out = function(){
      console.log("Time-out function called.")
      socket.get('client_id', function (err,status) {
        
        if(status == "on"){
          metrics
          .where('name',data.name)
          .where('period',period)
          .where('timestamp').gt(timestamp)
          .exec(function(e,d){

            metrics
            .where('name',data.name)
            .where('period',period)
            .where('timestamp').gt(data.start)
            .sort('stats.' + metric_type,-1)
            .limit(1)
            .exec(function(error,docs){
              if(d.length > 0){
                socket.emit('metrics', {data : d, max : docs});
                timestamp = d[d.length-1].timestamp;
              }
            })

          });
          
        }else{
          console.log("Clearing interval");
          clearInterval(interval_id);
        }
      });
    };
    
    interval_id = setInterval(timed_out,period * 1000)
  });
  
  socket.on('disconnect', function () {
    socket.get('client_id', function (status) {
      if(status == "on"){
        socket.set('client_id', "off", function () {});
      }
    });
  });
});
