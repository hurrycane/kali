var cbrewer = [ "#7FCDBB", "#2C7FB8", "#ADDD8E", "#31A354", "#C51B8A", "#FA9FB5", "#A6BDDB", "#2B8CBE", "#FDBB84", "#E34A33", "#A8DDB5", "#43A2CA", "#8856A7", "#9EBCDA", "#2CA25F", "#99D8C9" ];

var show = {
  count : 0,
}

var Kali = {
  init_datepickers : function(){
    $('.date_start').datepicker();
    $('.date_end').datepicker();
    $('.time_start').timepicker();
    $('.time_end').timepicker();
  },
  
  init_typeahead : function(){
    $.getJSON('/metrics/names',function(data){
      $('.search-query').typeahead({
        source: data
      })

      $('#input01').typeahead({
        source: data
      })
    })
    
  },
  init_now : function(){
    $("#now_btn").bind('click',function(e){
      e.preventDefault();
      $(".date_end").val("now");
      $(".time_end").val("");
    });
  },
  init_line : function(){
    $(".span8").bind("mousemove",function(e){
       var parentOffset = $(this).offset();
       //or $(this).offset(); if you really just want the current element's offset
       var relX = e.pageX - parentOffset.left;
       var relY = e.pageY - parentOffset.top;

       // console.log(Math.round(relX));
       $(".line").css("left",e.pageX + "px");
       $(".line").css("height",$("#wrapper").height() + 50 + "px");

       $.each($(".chart_value"),function(index,value){
         var offset = Math.round(relX);
         if(offset < 624){
           var position = parseInt($(value).attr("ref"));
           var d = Graph.data[position];
           $(value).text(d[offset-1].actual_value);
         }
       });

       $(".chart_value").css("left",-80 + relX + "px");
    });

    $(".span8").bind("mouseover",function(e){
      $(".line").show();
      $(".chart_value").show();
    });

    $(".span8").bind("mouseout",function(e){
      $(".line").hide();
      $(".chart_value").hide();
    });
    
    $("#update").bind("click",function(event){
      event.preventDefault();
    });
  }
}

Kali.AddGraph = {
  metric_name : null,
  date_start : null,
  date_end: null,
  is_now : null,
  current_color: null,
  validate : function(){
    Kali.AddGraph.metric_name = $("#input01").val();
    if(Kali.AddGraph.metric_name.length == 0){
      alert("You need a metric name to draw a graph");
      return false;
    }

    Kali.AddGraph.date_start = moment($(".date_start").val() + " "+ $(".time_start").val(), "DD-MM-YYYY hh:mm A");
    Kali.AddGraph.date_end = null;
    Kali.AddGraph.is_now = false;

    if($(".date_end").val() == "now" && $(".time_end").val() == ""){
      Kali.AddGraph.date_end = moment();
      Kali.AddGraph.is_now = true;
    }else{
      Kali.AddGraph.date_end = moment($(".Kali.AddGraph.date_end").val() + " " + $(".time_end").val(), "DD-MM-YYYY hh:mm A");      
    }

    if(Kali.AddGraph.date_start > Kali.AddGraph.date_end){
      alert('Start time should be lower than end time');
      return false;
    }

    return true;
  },

  addMetricBox : function(){
    var container = $(".left-column-item");
    
    // if no container present add one
    if(container.length == 0){
      var future_container = $("<div />").attr("class","left-column-item");
      $(".span4").append(future_container);
      container = $(".left-column-item");
    }

    // select the last container
    container = container[container.length-1];

    var metric_entry = $("#metricTemplate").tmpl({name:Kali.AddGraph.metric_name})
    var icon = metric_entry.find(".icon-envelope");
    
    var color_id = parseInt(Math.random()*16);
    Kali.AddGraph.current_color = cbrewer[color_id];
    icon.css("background-color",Kali.AddGraph.current_color);
    
    metric_entry.attr("ref",show.count);
    
    var c = show.count;
    
    metric_entry.find("a").bind("click",function(event){
      event.preventDefault();
      $(".input-prepend[ref="+c+"]").remove();
      
      if($(".input-prepend").length == 0){
        $(".left-column-item").remove();
      }
    });
    
    show.count++;

    metric_entry.appendTo(container);
  },
  getTimeSeris: function(event){
    var period = $("#select01").val();
    var metric_type = $("#select02").val();
    
    $.ajax({
      url: '/metrics',
      data: {
        name : Kali.AddGraph.metric_name,
        period : period,
        metric_type : metric_type,
        s : Kali.AddGraph.date_start.unix(),
        e : Kali.AddGraph.date_end.unix(),
      },
      success: function(response){
        if(response.data.length == 0) {
          alert("Data points not found for that metric/interval");
        }else{
          Kali.AddGraph.addMetricBox();
          var position = Graph.draw(Kali.AddGraph.current_color,
                                    Kali.AddGraph.metric_name,
                                    period,
                                    response,
                                    metric_type);

          if(Kali.AddGraph.is_now){
            Kali.AddGraph.getSocket(response,metric_type,position,Kali.AddGraph.date_start.unix());
          }
        }
      }
    });
  },
  getSocket : function(response,metric_type,position,date_start){
    var t = null;
    if(response.data.length > 0){
      t = response.data[response.data.length -1].timestamp;
    }else{
      return ;
    }
    
    var period = $("#select01").val();
    var mapping = {
      "10s" : "10",
      "1 min" : "60",
      "10 mins" : "600"
    };
    
    var metric_name = "" + Kali.AddGraph.metric_name;
    var socket = io.connect('http://localhost:3000');
    socket.emit('subscribe', { name : metric_name, t : t, metric_type : metric_type, p : period, start : date_start});
    socket.on('metrics', function (data) {
      var state = Graph.state[position];
      
      state.input["max"] = data["max"];
      $.each(data.data,function(index,value){
        state.input["data"].push(value);
      })
      
      Graph.data[position] = Graph.prepareData(state.input,metric_type,mapping[period],position);
      Graph.redraw(state);
      $(".chart_current_value[ref=1]").text(Graph.lastValue(Graph.data[position]));
    });
  },
  handler : function(event){
    event.preventDefault();
    // validate adding a new graph
    if(!Kali.AddGraph.validate()) return;
    Kali.AddGraph.getTimeSeris();
  }
}

$(document).ready(function(){
  
  Kali.init_datepickers();
  Kali.init_typeahead();
  Kali.init_now();

  $("#add_btn").bind("click",Kali.AddGraph.handler);
  
  Kali.init_line();
})