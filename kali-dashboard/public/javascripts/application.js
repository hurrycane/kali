var colors = {
            aliceblue: "#f0f8ff",
            antiquewhite: "#faebd7",
            aqua: "#00ffff",
            aquamarine: "#7fffd4",
            azure: "#f0ffff",
            beige: "#f5f5dc",
            bisque: "#ffe4c4",
            black: "#000000",
            blanchedalmond: "#ffebcd",
            blue: "#0000ff",
            blueviolet: "#8a2be2",
            brown: "#a52a2a",
            burlywood: "#deb887",
            cadetblue: "#5f9ea0",
            chartreuse: "#7fff00",
            chocolate: "#d2691e",
            coral: "#ff7f50",
            cornflowerblue: "#6495ed",
            cornsilk: "#fff8dc",
            crimson: "#dc143c",
            cyan: "#00ffff",
            darkblue: "#00008b",
            darkcyan: "#008b8b",
            darkgoldenrod: "#b8860b",
            darkgray: "#a9a9a9",
            darkgreen: "#006400",
            darkgrey: "#a9a9a9",
            darkkhaki: "#bdb76b",
            darkmagenta: "#8b008b",
            darkolivegreen: "#556b2f",
            darkorange: "#ff8c00",
            darkorchid: "#9932cc",
            darkred: "#8b0000",
            darksalmon: "#e9967a",
            darkseagreen: "#8fbc8f",
            darkslateblue: "#483d8b",
            darkslategray: "#2f4f4f",
            darkslategrey: "#2f4f4f",
            darkturquoise: "#00ced1",
            darkviolet: "#9400d3",
            deeppink: "#ff1493",
            deepskyblue: "#00bfff",
            dimgray: "#696969",
            dimgrey: "#696969",
            dodgerblue: "#1e90ff",
            firebrick: "#b22222",
            floralwhite: "#fffaf0",
            forestgreen: "#228b22",
            fuchsia: "#ff00ff",
            gainsboro: "#dcdcdc",
            ghostwhite: "#f8f8ff",
            gold: "#ffd700",
            goldenrod: "#daa520",
            gray: "#808080",
            green: "#008000",
            greenyellow: "#adff2f",
            grey: "#808080",
            honeydew: "#f0fff0",
            hotpink: "#ff69b4",
            indianred: "#cd5c5c",
            indigo: "#4b0082",
            ivory: "#fffff0",
            khaki: "#f0e68c",
            lavender: "#e6e6fa",
            lavenderblush: "#fff0f5",
            lawngreen: "#7cfc00",
            lemonchiffon: "#fffacd",
            lightblue: "#add8e6",
            lightcoral: "#f08080",
            lightcyan: "#e0ffff",
            lightgoldenrodyellow: "#fafad2",
            lightgray: "#d3d3d3",
            lightgreen: "#90ee90",
            lightgrey: "#d3d3d3",
            lightpink: "#ffb6c1",
            lightsalmon: "#ffa07a",
            lightseagreen: "#20b2aa",
            lightskyblue: "#87cefa",
            lightslategray: "#778899",
            lightslategrey: "#778899",
            lightsteelblue: "#b0c4de",
            lightyellow: "#ffffe0",
            lime: "#00ff00",
            limegreen: "#32cd32",
            linen: "#faf0e6",
            magenta: "#ff00ff",
            maroon: "#800000",
            mediumaquamarine: "#66cdaa",
            mediumblue: "#0000cd",
            mediumorchid: "#ba55d3",
            mediumpurple: "#9370db",
            mediumseagreen: "#3cb371",
            mediumslateblue: "#7b68ee",
            mediumspringgreen: "#00fa9a",
            mediumturquoise: "#48d1cc",
            mediumvioletred: "#c71585",
            midnightblue: "#191970",
            mintcream: "#f5fffa",
            mistyrose: "#ffe4e1",
            moccasin: "#ffe4b5",
            navajowhite: "#ffdead",
            navy: "#000080",
            oldlace: "#fdf5e6",
            olive: "#808000",
            olivedrab: "#6b8e23",
            orange: "#ffa500",
            orangered: "#ff4500",
            orchid: "#da70d6",
            palegoldenrod: "#eee8aa",
            palegreen: "#98fb98",
            paleturquoise: "#afeeee",
            palevioletred: "#db7093",
            papayawhip: "#ffefd5",
            peachpuff: "#ffdab9",
            peru: "#cd853f",
            pink: "#ffc0cb",
            plum: "#dda0dd",
            powderblue: "#b0e0e6",
            purple: "#800080",
            red: "#ff0000",
            rosybrown: "#bc8f8f",
            royalblue: "#4169e1",
            saddlebrown: "#8b4513",
            salmon: "#fa8072",
            sandybrown: "#f4a460",
            seagreen: "#2e8b57",
            seashell: "#fff5ee",
            sienna: "#a0522d",
            silver: "#c0c0c0",
            skyblue: "#87ceeb",
            slateblue: "#6a5acd",
            slategray: "#708090",
            slategrey: "#708090",
            snow: "#fffafa",
            springgreen: "#00ff7f",
            steelblue: "#4682b4",
            tan: "#d2b48c",
            teal: "#008080",
            thistle: "#d8bfd8",
            tomato: "#ff6347",
            turquoise: "#40e0d0",
            violet: "#ee82ee",
            wheat: "#f5deb3",
            white: "#ffffff",
            whitesmoke: "#f5f5f5",
            yellow: "#ffff00",
            yellowgreen: "#9acd32"
        };

