function drawCharts(color){
  var w = 1, h = 100;
  var t = 1297110663,
      v = 70,
  data = d3.range(625).map(next);

  function next() {
    return {
      time: ++t,
      value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))
    };
  }

  var x = d3.scale.linear().domain([0, 1]).range([0, w]);
  var y = d3.scale.linear().domain([0, 100]).rangeRound([0, h]);

  // chart
  var chart = d3.select("div.span8")
    .append("canvas")
    .attr("id", "chart")
    .attr("width", w * data.length - 1)
    .attr("height", h);

  var ctx = chart[0][0].getContext("2d");
  
  redraw();
  
  setInterval(function() {
    data.shift();
    data.push(next());
    redraw();
    }, 1500);

  // context . fillRect(x, y, w, h)
  
  function redraw(){
    ctx.clearRect(0,0,w * data.length - 1,h);
    ctx.fillStyle = "black";
    ctx.fillRect(0,0,w * data.length - 1,1);
    ctx.fillStyle = color;
    $.each(data,function(index,d){
      ctx.fillRect(index,h - y(d.value),1,y(d.value));
    })
    ctx.fillStyle = "black";
    ctx.fillRect(0,h-1,w * data.length - 1,1);
  }
}