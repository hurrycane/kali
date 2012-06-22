var metrics = require("../metrics").Metrics;
var moment = require('moment');

exports.index = function(req, res){
  var nav =  {'home' : 'active', 'quick' : '', 'dashboard' : ''}
  res.render('index', { title: 'Express',  nav : nav})
};

exports.search = function(req, res){
  var nav =  {'home' : '', 'quick' : '', 'dashboard' : ''}
  metrics.find({"name" : req.query['q']},function (err, docs) {
    res.render('search', { title: docs, moment: moment,  nav : nav})
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