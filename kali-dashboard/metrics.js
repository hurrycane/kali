var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/monitoring');

var Schema = mongoose.Schema, ObjectId = Schema.ObjectId;
var Metrics = new Schema({
      _id       : ObjectId
    , name      : String
    , stats     : {
      p90       : String
    , p50       : String
    , max       : String
    , min       : String
    , n         : Number
    }
    , timestamp : Number
    , period    : Number
});

var MyModel = mongoose.model('metrics', Metrics);


exports.Metrics = MyModel;
