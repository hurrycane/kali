var Graph = {
  data : {},
  state : {},
  count : 0,
  lastValue : function(set){
    return set[set.length - 1].actual_value;
  },
  prepareData : function(input,metric_type,period,position){
    var zeros = 0;
    var width = 624;

    if(input["data"].length < width){
      zeros = width - input["data"].length;
    }
    
    if(input["data"].length > width){
      input["data"] = input["data"].slice(0,width);
    }

    var dataset = [];
    if(zeros == 624) return dataset;

    // normalize metric set
    var highest = input['max'][0]['stats'][metric_type];

    var t_start = null;

    $.each(input["data"],function(index,value){
      var current_value = value['stats'][metric_type] * 1;
      var is_zero = false;

      /* The problem with showing data in this way is that you can have datapoints
       * not published on after another. This piece of code handles this edge case.
       */
      if(t_start == null){
        t_start = value.timestamp;
      }else{
        if(value.timestamp > t_start + 10){
          var nb_zeros = parseInt((value.timestamp - t_start) / period);
          if(nb_zeros < 0) nb_zeros = 0;
          for(var i=0; i < nb_zeros; i++){
            dataset.push({value : 0, actual_value : 0});
          }
        }
        
        t_start = value.timestamp;
      }

      var published_value = value['stats'][metric_type]  * 100 / highest;
      if(current_value == null || published_value == null){
        dataset.push({value : 0, actual_value : 0});
      }else{
        dataset.push({value : published_value.toFixed(2), actual_value : current_value.toFixed(2), t : value.timestamp});
      }

    });
    
    var nz = 624 - dataset.length;
    for(var i=0;i<nz;i++){
      dataset.unshift({value : 0, actual_value : 0});
    }

    return dataset;
  },
  redraw : function (drawState){
    var color = drawState.color;
    var f_label =  drawState.f_label;
    var position = drawState.position;
    var ctx = drawState.ctx;

    var w = 1, h = 100;
    var v = 70;
    var width = 624;
    var padding = 25;
    var x = d3.scale.linear().domain([0, 1]).range([0, w]);
    var y = d3.scale.linear().domain([0, 100]).rangeRound([0, h]);
    var last_timestamp = Graph.data[position][Graph.data[position].length - 1].t;
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

    // context . fillRect(x, y, w, h)

    // upper line
    ctx.fillRect(0,padding,width,1);

    // graph color
    ctx.fillStyle = color;
    // lines itself
    $.each(Graph.data[position],function(index,d){
      ctx.fillRect(index,h + padding + 1 - y(d.value),1,y(d.value));
    })

    // bottom line
    ctx.fillStyle = "black";
    ctx.fillRect(0,h + padding + 1,width,1);
  },
  draw : function(color,label,period,input,metric_type){  
    var position = (++Graph.count)
    var w = 1, h = 100;
    var v = 70;
    var width = 624;
    var padding = 25;
    var f_label = Labels[period];

    var mapping = {
      "10s" : "10",
      "1 min" : "60",
      "10 mins" : "600"
    };
    
    // populate data array
    Graph.data[position] = Graph.prepareData(input,metric_type,mapping[period],position);

    var chartContainer = d3.select("div.span8")
      .append("div")
      .attr("class", "chart_container");

    var chart = chartContainer
      .append("canvas")
      .attr("id", "chart")
      .attr("width", width)
      .attr("height", h + 2 * padding);

    var ctx = chart[0][0].getContext("2d");

    var drawState = {
      input : input,
      color : color,
      f_label : f_label,
      position : position,
      ctx : ctx,
      chartContainer: chartContainer
    };

    Graph.state[position] = drawState;
    Graph.redraw(drawState);

    chartContainer.append("span").attr("class","chart_label").text(label);
    chartContainer.append("span").attr("class","chart_current_value").attr("ref",position).text(Graph.lastValue(Graph.data[position]));
    chartContainer.append("span").attr("class","chart_value").attr("ref",position).text(Graph.lastValue(Graph.data[position]));
    return position;
  }
};