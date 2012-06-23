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
  '1 h' : function(start_time,end_time) {
    var smoment = moment(start_time);
    var w = 624;

    var period = 15;

    var remaining_h = smoment.format('h');
    
    var firstLabel = smoment.subtract('hours',remaining_h);

    var labels = [];
    labels.push(firstLabel.format('DD MMM H:00'))

    w -= remaining_h;

    while(w > period){
      var now = firstLabel.subtract('hours',90);
      labels.push(firstLabel.format('DD MMM H:00'))

      w -= period * 6;
    }

    return [remaining_h,labels];
  }
}

var data = null;

var Graph = (function(){

  var w = 1, h = 100;
  var v = 70;

  var width = 624;
  var padding = 25;
  var x = d3.scale.linear().domain([0, 1]).range([0, w]);
  var y = d3.scale.linear().domain([0, 100]).rangeRound([0, h]);

  var data = [];
  var graphNb = 0;

  function lastValue(set){
    return set[set.length - 1].actual_value;
  }

  function prepareData(input,metric_type){
    if(input["data"].length < width){
      var zeros = width - input["data"].length;
    }

    var dataset = [];
    for(var i=0;i<zeros;i++){
      dataset.push({value : 0});
    }

    if(zeros == 624) return dataset;

    var highest = input['max'][0]['stats'][metric_type];

    $.each(input["data"],function(index,value){

      var current_value = value['stats'][metric_type] * 1;
      var published_value = value['stats'][metric_type]  * 100 / highest;
      if(current_value == null || published_value == null){
        dataset.push({value : 0, actual_value : 0});
      }else{
        dataset.push({value : published_value.toFixed(2), actual_value : current_value.toFixed(2), t : value.timestamp});
      }

    });

    return dataset;
  }

  function drawGraph(color,label,period,input,metric_type){
    graphNb +=1;
    var position = graphNb;
    
    var f_label = Labels[period];
    
    function next() {
      return {
        value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))
      };
    };

    data[position] = prepareData(input,metric_type);

    var chartContainer = d3.select("div.span8")
      .append("div")
      .attr("class", "chart_container");
    
    var chart = chartContainer
      .append("canvas")
      .attr("id", "chart")
      .attr("width", width)
      .attr("height", h + 2 * padding);

    var ctx = chart[0][0].getContext("2d");

    redraw();

    chartContainer.append("span").attr("class","chart_label").text(label);

    chartContainer.append("span").attr("class","chart_current_value").text(lastValue(data[position]));
    chartContainer.append("span").attr("class","chart_value").text(lastValue(data[position]));

    function redraw(){
      var last_timestamp = data[position][data[position].length - 1].t;
      var l = f_label(last_timestamp,last_timestamp);

      var startIndex = parseInt(l[0]);
      var labels = l[1];

      // clear canvas
      ctx.clearRect(0,0,width,h + 2 * padding);

      ctx.fillStyle = "black";
      ctx.font         = '9px Verdana';
      ctx.textBaseline = 'top';
      
      $.each(labels,function(index,value){
        var textWidth = ctx.measureText(value).width;
        ctx.fillText(value, width - (startIndex + 15*6* index) - Math.round(textWidth/2), 2);
        ctx.fillRect(width - (startIndex + 15*6* index),16,1,5);
      })

      // upper line
      // context . fillRect(x, y, w, h)
      ctx.fillRect(0,padding,width,1);

      // graph color
      ctx.fillStyle = color;
      // lines itself
      $.each(data[position],function(index,d){
        ctx.fillRect(index,h + padding + 1 - y(d.value),1,y(d.value));
      })

      // bottom line
      ctx.fillStyle = "black";
      ctx.fillRect(0,h + padding + 1,width,1);
    }
  }

  return {
    data : function(){
      return data;
    },
    graphNb : function(){
      return graphNb;
    },
    draw : drawGraph
  }

})();