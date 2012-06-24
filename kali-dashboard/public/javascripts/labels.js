var Labels = {
  '10s' : function(start_time,end_time) {
    var smoment = moment(start_time);
    var w = 624;

    var period = 15;

    var subs_start = smoment.format('m') % period;
    var subs_second = parseInt ( smoment.format('s') / 10 );
    var firstLabel = smoment.subtract('minutes',subs_start);

    var labels = [];
    labels.push(firstLabel.format('HH:mm:ss'))

    w -= subs_start * 6 + subs_second;

    while(w > period){
      var now = firstLabel.subtract('minutes',period);
      labels.push(firstLabel.format('HH:mm:ss'))

      w -= period * 6;
    }
    return [subs_start * 6 + subs_second,labels];
  },
  '1 min' : function(start_time,end_time) {
    var smoment = moment(start_time);
    var w = 624;

    var period = 15;

    var remaining_mins = smoment.format('m') % period;
    var nb_mins = parseInt(smoment.format('m') / period);

    var mins_sub = 6 - nb_mins;
    var firstLabel = smoment.subtract('minutes',mins_sub * period + remaining_mins);

    var labels = [];
    labels.push(firstLabel.format('HH:mm'))

    w -= mins_sub * period + remaining_mins;

    while(w > period){
      var now = firstLabel.subtract('minutes',period * 6);
      labels.push(firstLabel.format('HH:mm'))

      w -= period * 6;
    }
    return [mins_sub * period + remaining_mins,labels];
  },
  '10 mins' : function(start_time,end_time) {
    var smoment = moment(start_time);
    var w = 624;

    var period = 15;

    var remaining_h = smoment.format('h') % 15;
    var firstLabel = smoment.subtract('hours',remaining_h);

    var labels = [];
    labels.push(firstLabel.format('DD MMM H:m'))

    w -= remaining_h;

    while(w > period){
      var now = firstLabel.subtract('hours',15);
      labels.push(firstLabel.format('DD MMM H:00'))

      w -= period * 6;
    }

    return [remaining_h,labels];
  }
}
