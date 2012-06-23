var metrics = require("../metrics").Metrics;
var moment = require('moment');

exports.index = function(req, res){
  var nav =  {'home' : 'active', 'quick' : '', 'dashboard' : ''}
  res.render('index', { title: 'Express',  nav : nav})
};

exports.search = function(req, res){
  var nav =  {'home' : '', 'quick' : '', 'dashboard' : ''};
  
  metrics
  .where('name',req.query['q'])
  .distinct('name',function(e,docs){
    res.render('search', { items: docs, moment: moment,  nav : nav})
  });
}; 

exports.quick = function(req, res){
  var nav =  {'home' : '', 'quick' : 'active', 'dashboard' : ''}
  res.render('index', { title: 'Express',  nav : nav})
};

exports.all = function(req, res){
  metrics.find({},function(e,d){ }).distinct('name',function(err,docs){
    res.json(docs);
  });
};

exports.save = function(req, res){
  res.render('index', { title: 'Express',  nav : nav})
};

exports.show = function(req, res){
  var nav =  {'home' : '', 'quick' : '', 'dashboard' : 'active'}
  res.render('index', { title: 'Express',  nav : nav})
};

exports.metrics = function(req, res){
  var mapping = { '10s' : 60, '1 min':600, '1 hour' : 3600 }

  var metric_name = req.query['name']
  var period = req.query['period']
  var metric_type = req.query['metric_type']
  var start = parseInt(req.query['s'])
  var end = parseInt(req.query['e'])

  metrics
  .where('name',metric_name)
  .where('period',mapping[period])
  .where('timestamp').gte(start).lte(end)
  .exec(function(e,d){

    metrics
    .where('name',metric_name)
    .where('period',mapping[period])
    .where('timestamp').gte(start).lte(end)
    .sort('stats.' + metric_type,-1)
    .limit(1)
    .exec(function(error,docs){
      res.json({data : d, max : docs});
    })

  });
};