var cbrewer = [ "#7FCDBB", "#2C7FB8", "#ADDD8E", "#31A354", "#C51B8A", "#FA9FB5", "#A6BDDB", "#2B8CBE", "#FDBB84", "#E34A33", "#A8DDB5", "#43A2CA", "#8856A7", "#9EBCDA", "#2CA25F", "#99D8C9" ];

var show = {
  count : 0,
}
$(document).ready(function(){
  $('.date_start').datepicker();
  $('.date_end').datepicker();
  $('.time_start').timepicker();
  $('.time_end').timepicker();
  
  $.getJSON('/metrics/names',function(data){
    $('.search-query').typeahead({
      source: data
    })
    
    $('#input01').typeahead({
      source: data
    })
  })
  
  $("#now_btn").bind('click',function(e){
    e.preventDefault();
    $(".date_end").val("now");
    $(".time_end").val("");
  });
  
  $("#add_btn").bind("click",function(event){
    event.preventDefault();
    // validate
    var metric_name = $("#input01").val();
    if(metric_name.length == 0){
      alert("You need a metric name to draw a graph");
      return ;
    }
    
    var date_start = date_end = moment($(".date_start").val() + " " + $(".time_start").val(), "DD-MM-YYYY hh:mm A");
    
    var date_end = null;
    if($(".date_end").val() == "now" && $(".time_end").val() == ""){
      date_end = moment();
    }else{
      date_end = moment($(".date_end").val() + " " + $(".time_end").val(), "DD-MM-YYYY hh:mm A");      
    }
    
    if(date_start > date_end){
      alert('Start time should be lower than end time');
      return ;
    }
    
    var container = $(".left-column-item");
    if(container.length == 0){
      var future_container = $("<div />").attr("class","left-column-item");
      $(".span4").append(future_container);
      container = $(".left-column-item");
    }
    
    container = container[container.length-1];
    
    var metric_entry = $("#metricTemplate").tmpl({name:metric_name})
    var icon = metric_entry.find(".icon-envelope");
    
    var color_id = parseInt(Math.random()*16);
    var current_color = cbrewer[color_id];
    icon.css("background-color",current_color);
    
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
    var period = $("#select01").val();
    Graph.draw(current_color,metric_name,period);
  });
  
  $("#update").bind("click",function(event){
    event.preventDefault();
  });
  
  $(".span8").bind("mousemove",function(e){
     var parentOffset = $(this).offset();
     //or $(this).offset(); if you really just want the current element's offset
     var relX = e.pageX - parentOffset.left;
     var relY = e.pageY - parentOffset.top;

     // console.log(Math.round(relX));
     $(".line").css("left",e.pageX + "px");
     $(".line").css("height",$("#wrapper").height() + 50 + "px");
     
     var current_data = Graph.data();
     $.each($(".chart_value"),function(index,value){
       var offset = Math.round(relX);
       if(offset < 624){
         $(value).text(current_data[index+1][offset].value);
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
  })
})


/*
Show current number on the left part of the graph.
*/