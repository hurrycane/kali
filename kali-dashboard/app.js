
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes');
var io = require('socket.io');

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
sio.sockets.on('connection', function (socket) {
  console.log('A socket connected!');
});
