/*
 @param: dataUrl is a URL to a pipe-separated-value file of the form:
   chart|date|executionTime|upstreamLatency|proxyLatency|responseCode
 For example: https://raw.githubusercontent.com/bcgov/dbcrss/master/heartbeat/src/geocoder-public-heartbeat.txt
*/
makeCharts = function(dataUrl) {

  var margin = {
          top: 55,
          right: 10,
          bottom: 40,
          left: 50
      },
      width = 1300 - margin.left - margin.right,
      height = 350 - margin.top - margin.bottom;

  var parseDate = d3.time.format("%H:%M:%S").parse;

  var psv = d3.dsv("|", "text/plain");

  var x = d3.time.scale().range([0, width]);
  var y = d3.scale.linear().range([height, 0]);

  var area = d3.svg.area()
      .x(function(d) {
          return x(d.date);
      })
      .y0(height)
      .y1(function(d) {
          return y(d.executionTime);
      });

  var line = d3.svg.line()
      .x(function(d) {
          return x(d.date);
      })
      .y(function(d) {
          return y(d.executionTime);
      });

  var xAxis = d3.svg.axis().scale(x)
      .orient("bottom").ticks(24);

  var yAxis = d3.svg.axis().scale(y)
      .orient("left").ticks(5)
      .innerTickSize(-width);


  //get the data
  psv(dataUrl, function(error, data) {
      data.forEach(function(d) {
          d.date = parseDate(d.date);
          d.executionTime = +d.executionTime;
      });
      // Scale the range of the data
      x.domain(d3.extent(data, function(d) {
          return d.date;
      }));
      y.domain([0, 100]);

      // Nest data by chart.
      var charts = d3.nest()
          .key(function(d) {
              return d.chart;
          })
          .sortKeys(d3.descending)
          .entries(data);

      // Compute the maximum executionTime per chart, needed for the y-domain.
      charts.forEach(function(s) {
          s.maxexecutionTime = d3.max(s.values, function(d) {
              return d.executionTime;
          });
      });

      // Calculate the minimum and maximum date across charts.
      x.domain([
          d3.min(charts, function(s) {
              return s.values[0].date;
          }),
          d3.max(charts, function(s) {
              return s.values[s.values.length - 1].date;
          })
      ]);

      // Add an svg element for each chart
      var svg = d3.select("body").selectAll("svg")
          .data(charts)
          .enter().append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // Add the area path elements.
      svg.append("path")
          .attr("class", "area")
          .attr("d", function(d) {
              y.domain([0, d.maxexecutionTime]);
              return area(d.values);
          });

      // Add the line path elements.
      svg.append("path")
          .attr("class", "line")
          .attr("d", function(d) {
              y.domain([0, d.maxexecutionTime]);
              return line(d.values);
          });

      svg.append("g")
          .attr("class", "x axis")
          .attr("y", height - 6)
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      // Add the Y Axis
      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis);

      // Add the text label for the x axis
      svg.append("text")
          .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom) + ")")
          .attr("x", -45)
          .style("text-anchor", "middle")
          .text(function(d) {
              return d.key;
          });

      svg.append("text")
          .attr("transform", "rotate(-90)")
          .attr("x", 0 - (height / 2))
          .attr("y", -55)
          .attr("dy", "1em")
          .style("text-anchor", "middle")
          .text("Milliseconds");

  });

} //end function